from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.core.config import settings
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS Configuration
# Allow frontend (Vite default: 5173) and local development
origins = [
    "http://localhost",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from backend.api.api_router import router as api_router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Mount static files - Handle PyInstaller bundled mode
import sys
if getattr(sys, 'frozen', False):
    # Running as compiled exe
    base_path = sys._MEIPASS
else:
    # Running in development
    base_path = os.path.dirname(__file__)

static_dir = os.path.join(base_path, "static")

# Mount assets directory
if os.path.exists(static_dir):
    assets_dir = os.path.join(static_dir, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

# Serve root-level static files (app_icon.png, etc.)
@app.get("/app_icon.png")
async def serve_app_icon():
    icon_path = os.path.join(static_dir, "app_icon.png")
    if os.path.exists(icon_path):
        return FileResponse(icon_path)
    from fastapi import HTTPException
    raise HTTPException(status_code=404, detail="Icon not found")

# Catch-all route for SPA (must be last)
@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    # If path starts with api, let it 404 naturally if not matched above
    if full_path.startswith("api"):
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="API endpoint not found")
    
    # Serve index.html for any other route (React Router handles the rest)
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Frontend not built. Please run 'npm run build' in frontend directory."}


if __name__ == "__main__":
    import uvicorn
    import webbrowser
    import threading
    import time
    
    def open_browser():
        # Wait for server to start
        time.sleep(2)
        webbrowser.open("http://localhost:8000")
    
    # Open browser in background thread
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Reload=False for production/exe
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)


