import PyInstaller.__main__
import os
import shutil
import platform
import subprocess
import stat
from pathlib import Path

# Define paths
BASE_DIR = Path(__file__).resolve().parent
BACKEND_DIR = BASE_DIR / "backend"
DIST_DIR = BASE_DIR / "dist"
BIN_DIR = BACKEND_DIR / "bin"

def get_ffmpeg_paths():
    """
    Returns a list of (source, dest) tuples for FFmpeg binaries.
    """
    system = platform.system()
    binaries = []
    
    if system == "Windows":
        # On Windows, we bundle the .exe files we downloaded
        ffmpeg_exe = BIN_DIR / "ffmpeg.exe"
        ffprobe_exe = BIN_DIR / "ffprobe.exe"
        
        if ffmpeg_exe.exists():
            binaries.append((str(ffmpeg_exe), "."))
        if ffprobe_exe.exists():
            binaries.append((str(ffprobe_exe), "."))
            
    else:
        # On Mac/Linux, we expect ffmpeg to be installed via system package manager (brew/apt)
        ffmpeg_path = shutil.which("ffmpeg")
        ffprobe_path = shutil.which("ffprobe")
        
        if ffmpeg_path:
            print(f">>> Found system FFmpeg at: {ffmpeg_path}")
            binaries.append((ffmpeg_path, "."))
        else:
            print("!!! WARNING: FFmpeg not found in system PATH. App may fail.")
            
        if ffprobe_path:
            binaries.append((ffprobe_path, "."))

    return binaries

def on_rm_error(func, path, exc_info):
    # Error handler for shutil.rmtree to fix Windows file lock/permission issues
    try:
        os.chmod(path, stat.S_IWRITE)
        func(path)
    except Exception as e:
        print(f"!!! Warning: Failed to remove {path}: {e}")

def build():
    print(f">>> Starting Build Process for Platform: {platform.system()}...")
    
    # 1. Clean dist
    if DIST_DIR.exists():
        try:
            shutil.rmtree(DIST_DIR, onerror=on_rm_error)
            print(">>> Cleaned dist directory.")
        except Exception as e:
            print(f"!!! Warning: Could not fully clean dist directory: {e}")
    
    # 2. Prepare Arguments
    sep = os.pathsep # ';' on Windows, ':' on Unix
    
    # Base arguments
    pyinstaller_args = [
        str(BACKEND_DIR / "main.py"),
        '--name=yt_abstract',
        '--onedir', 
        '--windowed', # Required for Mac .app bundle and nice Windows UX
        '--noconfirm',
        
        # Static files
        f'--add-data={BACKEND_DIR / "static"}{sep}static',
        
        # Hidden imports
        '--hidden-import=uvicorn',
        '--hidden-import=fastapi',
        '--hidden-import=engineio.async_drivers.asgi',
        
        # Excludes (Optimization)
        '--exclude-module=torch',
        '--exclude-module=matplotlib',
        '--exclude-module=PIL',
        '--exclude-module=tkinter',
        '--exclude-module=pynvml',       
        '--exclude-module=faster_whisper',
        
        # Metadata
        f'--icon={BASE_DIR / "app_icon.ico"}',
    ]
    
    # 3. Platform Specifics
    # FFmpeg
    ffmpeg_binaries = get_ffmpeg_paths()
    for src, dst in ffmpeg_binaries:
        pyinstaller_args.append(f'--add-binary={src}{sep}{dst}')
        
    # UPX - Disable to avoid issues
    pyinstaller_args.append('--noupx')
    
    # 4. Run PyInstaller
    print(">>> Running PyInstaller with args:", pyinstaller_args)
    PyInstaller.__main__.run(pyinstaller_args)
    
    print("\n>>> PyInstaller Build Complete!")
    
    # 5. Post-Build: Dependency Injection (faster_whisper)
    exe_name = "yt_abstract.app" if platform.system() == "Darwin" else "yt_abstract"
    
    # Location where PyInstaller puts the output
    # For onedir, it's typically dist/yt_abstract (or .app on Mac depending on mode)
    # Note: --onedir on Mac creates a .app bundle but the internal files are deep inside.
    # However, to keep it simple across platforms for installing 'faster_whisper',
    # we target the folder containing the executable logic.
    
    target_dir = DIST_DIR / "yt_abstract" # Default
    
    if platform.system() == "Darwin":
        # On Mac, --onedir creates yt_abstract.app
        # We need to find where to put libraries.
        # Usually dist/yt_abstract.app/Contents/MacOS is where binaries live,
        # but _internal might be elsewhere depending on PyInstaller version.
        # Let's trust PyInstaller's default layout and assume we find _internal inside the bundle?
        # Pro-tip: For Mac, installing into the bundle is tricky via pip target.
        # We might skip manual install on Mac for now and rely on PyInstaller collecting it?
        # BUT we excluded it.
        # Let's try to target the standard path if it exists.
        candidate = DIST_DIR / "yt_abstract.app" / "Contents" / "Resources"
        if candidate.exists():
            target_dir = candidate
        else:
            # Fallback
            target_dir = DIST_DIR / "yt_abstract.app" / "Contents" / "MacOS"
            
    internal_dir = target_dir / "_internal"
    
    # If the _internal dir wasn't created by PyInstaller (e.g. if we messed up paths), we can't install to it.
    # But usually PyInstaller creates it.
    # On Windows/Linux, it is dist/yt_abstract/_internal
    
    # Fallback search
    if not internal_dir.exists():
        # Try generic
        internal_dir = DIST_DIR / "yt_abstract" / "_internal"
        
    if internal_dir.exists() or platform.system() != "Darwin": # Only strictly enforce on Win/Linux where structure is known
        if internal_dir.exists():
            print(f">>> Installing faster_whisper to {internal_dir}...")
            try:
                subprocess.check_call([
                    "pip", "install", 
                    "faster_whisper", 
                    "-t", str(internal_dir), 
                    "--no-deps"
                ])
                print(">>> Installed faster_whisper successfully.")
            except Exception as e:
                print(f"!!! Failed to install faster_whisper: {e}")
    else:
        print(f"!!! Warning: Could not locate _internal directory for manual package installation.")

if __name__ == "__main__":
    build()
