import gradio as gr
import pandas as pd
import os
import re
import json
import subprocess
import sys
import time
import threading
import queue
import urllib.request

state = {
    "history": "尚未開始。",
    "status": "等待中...",
    "failed": "✨ 目前沒有下載失敗的歌曲！",
    "is_running": False,
}
state_lock = threading.Lock()
global_failed_songs = []

def format_failed_list():
    if not global_failed_songs:
        return "✨ 目前沒有下載失敗的歌曲！"
    return "\n".join([f"• {song}" for song in global_failed_songs])

def update_state(history=None, status=None, failed=None):
    with state_lock:
        if history is not None:
            state["history"] = history
        if status is not None:
            state["status"] = status
        if failed is not None:
            state["failed"] = failed

def parse_spotify_url_no_api(spotify_url):
    """不用 API Key / Premium，直接解析 Spotify 網頁內嵌資料取得歌單內容"""
    match = re.search(r'spotify\.com/(track|album|playlist)/([a-zA-Z0-9]+)', spotify_url)
    if not match:
        raise ValueError("無法識別此 Spotify 連結，請確認格式是否正確。")

    kind, spotify_id = match.group(1), match.group(2)
    embed_url = f"https://open.spotify.com/embed/{kind}/{spotify_id}"

    req = urllib.request.Request(
        embed_url,
        headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode('utf-8')
    except Exception as e:
        raise ValueError(f"無法讀取 Spotify 網頁: {e}")

    json_match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html)
    if not json_match:
        raise ValueError("無法解析 Spotify 網頁結構，請嘗試改用 CSV 方式。")

    try:
        data = json.loads(json_match.group(1))
        page_props = data.get('props', {}).get('pageProps', {})
        entity = page_props.get('state', {}).get('data', {}).get('entity') or page_props.get('entity', {})
    except Exception as e:
        raise ValueError(f"解析 Spotify 曲目失敗: {e}")

    songs = []
    if kind == 'track':
        title = entity.get('name') or entity.get('title')
        artists = entity.get('subtitle') or ", ".join([a.get('name', '') for a in entity.get('artists', []) if isinstance(a, dict)])
        if title:
            songs.append({"track": title, "artist": artists})
    else:
        track_list = entity.get('trackList') or []
        if not track_list and 'tracks' in entity:
            track_list = entity['tracks'].get('items', [])

        for t in track_list:
            if not isinstance(t, dict):
                continue
            title = t.get('title') or t.get('name')
            if not title and isinstance(t.get('track'), dict):
                title = t['track'].get('name')

            subtitle = t.get('subtitle') or ""
            if not subtitle and 'artists' in t and isinstance(t['artists'], list):
                subtitle = ", ".join([a.get('name', '') for a in t['artists'] if isinstance(a, dict)])
            elif not subtitle and isinstance(t.get('track'), dict) and 'artists' in t['track']:
                subtitle = ", ".join([a.get('name', '') for a in t['track']['artists'] if isinstance(a, dict)])

            if title:
                songs.append({"track": title, "artist": subtitle})

    if not songs:
        raise ValueError("該 Spotify 連結中未找到任何曲目。")

    return songs

def run_yt_dlp(cmd, timeout=180):
    output_queue = queue.Queue()

    def reader(proc, q):
        try:
            for line in iter(proc.stdout.readline, ''):
                if line:
                    q.put(line.strip())
        except Exception:
            pass
        finally:
            q.put(None)

    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )
    t = threading.Thread(target=reader, args=(process, output_queue), daemon=True)
    t.start()

    start_time = time.time()
    output_finished = False

    while True:
        if time.time() - start_time > timeout:
            process.kill()
            yield "⏱️ 逾時", True
            return

        try:
            line = output_queue.get(timeout=0.1)
            if line is None:
                output_finished = True
            elif line:
                yield line, False
        except queue.Empty:
            pass

        retcode = process.poll()
        if retcode is not None and output_finished:
            yield ("__DONE_OK__" if retcode == 0 else "__DONE_FAIL__"), True
            return

        time.sleep(0.05)

