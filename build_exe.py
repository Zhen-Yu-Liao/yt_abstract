import PyInstaller.__main__
import os
import shutil
from pathlib import Path

# Define paths
BASE_DIR = Path(__file__).parent
BACKEND_DIR = BASE_DIR / "backend"
FRONTEND_DIR = BASE_DIR / "frontend"
DIST_DIR = BASE_DIR / "dist"

def build():
    print(">>> Starting Build Process...")
    
    # 1. Clean dist
    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)
        print(">>> Cleaned dist directory.")

    # 2. Check if frontend is built (we assume yes from previous step, or check static)
    static_assets = BACKEND_DIR / "static" / "assets"
    if not static_assets.exists():
        print("!!! API WARNING: Frontend assets not found in backend/static. App might look broken.")
    
    # 3. Run PyInstaller
    # --add-data: source;dest (Windows uses ;)
    # We bundle the static folder into 'static' in the temp dir of exe
    print(">>> Running PyInstaller...")
    
    PyInstaller.__main__.run([
        str(BACKEND_DIR / "main.py"),
        '--name=yt_abstract',
        '--onedir',  # Changed from --onefile to --onedir for speed
        '--noconfirm',
        '--noupx',   # Disable UPX to avoid decompression overhead
        
        # Add static files (Frontend)
        '--add-data', f'{BACKEND_DIR / "static"}{os.pathsep}static',
        
        # Add FFmpeg (Binary)
        '--add-binary', f'{BACKEND_DIR / "bin" / "ffmpeg.exe"}{os.pathsep}.',
        '--add-binary', f'{BACKEND_DIR / "bin" / "ffprobe.exe"}{os.pathsep}.',
        
        # Exclude heavy modules not needed for inference (Manual Copy/Install Strategy)
        '--exclude-module=torch',
        '--exclude-module=matplotlib',
        '--exclude-module=PIL',
        '--exclude-module=tkinter',
        #'--exclude-module=yt_dlp',       # Reverted: Let process naturally
        '--exclude-module=pynvml',       # Manual install
        '--exclude-module=faster_whisper', # Manual install (to avoid analysis hang)
        
        # Hidden imports needed for lazy loading (Only for modules handled by PyInstaller)
        '--hidden-import=uvicorn',
        '--hidden-import=fastapi',
        '--hidden-import=engineio.async_drivers.asgi',

        
        # Removed collect-all to avoid stall
        # '--collect-all=faster_whisper', 
        
        # Metadata
        f'--icon={BASE_DIR / "app_icon.ico"}',
    ])
    
    print("\n>>> Build Complete!")
    print(f">>> Executable is at: {DIST_DIR / 'yt_abstract.exe'}")
    
    # 4. Manual Copy/Install for Speed (Hybrid Packaging)
    INTERNAL_DIR = DIST_DIR / "yt_abstract" / "_internal"
    
    # 4.1 Copy yt_dlp (Reverted: PyInstaller handles this)
    # try:
    #     print(">>> Manually copying yt_dlp to _internal...")
    #     import yt_dlp
    #     yt_dlp_src = Path(yt_dlp.__file__).parent
    #     
    #     dest_dir = INTERNAL_DIR / "yt_dlp"
    #     if dest_dir.exists():
    #         shutil.rmtree(dest_dir)
    #     shutil.copytree(yt_dlp_src, dest_dir)
    #     print(f">>> Copied yt_dlp to {dest_dir}")
    #     
    # except Exception as e:
    #     print(f"!!! Failed to copy yt_dlp: {e}")

    # 4.2 Install faster_whisper (and dependencies if needed, but we try no-deps first if env has them)
    # Actually, faster_whisper has binary dependencies (CTranslate2). 
    # Installing via pip to target dir is safest.
    try:
        print(">>> Installing faster_whisper to _internal...")
        import subprocess
        subprocess.check_call([
            "pip", "install", 
            "faster_whisper", 
            "-t", str(INTERNAL_DIR), 
            "--no-deps" # Assume dependencies (av, numpy) are handled by PyInstaller or existing env
        ])
        print(">>> Installed faster_whisper")
    except Exception as e:
        print(f"!!! Failed to install faster_whisper: {e}")

if __name__ == "__main__":
    build()
