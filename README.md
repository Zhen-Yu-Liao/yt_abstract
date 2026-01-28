
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
