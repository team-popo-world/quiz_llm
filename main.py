#!/usr/bin/env python3
"""
Quiz LLM API Server
10세 이하 어린이를 위한 경제 교육 퀴즈 생성 서버
"""

import uvicorn
import sys
import os

# src 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.app import app
from src.config import settings


def main():
    """메인 함수 - API 서버 실행"""
    print("=" * 50)
    print("Quiz LLM API Server Starting...")
    print(f"Model: {settings.model_name}")
    print(f"Server: http://{settings.host}:{settings.port}")
    print(f"Docs: http://{settings.host}:{settings.port}/docs")
    print("=" * 50)
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
        log_level="info"
    )


if __name__ == "__main__":
    main()
