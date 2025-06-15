from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from src.api import quiz_router
from src.config import settings
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """FastAPI 앱 생성 및 설정"""
    
    app = FastAPI(
        title="Quiz LLM API",
        description="10세 이하 어린이를 위한 경제 교육 퀴즈 생성 API",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # CORS 설정
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 운영환경에서는 특정 도메인으로 제한
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 라우터 등록
    app.include_router(quiz_router)
    
    # 헬스 체크 엔드포인트
    @app.get("/", tags=["Health"])
    async def root():
        """API 상태 확인"""
        return {
            "message": "Quiz LLM API is running!",
            "version": "0.1.0",
            "status": "healthy"
        }
    
    @app.get("/health", tags=["Health"])
    async def health_check():
        """상세 헬스 체크"""
        try:
            # Google API 키 설정 확인
            if not settings.google_api_key or settings.google_api_key == "your_google_api_key_here":
                return {
                    "status": "unhealthy",
                    "message": "Google API key가 설정되지 않았습니다."
                }
            
            return {
                "status": "healthy",
                "message": "모든 서비스가 정상 작동 중입니다.",
                "model": settings.model_name
            }
        except Exception as e:
            logger.error(f"헬스 체크 실패: {str(e)}")
            raise HTTPException(status_code=500, detail="서비스 상태 확인 중 오류가 발생했습니다.")
    
    return app


# 앱 인스턴스 생성
app = create_app()

if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting Quiz LLM API server on {settings.host}:{settings.port}")
    uvicorn.run(
        "src.app:app",
        host=settings.host,
        port=settings.port,
        reload=True
    )
