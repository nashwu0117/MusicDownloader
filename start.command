#!/bin/bash
cd "$(dirname "$0")"

echo "=========================================="
echo " 🚀 正在為您啟動專屬音樂下載器..."
echo "=========================================="

if [ ! -d "venv" ]; then
    echo "📦 初次執行，正在為您建立獨立運行環境..."
    python3 -m venv venv
fi

source venv/bin/activate

echo "🔄 檢查並更新必要套件中..."
pip install -q --upgrade pip
pip install -q gradio yt-dlp pandas spotipy

echo "=========================================="
echo " ✅ 環境準備就緒！正在打開網頁介面..."
echo "=========================================="

python3 app.py

echo ""
echo "------------------------------------------"
echo "⚠️ 程式已停止執行。請按 Enter 鍵關閉此視窗..."
read
