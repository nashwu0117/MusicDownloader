# 🎵 Spotify Music Downloader (No-API Edition)

A Gradio-based graphical interface: paste a Spotify **track / album / playlist** link and it automatically resolves the tracks and downloads each one as a **320 kbps MP3**. **No Spotify API key required. No Premium account required.**

> 📖 中文版說明請見 [README.zh-TW.md](README.zh-TW.md)

---

## ✨ Features

- **Paste-and-resolve** — Drop in a Spotify link; tracks are parsed automatically via Spotify's public embed page.
- **No API key** — Uses Spotify's public embed page, no developer account needed.
- **CSV supported** — Can also import a CSV exported from [Exportify](https://github.com/exportify/exportify).
- **Skip existing** — Compares against existing `.mp3` files in the target folder to avoid duplicates.
- **Retry failures** — One click re-downloads the songs that failed.
- **Live progress** — UI refreshes every second to show current download status.
- **Embeds cover & metadata** — Automatically embeds thumbnails and ID3 tags.

## 🚀 Quick Start

### macOS (easiest)

1. Download or clone this project.
2. Double-click `start.command`. It creates a virtualenv, installs the required packages, and opens the web UI.

### Manual (cross-platform)

```bash
# Clone
git clone https://github.com/nashwu0117/MusicDownloader.git
cd MusicDownloader

# Create virtual environment
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Launch
python3 app.py
```

The app launches automatically opens in your default browser.

## 📋 Dependencies

See [requirements.txt](requirements.txt):

- `gradio` — web UI
- `yt-dlp` — download core
- `pandas` — CSV parsing
- `spotipy` — (optional) Spotify API fallback

## ⚠️ Requirements

- **Python 3.8+**
- **FFmpeg** — Required to convert to MP3. The app defaults to `~/.spotdl/ffmpeg`.
  - Install via [spotDL](https://github.com/spotDL/spotify-downloader): `pip install spotdl && spotdl --download-ffmpeg`
  - Or install FFmpeg yourself and edit `--ffmpeg-location` in `app.py`.

## 📦 Build a Standalone Executable (PyInstaller)

Want a single `.app` / `.exe` you can distribute without requiring Python? Use PyInstaller.

```bash
# Install PyInstaller
pip install pyinstaller

# Build (one-file, with app icon if you have one)
pyinstaller --noconfirm --onefile --windowed \
  --name "MusicDownloader" \
  app.py
```

- Output appears in `dist/MusicDownloader` (or `dist/MusicDownloader.app` on macOS).
- **Note:** `yt-dlp` and `ffmpeg` are *not* bundled by default and must still be available on the target machine. For a fully self-contained build you'd need to bundle the FFmpeg binary as a resource — see the PyInstaller docs on `--add-data`.

> ⚠️ PyInstaller builds are per-OS. Build on macOS for Mac users, on Windows for Windows users.

## 🔒 Privacy Note

This project contains no hardcoded credentials. The `.cache` file (Spotify token) is generated at runtime and is **excluded by `.gitignore`** — it never gets uploaded. Each user starts fresh.

## 📝 Disclaimer

This tool is intended for backing up music you personally own. Please follow local copyright law and the Spotify / YouTube Terms of Service. Do not use it for distribution or commercial purposes. Users are responsible for their own legal compliance.

## 📂 Project Structure

```
MusicDownloader/
├── app.py                 # Main app (Gradio UI + download logic)
├── start.command          # macOS one-click launcher
├── requirements.txt       # Python dependencies
├── .gitignore
├── LICENSE                # MIT
├── README.md              # English (this file)
└── README.zh-TW.md        # 繁體中文
```

## 📄 License

MIT License — see [LICENSE](LICENSE).
