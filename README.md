# YT Abstract

Design-driven video summarization tool using Local GPU (Whisper) and Cloud AI (Gemini).

## Features

- **Hybrid AI**: Run transcription locally on your RTX 4060 (Free & Private) or via Cloud API.
- **Smart Summarization**: Uses Google Gemini 1.5 Flash for long-context video understanding.
- **Markdown Export**: Download clean, structured notes.
- **Modern UI**: Dark mode interface designed with Pencil.dev.

## Prerequisites

1. **Python 3.10+**
2. **Node.js 18+**
3. **FFmpeg** (Required for audio extraction)
   - Ensure `ffmpeg` is in your System PATH.
4. **NVIDIA Driver + CUDA** (For Local GPU mode)

## Installation

1. Install Dependencies:

   ```powershell
   # Backend
   pip install -r backend/requirements.txt
   
   # Frontend
   cd frontend
   npm install
   ```

2. Configuration (Optional):
   - Copy `.env.example` to `.env` if you want to set default API keys.

## Running the App

Simply run the startup script:

```powershell
./start_app.ps1
```

Or manually:

- Backend: `uvicorn backend.main:app --reload`
- Frontend: `npm run dev` (in frontend dir)
