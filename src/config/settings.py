from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    
    # Google AI API Configuration
    google_api_key: str
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8003
    
    # Quiz Configuration
    default_difficulty: int = 0
    default_quiz_count: int = 3
    
    # Model Configuration
    model_name: str = "gemini-2.5-flash"
    max_tokens: Optional[int] = None
    temperature: float = 0.7
    
    # 비동기 처리 설정
    max_concurrent_requests: int = 5  # 최대 동시 요청 수
    default_timeout: float = 30.0  # 기본 타임아웃 (초)
    llm_timeout: float = 25.0  # LLM 응답 타임아웃 (초)
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()
