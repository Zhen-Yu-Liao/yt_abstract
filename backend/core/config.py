import os
from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "YT Abstract"
    API_V1_STR: str = "/api"
    
    # Base Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    TEMP_DIR: Path = BASE_DIR / "temp"
    
    # AI Config
    DEFAULT_WHISPER_MODEL: str = "medium"  # or 'large-v3' if GPU allows
    
    # API Keys (Optional, can be injected at runtime or env)
    # The frontend will send these if provided by user
    
    class Config:
        env_file = ".env"
        extra = "ignore"  # Allow extra fields from .env (like OPENAI_API_KEY, GEMINI_API_KEY)

settings = Settings()

# Ensure temp dir exists
os.makedirs(settings.TEMP_DIR, exist_ok=True)
