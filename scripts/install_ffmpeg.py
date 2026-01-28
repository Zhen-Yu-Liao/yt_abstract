import os
import zipfile
import urllib.request
import shutil
from pathlib import Path

FFMPEG_URL = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
DOWNLOAD_DIR = Path("downloads")
BIN_DIR = Path("backend/bin")

def install_ffmpeg():
    print(">>> Starting FFmpeg installation...")
    
    # 1. Create directories
    DOWNLOAD_DIR.mkdir(exist_ok=True)
    BIN_DIR.mkdir(parents=True, exist_ok=True)
    
    zip_path = DOWNLOAD_DIR / "ffmpeg.zip"
    
    # 2. Download
    if not zip_path.exists():
        print(f">>> Downloading FFmpeg from {FFMPEG_URL}...")
        try:
            urllib.request.urlretrieve(FFMPEG_URL, zip_path)
            print(">>> Download complete.")
        except Exception as e:
            print(f"!!! Download failed: {e}")
            return

    # 3. Extract
    print(">>> Extracting FFmpeg...")
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Find the bin folder inside the zip
            for file in zip_ref.namelist():
                if file.endswith('ffmpeg.exe') or file.endswith('ffprobe.exe'):
                    filename = os.path.basename(file)
                    source = zip_ref.open(file)
                    target = open(BIN_DIR / filename, "wb")
                    with source, target:
                        shutil.copyfileobj(source, target)
                    print(f"   -> Extracted {filename}")
        
        print(f">>> FFmpeg installed to: {BIN_DIR.absolute()}")
        
    except Exception as e:
        print(f"!!! Extraction failed: {e}")

if __name__ == "__main__":
    install_ffmpeg()
