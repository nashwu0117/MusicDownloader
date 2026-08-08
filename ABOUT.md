# 🎵 關於本專案（About）

## 這是什麼？

**專屬音樂下載器** 是一個 MIT 授權的開源工具，目標是讓「備份自己喜歡的音樂」這件事變得**簡單到不行**。

它提供一個圖形化網頁介面，你只要貼上音樂連結（Spotify、YouTube、YouTube Music、SoundCloud 的歌曲／專輯／歌單皆可），程式就會自動偵測平台、解析曲目，然後把每一首歌下載成 **320kbps MP3**（自動嵌入封面與 ID3 標籤）。

你**不需要** Spotify API Key、不需要 Premium 帳號、也不需要自己寫任何 Code。

## 為什麼要做這個？

- **音樂串流服務會下架歌曲** — 喜歡的歌隨時可能從平台消失，留下一個無法解決的缺憾。
- **官方方案綁手綁腳** — Spotify 的離線下載只能在 App 內聽，換裝置、斷訂閱就沒了。
- **只想簡單點** — 不想要一堆指令列、不想要研究技術文件，貼上連結、按一個按鈕，就應該完成。

## 怎麼運作的？

```
貼上連結 / 上傳 CSV
       │
       ▼
自動偵測平台（Spotify / YouTube / YT Music / SoundCloud）
       │
       ▼
解析曲目清單（歌曲、專輯、歌單全部拆開）
       │
       ▼
逐首下載 → 嵌入封面與 ID3 標籤 → 存成 MP3
       │
       ▼
智慧跳過已下載、失敗自動重試、畫面即時進度
```

## 技術棧

| 元件 | 用途 |
| --- | --- |
| [Gradio](https://gradio.app/) | 網頁圖形介面 |
| [yt-dlp](https://github.com/yt-dlp/yt-dlp) | 下載核心 |
| spotipy | （備用）Spotify API 快取機制 |
| [pandas](https://pandas.pydata.org/) | 讀取 Exportify CSV |
| FFmpeg | 轉檔成 MP3 |

## 功能特色

- **貼連結自動解析** — Spotify / YouTube / YouTube Music / SoundCloud 全支援
- **免 API Key** — 透過 Spotify 公開嵌入頁面解析，不用申請開發者帳號
- **CSV 匯入** — 使用 [Exportify](https://github.com/exportify/exportify) 匯出的歌單 CSV 也可以
- **智慧跳過** — 目標資料夾已存在的 MP3 自動跳過，不會重複下載
- **失敗重試** — 一鍵重新下載失敗的清單
- **完整標籤** — 自動嵌入封面圖、藝人、曲名等 ID3 中繼資料

## 快速開始

macOS 使用者直接雙擊 `start.command` 即可；其他平台請見 [README](README.md) 的手動安裝步驟。

## 專案授權與責任

- **授權**：[MIT](LICENSE)
- **使用須知**：本工具以「個人備份自己擁有的音樂」為目的，請遵守各地著作權法與平台服務條款，勿作為散布或商業用途；使用者需自負法律責任。

## 了解更多

- [英文 ReadMe](README.md)
- [繁體中文 ReadMe](README.zh-TW.md)