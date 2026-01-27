import yt_dlp
import uuid
import logging
from pathlib import Path
from datetime import datetime
import os
from backend.core.config import settings

logger = logging.getLogger(__name__)

class MediaService:
    def __init__(self):
        self.temp_dir = settings.TEMP_DIR

    async def download_audio(self, url: str, progress_callback=None) -> tuple[Path, str, float]:
        """
        Downloads audio from YouTube URL.
        Returns: (file_path, title, duration_seconds)
        """
        filename = f"{uuid.uuid4()}"
        timestamp = int(datetime.now().timestamp())
        # Use a simpler template to avoid yt-dlp appending too much stuff
        output_template = str(self.temp_dir / f"{filename}") # yt-dlp adds extension
        
        result_info = {'duration': 0, 'title': 'Unknown'}

        def progress_hook(d):
            if d['status'] == 'downloading':
                if progress_callback:
                    try:
                        p_str = d.get('_percent_str', '0%').replace('%','')
                        # ANSI codes might be present, strip them if needed, but usually _percent_str is cleanish
                        # simple float conversion
                        progress_callback(float(p_str))
                    except:
                        pass
            elif d['status'] == 'finished':
                pass

        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': output_template + ".%(ext)s",
            'quiet': True,
            'no_warnings': True,
            'progress_hooks': [progress_hook]
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                logger.info(f"Starting download for URL: {url}")
                # extract_info with download=False first to get metadata? 
                # No, download=True allows hooks to run.
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
