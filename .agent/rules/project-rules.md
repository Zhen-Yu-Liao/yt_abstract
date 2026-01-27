# Project Rules (專案規則)

本文件由 `rule-generator` 自動生成，定義了 **YT Abstract** 專案的開發規範與最佳實踐。

## 1. 技術堆疊 (Tech Stack)

### Frontend

- **Framework**: React (Vite)
- **Language**: TypeScript
- **Styling**: TailwindCSS
- **State Management**: React Hooks (useState, useEffect)
- **Icons**: Lucide React
- **Visualization**: Mermaid.js

### Backend

- **Framework**: FastAPI
- **Language**: Python 3.10+
- **AI Models**: Faster-Whisper (Local), Groq (Cloud), Google Gemini (Summary)
- **Utilities**: yt-dlp (Download), FFmpeg (Media Processing)

## 2. 核心原則 (Core Principles)

1. **用戶體驗優先 (UX First)**:
    - 所有的長時間操作（下載、轉錄）必須有明確的進度條 (Progress Bar) 與狀態提示。
    - 錯誤訊息必須友善且具體。
2. **型別安全 (Type Safety)**:
    - 前端嚴格使用 TypeScript，避免 `any`。
    - 後端使用 Pydantic Models 進行資料驗證。
3. **隱私保護 (Privacy)**:
    - Local GPU 模式下，確保數據不離開本機。
    - API Keys 必須存放在 `.env`，嚴禁 Hardcode。

## 3. 目錄結構規範 (Directory Structure)

```
yt_abstract/
├── backend/                # Python FastAPI Backend
│   ├── api/                # API Routers
│   ├── core/               # App Configuration & Settings
│   ├── services/           # Business Logic (Media, Transcription, Summary)
│   └── main.py             # App Entry Point
├── frontend/               # React Vite Frontend
│   ├── public/             # Static Assets
│   ├── src/
│   │   ├── components/     # UI Components (atoms/molecules)
│   │   ├── lib/            # Utilities & API Clients
│   │   └── App.tsx         # Main Application Layout
│   └── index.html
├── docs/                   # Project Documentation
│   └── codemaps/           # Architecture Diagrams
└── .agent/rules/           # Antigravity Rules
```

## 4. 程式碼風格 (Coding Style)

### Naming Conventions

- **Files**:
  - Python: `snake_case.py` (e.g., `media_service.py`)
  - TypeScript: `PascalCase.tsx` (Components), `camelCase.ts` (Utils)
- **Variables**:
  - Python: `snake_case`
  - TypeScript: `camelCase` (Constants `UPPER_SNAKE_CASE`)

### Best Practices

- **React**: 使用 Functional Components 與 Hooks。避免 Class Components。
- **FastAPI**: 使用 Dependency Injection (`Depends`)。
- **Async**: 所有 I/O 操作（下載、AI 推理）必須是非阻塞 (Async/Await)。

## 5. 版本控制 (Git Workflow)

- **Commit Message**: 使用 Conventional Commits (e.g., `feat: add mind map support`, `fix: progress bar 0B issue`).
- **Ignore**: 確保 `.env`, `__pycache__`, `node_modules`, `downloads/` 被列入 `.gitignore`。

---
*Last Updated: 2026-01-27*