def download_worker(csv_path, spotify_url, output_path):
    global global_failed_songs
    global_failed_songs = []

    raw_path = str(output_path).strip()
    if raw_path.startswith("~/Users/"):
        raw_path = raw_path.replace("~", "", 1)
    elif not raw_path:
        raw_path = "~/Downloads/Spotify音樂"

    output_dir = os.path.expanduser(raw_path)
    os.makedirs(output_dir, exist_ok=True)

    url_input = str(spotify_url).strip() if spotify_url else ""

    songs = []
    source_label = ""

    if url_input:
        update_state(history="🔍 正在自動解析 Spotify 連結曲目中...", status="解析網址中...", failed=format_failed_list())
        try:
            songs = parse_spotify_url_no_api(url_input)
            source_label = "Spotify 連結 (免 API 自動解析)"
        except Exception as e:
            update_state(history=f"❌ 解析失敗: {e}", status="錯誤", failed=format_failed_list())
            state["is_running"] = False
            return
    elif csv_path:
        try:
            df = pd.read_csv(csv_path)
            for _, row in df.iterrows():
                track = row.get('Track Name') or row.get('Name') or row.get('track_name')
                artist = row.get('Artist Name(s)') or row.get('Artist Name') or row.get('artist_name')
                if track and artist:
                    songs.append({"track": track, "artist": artist})
            source_label = "CSV 檔案"
        except Exception as e:
            update_state(history=f"❌ 讀取 CSV 失敗: {e}", status="錯誤", failed=format_failed_list())
            state["is_running"] = False
            return

    if not songs:
        update_state(history="❌ 找不到任何曲目資訊，請確認連結或 CSV 內容", status="錯誤", failed=format_failed_list())
        state["is_running"] = False
        return

    existing_files = os.listdir(output_dir) if os.path.exists(output_dir) else []
    existing_mp3s = [f.lower() for f in existing_files if f.lower().endswith('.mp3')]

    history_log = f"📂 儲存資料夾：{output_dir}\n"
    history_log += f"🔗 來源：{source_label}\n"
    history_log += f"📜 總共找到 {len(songs)} 首歌曲\n"
    history_log += f"🔍 現有完整 MP3 檔案：{len(existing_mp3s)} 個（已自動忽略圖片與暫存檔）\n=============================\n"
    update_state(history=history_log, status="準備開始檢查與下載...", failed=format_failed_list())

    for index, song in enumerate(songs):
        track = song["track"]
        artist = song["artist"]
        current_song = f"{artist} - {track}" if artist else str(track)

        track_lower = str(track).lower()
        is_exist = any(track_lower in mp3_f and len(track_lower) > 2 for mp3_f in existing_mp3s)

        if is_exist:
            history_log += f"⏭️ 已存在 MP3，略過: {current_song}\n"
            update_state(history=history_log, status=f"略過已存在: {current_song}", failed=format_failed_list())
            continue

        history_log += f"\n⏳ 正在下載 ({index + 1}/{len(songs)}): {current_song}\n"
        update_state(history=history_log, status=f"正在下載: {current_song}", failed=format_failed_list())

        cmd = [
            sys.executable, "-m", "yt_dlp",
            "--no-warnings",
            "--embed-thumbnail",
            "--embed-metadata",
            "-f", "bestaudio/best",
            "-x", "--audio-format", "mp3", "--audio-quality", "320",
            "--ffmpeg-location", os.path.expanduser("~/.spotdl/ffmpeg"),
            "-o", os.path.join(output_dir, "%(title)s.%(ext)s"),
            f"ytsearch1:{current_song}"
        ]

        success = False
        try:
            for line, is_final in run_yt_dlp(cmd, timeout=180):
                if is_final:
                    if line == "__DONE_OK__":
                        success = True
                    break
                else:
                    update_state(status=f"下載中: {current_song} | {line[:50]}")
        except Exception as e:
            history_log += f"❌ 發生錯誤: {current_song} ({type(e).__name__}: {e})\n"

        if success:
            history_log += f"✅ 成功下載: {current_song}\n"
        else:
            history_log += f"❌ 下載失敗: {current_song}\n"
            if current_song not in global_failed_songs:
                global_failed_songs.append(current_song)

        update_state(history=history_log, status=f"完成: {current_song}", failed=format_failed_list())

    history_log += "\n🎉 全部執行完畢！"
    update_state(history=history_log, status="任務結束！", failed=format_failed_list())
    state["is_running"] = False

