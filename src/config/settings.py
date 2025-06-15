from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    
    # Google AI API Configuration
    google_api_key: str
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Quiz Configuration
    default_difficulty: int = 0
    default_quiz_count: int = 3
    
    # Model Configuration
    model_name: str = "gemini-2.5-flash-preview-05-20"
    max_tokens: Optional[int] = None
    temperature: float = 0.7
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()
