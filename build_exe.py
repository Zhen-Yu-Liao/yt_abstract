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
        # '--exclude-module=PIL', # Needed for icon conversion on Mac?
        '--exclude-module=tkinter',
        '--exclude-module=pynvml',       
        '--exclude-module=faster_whisper',
        
        # Metadata
        # f'--icon={BASE_DIR / "app_icon.ico"}', # Moving to conditional
    ]
    
    # 3. Platform Specifics
    # Icon (Windows only for now to avoid Mac conversion issues)
    if platform.system() == "Windows":
        pyinstaller_args.append(f'--icon={BASE_DIR / "app_icon.ico"}')

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
    
    # DEBUG: Print dist structure
    print(">>> Debugging: Listing dist directory structure:")
    for root, dirs, files in os.walk(DIST_DIR):
        level = root.replace(str(DIST_DIR), '').count(os.sep)
        indent = ' ' * 4 * (level)
        print(f"{indent}{os.path.basename(root)}/")
        subindent = ' ' * 4 * (level + 1)
        # Limit file listing to avoid spam
        for f in files[:5]:
            print(f"{subindent}{f}")
        if len(files) > 5:
            print(f"{subindent}... ({len(files)-5} more)")

    # 5. Post-Build: Dependency Injection (faster_whisper)
    exe_name = "yt_abstract.app" if platform.system() == "Darwin" else "yt_abstract"
    target_dir = DIST_DIR / "yt_abstract" # Default
    
    if platform.system() == "Darwin":
        # Search for where _internal might be hidden
        # Typically: dist/yt_abstract.app/Contents/Frameworks/_internal or just _internal
        # Let's search recursively for '_internal' inside dist/yt_abstract.app
        app_root = DIST_DIR / "yt_abstract.app"
        found_internal = None
        if app_root.exists():
            for root, dirs, files in os.walk(app_root):
                if "_internal" in dirs:
                    found_internal = Path(root) / "_internal"
                    break
        
        if found_internal:
            internal_dir = found_internal
        else:
            # Fallback (maybe it is not called _internal on Mac or different PyInstaller setting)
            # We will default to Contents/Resources just in case we need to create it?
            # No, if PyInstaller didn't make it, we probably shouldn't mess with it.
            internal_dir = app_root / "Contents" / "Resources" / "_internal" # Guess
    else:
        internal_dir = DIST_DIR / "yt_abstract" / "_internal"

    print(f">>> Target _internal directory: {internal_dir}")

    # Install faster_whisper (Non-Fatal)
    try:
        if internal_dir.exists() or platform.system() != "Darwin":
            print(f">>> Installing faster_whisper to {internal_dir}...")
            subprocess.check_call([
                "pip", "install", 
                "faster_whisper", 
                "-t", str(internal_dir), 
                "--no-deps"
            ])
            print(">>> Installed faster_whisper successfully.")
        else:
             print(f"!!! Warning: Could not locate _internal directory (_internal) inside app bundle. Skipping optimization.")
             
    except Exception as e:
        print(f"!!! Warning: Failed to install faster_whisper: {e}")
        print("!!! Continuing build process without manual optimization.")
        # Do not raise, allow build to succeed
    
    # Final Success Message
    print(">>> Build Script Finished Successfully.")

if __name__ == "__main__":
    build()
