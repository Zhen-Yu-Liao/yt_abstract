# import yt_dlp  <-- Removed top-level import
import uuid
import logging
from pathlib import Path
from datetime import datetime
import os
from backend.core.config import settings

logger = logging.getLogger(__name__)

# Lazy import placeholder
yt_dlp = None

class MediaService:
    def __init__(self):
        self.temp_dir = settings.TEMP_DIR

    def download_audio(self, url: str, progress_callback=None) -> tuple[Path, str, float]:
        """
        Downloads audio from YouTube URL.
        Returns: (file_path, title, duration_seconds)
        """
        filename = f"{uuid.uuid4()}"
        timestamp = int(datetime.now().timestamp())
        # Use a simpler template to avoid yt-dlp appending too much stuff
        output_template = str(self.temp_dir / f"{filename}") # yt-dlp adds extension
        
        result_info = {'duration': 0, 'title': 'Unknown'}
        last_update_time = [0]  # Throttle updates
        
        def progress_hook(d):
            import time
            current_time = time.time()
            status = d.get('status', 'unknown')
            print(f"[HOOK] progress_hook called with status: {status}")  # DEBUG
            
            if d['status'] == 'downloading':
                if progress_callback:
                    try:
                        downloaded = d.get('downloaded_bytes', 0)
                        total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                        speed = d.get('speed', 0) or 0
                        
                        # Calculate percent
                        if total > 0:
                            percent = (downloaded / total) * 100
                            percent = min(percent, 99)
                        else:
                            # Even without total, show 0-50% based on downloaded bytes
                            # Assume ~50MB max for audio, cap at 50%
                            percent = min((downloaded / (50 * 1024 * 1024)) * 50, 50)
                        
                        # Throttle: only update every 0.3 seconds or if significant change
                        if current_time - last_update_time[0] >= 0.3:
                            last_update_time[0] = current_time
                            progress_info = {
                                'percent': percent,
                                'downloaded': downloaded,
                                'total': total,
                                'speed': speed
                            }
                            progress_callback(progress_info)
                            print(f"[DOWNLOAD] {percent:.1f}% - {downloaded:,}/{total:,} bytes @ {speed:.0f} B/s")
                    except Exception as e:
                        print(f"[DOWNLOAD PROGRESS ERROR] {e}")
            elif d['status'] == 'finished':
                if progress_callback:
                    # Get final file size
                    downloaded = d.get('downloaded_bytes', 0) or d.get('total_bytes', 0)
                    progress_callback({'percent': 100, 'downloaded': downloaded, 'total': downloaded, 'speed': 0})
                    print(f"[DOWNLOAD] 100% - Finished ({downloaded:,} bytes)")


        import sys
        if getattr(sys, 'frozen', False):
            # Running as compiled EXE
            # In onedir mode with --add-binary source;., the binary is in sys._MEIPASS
            # or sometimes in the dir of executable depending on config.
            # We check typical locations.
            base_path = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
            ffmpeg_path = os.path.join(base_path, "ffmpeg.exe")
            
            # Debugging fallback: check if it's in a subfolder or root
            if not os.path.exists(ffmpeg_path):
                 ffmpeg_path = os.path.join(os.path.dirname(sys.executable), "ffmpeg.exe")
        else:
            # Running in dev mode
            ffmpeg_path = os.path.join(settings.BASE_DIR, "bin", "ffmpeg.exe")
            
        logger.info(f"Using FFmpeg path: {ffmpeg_path}")

        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': output_template + ".%(ext)s",
            'quiet': False,  # Need to be False for progress_hooks to work properly
            'no_warnings': False,  # Allow warnings for debugging
            'noprogress': False,  # Ensure progress is not disabled
            'ffmpeg_location': os.path.dirname(ffmpeg_path) if os.path.exists(ffmpeg_path) else None,
            'progress_hooks': [progress_hook],
            # Anti-bot measures
            # Anti-bot measures: Let yt-dlp handle headers automatically
            # 'http_headers': { ... } removed to avoid stale signatures
            'retries': 3,
            'fragment_retries': 3,
            'extractor_retries': 3,
            'ignoreerrors': False,
            # Note: cookiesfrombrowser removed due to DPAPI errors on Windows
        }

        try:
            global yt_dlp
            if yt_dlp is None:
                logger.info("Lazy loading yt_dlp module...")
                import yt_dlp as _yt_dlp
                yt_dlp = _yt_dlp

            if progress_callback:
                progress_callback({'percent': 0, 'downloaded': 0, 'total': 0, 'speed': 0, 'message': 'Preparing download...'})

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                logger.info(f"Starting download for URL: {url}")
                info = ydl.extract_info(url, download=True)
                title = info.get('title', 'Unknown Title')
                duration = float(info.get('duration', 0))
                
                # The final file is likely mp3 because of postprocessor
                final_path = self.temp_dir / f"{filename}.mp3"
                
                if final_path.exists():
                    return final_path, title, duration
                
                # Fallback: check directory
                raise FileNotFoundError(f"File not found: {final_path}")
            
        except Exception as e:
            logger.error(f"Download failed: {str(e)}")
            raise e

    def cleanup(self, path: Path):
        """Removes the temporary file."""
        try:
            if path.exists():
                path.unlink()
                logger.debug(f"Deleted temp file: {path}")
        except Exception as e:
            logger.warning(f"Failed to delete temp file {path}: {str(e)}")
