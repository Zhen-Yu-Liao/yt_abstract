import logging
import os
from abc import ABC, abstractmethod
from pathlib import Path
from faster_whisper import WhisperModel
import openai
from backend.core.config import settings
from typing import Generator, Union

logger = logging.getLogger(__name__)

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
        
        full_text_list = []
        for segment in segments:
            full_text_list.append(segment.text)
            # Calculate progress
            if duration > 0:
                progress = min(segment.end / duration, 0.99)
                yield {"type": "progress", "value": progress * 100} # 0-100 scale
        
        full_text = " ".join(full_text_list)
        yield {"type": "complete", "text": full_text}

class OpenAIApiStrategy(TranscriptionStrategy):
    def transcribe(self, audio_path: Path, duration: float, api_key: str = None):
        if not api_key:
            raise ValueError("API Key is required for API Mode")
        
        logger.info("Transcribing using OpenAI API...")
        yield {"type": "progress", "value": 10} # Fake start progress
        
        client = openai.OpenAI(api_key=api_key)
        
        with open(audio_path, "rb") as audio_file:
            yield {"type": "progress", "value": 50} # Uploading...
            transcript = client.audio.transcriptions.create(
                model="whisper-1", 
                file=audio_file
            )
        
        yield {"type": "progress", "value": 100}
        yield {"type": "complete", "text": transcript.text}

class TranscriptionService:
    def __init__(self):
        self.local_strategy = None 
        self.api_strategy = OpenAIApiStrategy()
        
    def stream_transcribe(self, audio_path: Path, duration: float, mode: str, api_key: str = None):
        if mode == "local":
            if not self.local_strategy:
                self.local_strategy = LocalFasterWhisperStrategy()
            return self.local_strategy.transcribe(audio_path, duration, api_key)
        elif mode == "api":
            return self.api_strategy.transcribe(audio_path, duration, api_key)
        else:
            raise ValueError(f"Unknown mode: {mode}")
