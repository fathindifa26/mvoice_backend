import os
from pydantic_settings import BaseSettings
from typing import List, Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "MVoice Intelligence API"
    API_V1_STR: str = "/api"
    
    CORS_ORIGINS: List[str] = ["*"]
    
    # AI Configuration
    OPENROUTER_API_KEY: Optional[str] = None
    AI_MODEL: str = "google/gemini-3-flash-preview" # Or google/gemini-flash-1.5-8b
    
    CSV_PATH: str = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "creatives_dummy.csv")
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