def retry_worker(output_path):
    global global_failed_songs
    if not global_failed_songs:
        update_state(history="✨ 目前沒有失敗的項目需要重試。", status="無失敗項目", failed=format_failed_list())
        state["is_running"] = False
        return

    raw_path = str(output_path).strip()
    output_dir = os.path.expanduser(raw_path.replace("~", "", 1) if raw_path.startswith("~/Users/") else (raw_path or "~/Downloads/Spotify音樂"))
    os.makedirs(output_dir, exist_ok=True)

    history_log = f"🔄 開始重新下載失敗歌曲（共 {len(global_failed_songs)} 首）...\n=============================\n"
    update_state(history=history_log, status="準備重試...", failed=format_failed_list())

    still_failed = []
    songs_to_retry = list(global_failed_songs)

    for index, current_song in enumerate(songs_to_retry):
        history_log += f"\n⏳ 重新下載 ({index + 1}/{len(songs_to_retry)}): {current_song}\n"
        update_state(history=history_log, status=f"重試中: {current_song}", failed=format_failed_list())

        cmd = [
            sys.executable, "-m", "yt_dlp",
            "--no-warnings",
            "--embed-thumbnail",
            "--embed-metadata",
            "-f", "bestaudio/best",
            "-x", "--audio-format", "mp3", "--audio-quality", "320",
            "--ffmpeg-location", os.path.expanduser("~/.spotdl/ffmpeg"),
            "-o", os.path.join(output_dir, "%(title)s.%(ext)s"),
            f"ytsearch1:{current_song}"
        ]

        success = False
        try:
            for line, is_final in run_yt_dlp(cmd, timeout=180):
                if is_final:
                    if line == "__DONE_OK__":
                        success = True
                    break
                else:
                    update_state(status=f"重試中: {line[:50]}")
        except Exception:
            history_log += f"❌ 錯誤: {current_song}\n"

        if success:
            history_log += f"✅ 補抓成功: {current_song}\n"
        else:
            history_log += f"❌ 依然失敗: {current_song}\n"
            still_failed.append(current_song)

        global_failed_songs = still_failed
        update_state(history=history_log, status=f"重試完畢: {current_song}", failed=format_failed_list())

    history_log += "\n🎉 失敗歌曲重試完畢！"
    update_state(history=history_log, status="重試結束！", failed=format_failed_list())
    state["is_running"] = False

def start_download(csv_file, spotify_url, output_path):
    if state["is_running"]:
        return state["history"], "⚠️ 已經有任務在執行中，請稍候", state["failed"]

    if not spotify_url and csv_file is None:
        return "❌ 請貼上 Spotify 連結，或上傳 CSV 檔案", "請提供歌曲來源", "無"

    state["is_running"] = True
    update_state(history="🚀 任務已啟動，正在解析內容...", status="啟動中...", failed=format_failed_list())

    csv_path = csv_file.name if csv_file is not None else None
    t = threading.Thread(
        target=download_worker,
        args=(csv_path, spotify_url, output_path),
        daemon=True
    )
    t.start()

    return state["history"], state["status"], state["failed"]

def start_retry(output_path):
    if state["is_running"]:
        return state["history"], "⚠️ 已經有任務在執行中，請稍候", state["failed"]

    state["is_running"] = True
    update_state(status="啟動重試中...")

    t = threading.Thread(target=retry_worker, args=(output_path,), daemon=True)
    t.start()

    return state["history"], state["status"], state["failed"]

def poll_state():
    with state_lock:
        return state["history"], state["status"], state["failed"]

with gr.Blocks(title="🎵 專屬音樂下載器") as app:
    gr.Markdown("## 🎵 專屬音樂下載器 (全自動免 API 版)\n* **貼連結自動解析**：直接貼上 Spotify 歌曲 / 專輯 / 歌單連結，自動拆解歌曲並逐首下載。\n* **智慧跳過已下載檔**：自動比對目標資料夾的 `.mp3` 檔案，避免重複下載。\n* **即時進度更新**：每秒刷新畫面，清晰顯示目前下載進度與成敗。")

    with gr.Row():
        with gr.Column(scale=1):
            spotify_url_input = gr.Textbox(
                label="1️⃣ 貼上 Spotify 連結（歌曲 / 專輯 / 歌單皆可）",
                placeholder="例如：https://open.spotify.com/album/2k4FmEtXR0WiDW0Ac2QArT"
            )
            gr.Markdown("— 或者 —")
            csv_input = gr.File(label="上傳從 Exportify 匯出的 CSV 檔案")
            path_input = gr.Textbox(
                label="2️⃣ 自訂儲存路徑",
                value="~/Downloads/Spotify音樂"
            )
            run_btn = gr.Button("🚀 開始下載", variant="primary")
            retry_btn = gr.Button("🔄 重新下載失敗項目", variant="secondary")
        with gr.Column(scale=1):
            history_out = gr.Textbox(label="📋 整體進度 (歷史紀錄)", lines=15, value="尚未開始。")
            term_out = gr.Textbox(label="💻 目前執行狀態 (每秒自動更新)", lines=2, value="等待中...")
            failed_out = gr.Textbox(label="⚠️ 下載失敗清單", lines=5, value="✨ 目前沒有下載失敗的歌曲！")

    run_btn.click(
        fn=start_download,
        inputs=[csv_input, spotify_url_input, path_input],
        outputs=[history_out, term_out, failed_out]
    )
    retry_btn.click(fn=start_retry, inputs=[path_input], outputs=[history_out, term_out, failed_out])

    timer = gr.Timer(1)
    timer.tick(fn=poll_state, outputs=[history_out, term_out, failed_out])

app.queue().launch(inbrowser=True)
