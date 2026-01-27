import logging
import os
from abc import ABC, abstractmethod
from pathlib import Path
from faster_whisper import WhisperModel
import openai
from backend.core.config import settings
from typing import Generator, Union

logger = logging.getLogger(__name__)

def _format_timestamp(seconds: float) -> str:
    """Convert seconds to MM:SS format."""
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}:{secs:02d}"

def _format_segment(start: float, end: float, text: str) -> str:
    """Format a segment with timestamp range."""
    return f"[{_format_timestamp(start)} - {_format_timestamp(end)}] {text.strip()}"

class TranscriptionStrategy(ABC):
    @abstractmethod
    def transcribe(self, audio_path: Path, duration: float, api_key: str = None) -> Generator[tuple[str, float], None, str]:
        """
        Yields (status_message, progress_percent)
        Returns full_text at the end (handled via StopIteration value or final yield payload mechanism, 
        but simpler to just yield progress and return text or yield a final 'complete' event).
        
        To make it compatible with streaming, we will yield progress events, 
        and the LAST yielded item will be the full text wrapped in a specific way or we manage state in caller.
        
        Actually, let's make it yield progress 0.0-1.0. 
        And return the text? Generators in Python return value via StopIteration but that's hard to catch in simple iteration.
        
        Better approach: Yield progress floats. 
        The caller will accumulate text? No, Whisper streams segments.
        
        Let's yield: {"type": "progress", "value": 0.5} AND {"type": "segment", "text": "..."}
        Or simply yield progress updates, and at the end yield the full text?
        """
        pass

class LocalFasterWhisperStrategy(TranscriptionStrategy):
    _model = None

    def __init__(self):
        if LocalFasterWhisperStrategy._model is None:
            logger.info(f"Loading Faster-Whisper model: {settings.DEFAULT_WHISPER_MODEL} ...")
            try:
                LocalFasterWhisperStrategy._model = WhisperModel(
                    settings.DEFAULT_WHISPER_MODEL, 
                    device="cuda", 
                    compute_type="int8"
                )
                logger.info("Faster-Whisper model loaded via CUDA.")
            except Exception as e:
                logger.warning(f"Could not load CUDA, falling back to CPU: {e}")
                LocalFasterWhisperStrategy._model = WhisperModel(
                    settings.DEFAULT_WHISPER_MODEL, 
                    device="cpu", 
                    compute_type="int8"
                )

    def transcribe(self, audio_path: Path, duration: float, api_key: str = None):
        logger.info(f"Transcribing {audio_path} using Local Model...")
        segments, info = self._model.transcribe(
            str(audio_path), 
            beam_size=5,
            vad_filter=True
        )
        
        formatted_segments = []
        for segment in segments:
            # Format with timestamp
            formatted_line = _format_segment(segment.start, segment.end, segment.text)
            formatted_segments.append(formatted_line)
            # Calculate progress
            if duration > 0:
                progress = min(segment.end / duration, 0.99)
                yield {"type": "progress", "value": progress * 100}  # 0-100 scale
        
        full_text = "\n".join(formatted_segments)
        yield {"type": "complete", "text": full_text}

class GroqApiStrategy(TranscriptionStrategy):
    def transcribe(self, audio_path: Path, duration: float, api_key: str = None):
        if not api_key:
            raise ValueError("Groq API Key is required for Cloud API Mode")
        
        logger.info("Transcribing using Groq API...")
        yield {"type": "progress", "value": 10} # Fake start progress
        
        # Groq-compatible client
        client = openai.OpenAI(
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1"
        )
        
        try:
            with open(audio_path, "rb") as audio_file:
                yield {"type": "progress", "value": 50}  # Uploading...
                
                # Use Groq's Whisper model (usually very fast)
                transcript = client.audio.transcriptions.create(
                    model="whisper-large-v3", 
                    file=audio_file,
                    response_format="verbose_json"  # Get segments with timestamps
                )
            
            yield {"type": "progress", "value": 90}
            
            # Format segments with timestamps
            formatted_segments = []
            if hasattr(transcript, 'segments'):
                for seg in transcript.segments:
                    # Check if seg is dict or object
                    start = seg.get('start') if isinstance(seg, dict) else seg.start
                    end = seg.get('end') if isinstance(seg, dict) else seg.end
                    text = seg.get('text') if isinstance(seg, dict) else seg.text
                    
                    formatted_line = _format_segment(start, end, text)
                    formatted_segments.append(formatted_line)
            else:
                # Fallback if no segments returned (though verbose_json should have them)
                formatted_segments.append(transcript.text)
            
            full_text = "\n".join(formatted_segments)
            yield {"type": "progress", "value": 100}
            yield {"type": "complete", "text": full_text}
            
        except Exception as e:
            logger.error(f"Groq API Error: {str(e)}")
            raise RuntimeError(f"Groq Transcription Failed: {str(e)}")

class TranscriptionService:
    def __init__(self):
        self.local_strategy = None 
        self.api_strategy = GroqApiStrategy()
        
    def stream_transcribe(self, audio_path: Path, duration: float, mode: str, api_key: str = None):
        if mode == "local":
            if not self.local_strategy:
                self.local_strategy = LocalFasterWhisperStrategy()
            return self.local_strategy.transcribe(audio_path, duration, api_key)
        elif mode == "api":
            return self.api_strategy.transcribe(audio_path, duration, api_key)
        else:
            raise ValueError(f"Unknown mode: {mode}")
