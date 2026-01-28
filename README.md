# YT Abstract - 你的極致 YouTube 影片智慧助理

YT Abstract 是一款結合 **本地強大算力 (Local GPU)** 與 **雲端極速 AI (Cloud API)** 的現代化影片摘要工具。它能將冗長的 YouTube 影片轉化為結構清晰的重點筆記、摘要與視覺化心智圖。

![App Screenshot](https://via.placeholder.com/800x450.png?text=YT+Abstract+UI)

## ✨ 核心功能 (Features)

- **🚀 雙模引擎**: 支援 **Groq Cloud API** (秒級轉錄) 與 **NVIDIA Local GPU** (隱私免費)。
- **🧠 智慧摘要**: 整合 **Google Gemini 1.5**，無論影片多長都能精準抓取重點。
- **🗺️ 視覺化心智圖**: 自動生成 Mermaid 互動式圖表，一眼看懂邏輯結構。
- **📦 一鍵匯出**: 支援匯出 Markdown 筆記，無縫整合 Obsidian/Notion。
- **🎨 極致 UI**: 深色玻璃擬態 (Glassmorphism) 設計，提供沉浸式體驗。

---

## 📥 下載與使用指南 (For Users)

如果您是下載執行檔 (Release) 的使用者，請看這裡：

### 1. 下載對應版本

前往 [Releases 頁面](../../releases) 下載適合您系統的壓縮檔：

- **Windows**: `yt_abstract_win.zip`
- **macOS**: `yt_abstract_mac.zip`
- **Linux**: `yt_abstract_linux.tar.gz`

### 2. 解壓縮與執行

#### 🪟 Windows 使用者

1. 解壓縮 `yt_abstract_win.zip`。
2. 進入資料夾，雙擊 `yt_abstract.exe`。
3. 程式會自動啟動並開啟瀏覽器。

#### 🍎 macOS 使用者 (初次必讀！)

由於未購買 Apple 開發者憑證，初次開啟會顯示「應用程式已損毀」。請**只做一次**以下解鎖步驟：

1. 將 `yt_abstract.app` 拖曳到「應用程式 (Applications)」資料夾。
2. 開啟終端機 (Terminal)，貼上並執行：

   ```bash
   xattr -cr /Applications/yt_abstract.app
   ```

3. 現在可以正常點擊 App 開啟了！

#### 🐧 Linux 使用者

1. 解壓縮檔案。
2. 開啟終端機，授權執行指令：

   ```bash
   chmod +x yt_abstract
   ```

3. 執行：`./yt_abstract`

---

## 🛠️ 開發者指南 (For Developers)

如果您想貢獻程式碼或自行建置，請看這裡：

### 環境需求

- Python 3.10+
- Node.js 18+
- FFmpeg (需加入 PATH)

### 快速啟動 (One-click Start)

專案根目錄執行：

```powershell
./start_app.ps1
```

### 手動安裝與執行

1. **安装後端**:

   ```bash
   pip install -r backend/requirements.txt
   uvicorn backend.main:app --reload --port 8000
   ```

2. **安裝前端**:

   ```bash
   cd frontend && npm install
   npm run dev
   ```

### 📦 打包 (Build)

本專案使用 GitHub Actions 進行自動化打包。若要本地打包：

```bash
pip install pyinstaller
python build_exe.py
```

成品將位於 `dist/` 目錄。

---

## 🏗️ 技術架構 (Tech Stack)

- **Frontend**: React (Vite), TypeScript, TailwindCSS, Framer Motion
- **Backend**: FastAPI, Python
- **AI**: OpenAI Whisper (Local), Groq (Cloud), Google Gemini 1.5
- **Tools**: yt-dlp, FFmpeg

---
*Created by Antigravity*
