# 🎵 專屬音樂下載器（全自動免 API 版）

用 Gradio 做的圖形化介面:貼上 Spotify **歌曲／專輯／歌單**連結,就能自動解析曲目並逐首下載為 **320kbps MP3**。**不需要 Spotify API Key、不需要 Premium 帳號。**

> 📖 English version: [README.md](README.md) ・ 📄 更多介紹：[ABOUT.md](ABOUT.md)

---

## 📖 關於本專案（About）

「專屬音樂下載器」是一個 MIT 授權的開源工具，目標是讓「備份自己喜歡的音樂」變得很簡單：貼上連結、按一個按鈕，剩下的交給程式。你不需要 API Key、不需要 Premium 帳號、也不需要寫任何 Code。完整介紹（緣起、運作流程、技術棧）見 [ABOUT.md](ABOUT.md)。

## ✨ 功能特色

- **貼連結自動解析** — 直接貼上 Spotify 連結,自動拆解歌單／專輯內所有歌曲。
- **免 API Key** — 透過 Spotify 公開嵌入頁面解析,不需申請開發者帳號。
- **也支援 CSV** — 可用 [Exportify](https://github.com/exportify/exportify) 匯出的 CSV 當來源。
- **智慧跳過已下載** — 自動比對目標資料夾現有的 `.mp3`,避免重複下載。
- **失敗自動重試** — 一鍵重新下載失敗的歌曲。
- **即時進度更新** — 畫面每秒刷新,顯示目前下載進度與成敗狀態。
- **內嵌封面與資訊** — 自動嵌入縮圖與 ID3 中繼資料。

## 🚀 使用方式

### macOS(最簡單)

1. 下載或 Clone 本專案。
2. 雙擊 `start.command`,它會自動建立虛擬環境、安裝所需套件並開啟網頁介面。

### 手動執行(跨平台)

```bash
# Clone
git clone https://github.com/nashwu0117/MusicDownloader.git
cd MusicDownloader

# 建立虛擬環境
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 安裝依賴
pip install -r requirements.txt

# 啟動
python3 app.py
```

啟動後會自動在瀏覽器打開圖形介面。

## 📋 依賴套件

詳見 [requirements.txt](requirements.txt):

- `gradio` — 網頁介面
- `yt-dlp` — YouTube 下載核心
- `pandas` — 讀取 CSV
- `spotipy` — (備用)Spotify API

## ⚠️ 系統需求

- **Python 3.8 以上**
- **FFmpeg** — 轉檔成 MP3 必須有 FFmpeg。程式預設使用 `~/.spotdl/ffmpeg`。
  - 可透過 [spotDL](https://github.com/spotDL/spotify-downloader) 安裝:`pip install spotdl && spotdl --download-ffmpeg`
  - 或自行安裝 FFmpeg 並修改 `app.py` 中的 `--ffmpeg-location` 路徑。

## 📦 打包成單一執行檔(PyInstaller)

想要一個不用裝 Python 就能直接執行的 `.app` / `.exe` 嗎?用 PyInstaller 打包。

```bash
# 安裝 PyInstaller
pip install pyinstaller

# 打包(單檔、視窗模式,有圖示可自行加上 --icon)
pyinstaller --noconfirm --onefile --windowed \
  --name "MusicDownloader" \
  app.py
```

- 產出在 `dist/MusicDownloader`(macOS 為 `dist/MusicDownloader.app`)。
- **注意:** `yt-dlp` 與 `ffmpeg` 預設不會被打包進去,目標電腦仍需有這兩個工具。若要完全自帶,需用 PyInstaller 的 `--add-data` 把 FFmpeg 二進位一起包進去,詳見 PyInstaller 官方文件。

### ⚠️ FFmpeg 不會被打包 — 目標電腦必須自己裝

PyInstaller 預設**不會**把 `ffmpeg`、`yt-dlp` 包進執行檔。在沒有 FFmpeg 的電腦上,執行檔會**無法轉檔、直接失敗**。解法:

- 請使用者另行安裝 FFmpeg(`brew install ffmpeg` / 到 ffmpeg.org 下載)。
- 或你自己用 PyInstaller 的 `--add-data` 把 FFmpeg 二進位包進去,並修改 `app.py` 讓它執行時找到該路徑(詳見 PyInstaller 官方文件)。
- 程式目前寫死 `--ffmpeg-location ~/.spotdl/ffmpeg`,若使用者電腦的 FFmpeg 在別處,需調整這個路徑。

> ⚠️ PyInstaller 產物是「一個作業系統一份」:在 macOS 上打包只能給 Mac 用,在 Windows 上打包只能給 Windows 用。**macOS 打的檔在 Windows 上跑不起來。**

## 🔒 隱私與憑證

**本專案不含任何寫死的帳號密碼。**重點說明:

- 執行時產生的 `.cache`(Spotify access token)是在**每個使用者自己的電腦上**臨時產生,已透過 `.gitignore` 排除,**不會被上傳到 GitHub**。
- 這是 spotipy 依其[標準快取行為](https://spotipy.readthedocs.io/)寫到 `~/.cache` 的短期 bearer token(通常約 3600 秒過期)。
- **若你不小心把 `.cache` 暴露了**(例如 commit 進 repo、貼到某處),請立刻到 **Spotify → 帳號 → [已連結應用程式](https://www.spotify.com/account/apps/)** 撤銷授權,並刪除本機 `~/.cache`。
- 每個全新使用者 / 全新 clone 都沒有 token,第一次使用時會產生一個新的、綁定在**他自己** Spotify 帳號下的 token。

## 📝 使用須知

本工具以「個人備份自己擁有的音樂」為目的。請遵守各地著作權法與 Spotify、YouTube 的服務條款,勿用於散布或商業用途。**使用者需自負一切法律責任,本儲存庫作者不對任何濫用行為負責。**

## 📂 專案結構

```
MusicDownloader/
├── app.py                 # 主程式(Gradio 介面 + 下載邏輯)
├── start.command          # macOS 一鍵啟動腳本
├── requirements.txt       # Python 依賴
├── .gitignore
├── LICENSE                # MIT 授權
├── ABOUT.md               # 專案介紹
├── README.md              # 英文版
└── README.zh-TW.md        # 繁體中文(本檔)
```

## 📄 授權

MIT License — 見 [LICENSE](LICENSE)。
