from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, Literal
import asyncio
import json
import logging
from backend.services.media_service import MediaService
from backend.services.transcription_service import TranscriptionService
from backend.services.summary_service import SummaryService
from backend.utils.sse import format_sse

router = APIRouter()
logger = logging.getLogger(__name__)

# Models
class ProcessRequest(BaseModel):
    url: str
    mode: Literal["local", "api"] = "local"
    task_type: Literal["transcribe", "summary"] = "transcribe"
    openai_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None

# Services
media_service = MediaService()
transcription_service = TranscriptionService()
summary_service = SummaryService()

@router.post("/process_stream")
async def process_stream_video(request: ProcessRequest):
    async def event_generator():
        audio_path = None
        try:
            # 1. Validation
            if request.mode == "api" and not request.openai_api_key:
                yield format_sse("error", "OpenAI API Key is required for API mode")
                return
            from backend.core.config import settings
            if request.task_type == "summary" and not request.gemini_api_key and not settings.GEMINI_API_KEY:
                yield format_sse("error", "Gemini API Key is required for summary task (or set GEMINI_API_KEY in .env)")
                return

            # 2. Download Media (with Queue for progress)
            progress_queue = asyncio.Queue()
            loop = asyncio.get_running_loop()  # Capture event loop for thread-safe callback
            
            def download_progress_callback(progress_info):
                # progress_info is now a dict: {percent, downloaded, total, speed}
                loop.call_soon_threadsafe(progress_queue.put_nowait, progress_info)

            # Start download in background thread to avoid blocking event loop
            download_task = asyncio.create_task(
                asyncio.to_thread(media_service.download_audio, request.url, download_progress_callback)
            )

            # Consume queue while downloading
            while not download_task.done():
                try:
                    # Wait for progress or task completion
                    progress_info = await asyncio.wait_for(progress_queue.get(), timeout=0.1)
                    yield format_sse("progress", {
                        "stage": "downloading",
                        "progress": progress_info.get('percent', 0),
                        "downloaded": progress_info.get('downloaded', 0),
                        "total": progress_info.get('total', 0),
                        "speed": progress_info.get('speed', 0)
                    })
                except asyncio.TimeoutError:
                    continue
            
            # Check for exceptions in download
            try:
                audio_path, title, duration = await download_task
            except Exception as e:
                yield format_sse("error", f"Download failed: {str(e)}")
                return
            
            yield format_sse("progress", {"stage": "downloading", "progress": 100})
            
            # 3. Transcribe
            # Since transcription_service.stream_transcribe is a sync generator (yields), 
            # we can iterate it. If it blocks event loop, we might need run_in_executor, 
            # but LocalWhisper on GPU is heavy. Ideally run in thread. 'faster_whisper' releases GIL mostly?
            # Let's verify. faster-whisper calls CTranslate2 which releases GIL.
            
            full_transcript = ""
            
            # We wrap the sync generator in an async context or just iterate directly if it's fast enough 
            # or use to_thread for the blocking generator? 
            # It's safer to iterate normally, but each yield assumes quick return. 
            # faster-whisper yields segments.
            
            # Note: We refactored TranscriptionService to yield dicts
            stream = transcription_service.stream_transcribe(
                audio_path=audio_path,
                duration=duration,
                mode=request.mode,
                api_key=request.openai_api_key
            )
            
            for event in stream:
                if event['type'] == 'progress':
                    yield format_sse("progress", {"stage": "transcribing", "progress": event['value']})
                    # Yield to event loop to allow other tasks (like pings)
                    await asyncio.sleep(0) 
                elif event['type'] == 'complete':
                    full_transcript = event['text']

            yield format_sse("progress", {"stage": "transcribing", "progress": 100})

            # 4. Summary (Optional)
            summary = None
            if request.task_type == "summary":
                yield format_sse("progress", {"stage": "summarizing", "progress": 10})
                
                # Mock progress for summary since it's one call
                # Realistically we can't get progress from Gemini REST API easily
                # We simulate it with small delays or just indeterminate
                
                # Run summary in thread to avoid blocking loop
                yield format_sse("progress", {"stage": "summarizing", "progress": 50})
                
                summary = await asyncio.to_thread(
                    summary_service.summarize,
                    text=full_transcript,
                    api_key=request.gemini_api_key
                )
                
                yield format_sse("progress", {"stage": "summarizing", "progress": 100})
            
            # Final Result
            yield format_sse("result", {
                "transcript": full_transcript,
                "summary": summary
            })
            
        except Exception as e:
            logger.error(f"Stream error: {str(e)}")
            yield format_sse("error", str(e))
        finally:
            if audio_path:
                media_service.cleanup(audio_path)

    return StreamingResponse(event_generator(), media_type="text/event-stream")
