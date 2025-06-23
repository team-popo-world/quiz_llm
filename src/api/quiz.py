from fastapi import APIRouter, HTTPException, Depends, Query, Path
from src.models import (
    QuizRequest, 
    EasyQuizResponse, 
    MediumQuizResponse, 
    HardQuizResponse,
    QuizResponse,
    ErrorResponse, 
    DifficultyLevel
)
from src.services import QuizGeneratorService
from src.config import settings
from pydantic import BaseModel, Field
from typing import Optional, Union
import logging
import asyncio

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/quiz", tags=["Quiz"])

# QuizGeneratorService 의존성
def get_quiz_service() -> QuizGeneratorService:
    return QuizGeneratorService()


class SimplifiedQuizRequest(BaseModel):
    """간소화된 퀴즈 요청 모델 (난이도별 엔드포인트용)"""
    topic: Optional[str] = Field(
        default=None,
        description="특정 경제 주제 (예: 용돈, 저축, 소비 등)"
    )


@router.post(
    "/generate",
    response_model=Union[EasyQuizResponse, MediumQuizResponse, HardQuizResponse],
    responses={
        400: {"model": ErrorResponse, "description": "잘못된 요청"},
        408: {"model": ErrorResponse, "description": "요청 타임아웃"},
        500: {"model": ErrorResponse, "description": "서버 오류"}
    },
    summary="경제 퀴즈 생성 (범용)",
    description="10세 이하 어린이를 위한 경제 교육 퀴즈를 생성합니다. 난이도를 직접 지정할 수 있습니다."
)
async def generate_quiz(
    request: QuizRequest,
    timeout: float = Query(default=30.0, ge=5.0, le=120.0, description="타임아웃 시간 (초)"),
    quiz_service: QuizGeneratorService = Depends(get_quiz_service)
) -> Union[EasyQuizResponse, MediumQuizResponse, HardQuizResponse]:
    """경제 퀴즈 생성 API (범용)"""
    try:
        logger.info(f"퀴즈 생성 요청 - 난이도: {request.difficulty}, 개수: {request.quiz_count}, 주제: {request.topic}, 타임아웃: {timeout}초")
        
        # 현재는 3개 퀴즈만 지원
        if request.quiz_count != 3:
            raise HTTPException(
                status_code=400,
                detail="현재 버전에서는 3개 퀴즈만 지원합니다."
            )
        
        quiz_response = await quiz_service.generate_quiz(request, timeout=timeout)
        return quiz_response
        
    except asyncio.TimeoutError:
        logger.error(f"퀴즈 생성 타임아웃: {timeout}초")
        raise HTTPException(status_code=408, detail=f"퀴즈 생성에 너무 많은 시간이 걸렸습니다 ({timeout}초 초과)")
    except ValueError as e:
        logger.error(f"퀴즈 생성 중 값 오류: {str(e)}")
        if "타임아웃" in str(e) or "시간이 걸렸습니다" in str(e):
            raise HTTPException(status_code=408, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"퀴즈 생성 중 서버 오류: {str(e)}")
        raise HTTPException(status_code=500, detail="퀴즈 생성 중 오류가 발생했습니다.")


@router.post(
    "/easy",
    response_model=EasyQuizResponse,
    responses={
        400: {"model": ErrorResponse, "description": "잘못된 요청"},
        408: {"model": ErrorResponse, "description": "요청 타임아웃"},
        500: {"model": ErrorResponse, "description": "서버 오류"}
    },
    summary="쉬운 난이도 퀴즈 생성 (OX 퀴즈)",
    description="5-7세 어린이를 위한 쉬운 난이도의 경제 교육 OX 퀴즈를 생성합니다."
)
async def generate_easy_quiz(
    request: SimplifiedQuizRequest = SimplifiedQuizRequest(),
    timeout: float = Query(default=25.0, ge=5.0, le=120.0, description="타임아웃 시간 (초)"),
    quiz_service: QuizGeneratorService = Depends(get_quiz_service)
) -> EasyQuizResponse:
    """쉬운 난이도 퀴즈 생성 API"""
    try:
        logger.info(f"쉬운 난이도 퀴즈 생성 요청 - 주제: {request.topic}, 타임아웃: {timeout}초")
        
        quiz_request = QuizRequest(
            difficulty=DifficultyLevel.EASY,
            quiz_count=3,
            topic=request.topic
        )
        
        quiz_response = await quiz_service.generate_quiz(quiz_request, timeout=timeout)
        return quiz_response
        
    except asyncio.TimeoutError:
        logger.error(f"쉬운 퀴즈 생성 타임아웃: {timeout}초")
        raise HTTPException(status_code=408, detail=f"퀴즈 생성에 너무 많은 시간이 걸렸습니다 ({timeout}초 초과)")
    except ValueError as e:
        logger.error(f"쉬운 퀴즈 생성 중 값 오류: {str(e)}")
        if "타임아웃" in str(e) or "시간이 걸렸습니다" in str(e):
            raise HTTPException(status_code=408, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"쉬운 퀴즈 생성 중 서버 오류: {str(e)}")
        raise HTTPException(status_code=500, detail="쉬운 퀴즈 생성 중 오류가 발생했습니다.")


@router.post(
    "/medium",
    response_model=MediumQuizResponse,
    responses={
        400: {"model": ErrorResponse, "description": "잘못된 요청"},
        408: {"model": ErrorResponse, "description": "요청 타임아웃"},
        500: {"model": ErrorResponse, "description": "서버 오류"}
    },
    summary="보통 난이도 퀴즈 생성 (3지선다)",
    description="8-9세 어린이를 위한 보통 난이도의 경제 교육 3지선다 퀴즈를 생성합니다."
)
async def generate_medium_quiz(
    request: SimplifiedQuizRequest = SimplifiedQuizRequest(),
    timeout: float = Query(default=30.0, ge=5.0, le=120.0, description="타임아웃 시간 (초)"),
    quiz_service: QuizGeneratorService = Depends(get_quiz_service)
) -> MediumQuizResponse:
    """보통 난이도 퀴즈 생성 API"""
    try:
        logger.info(f"보통 난이도 퀴즈 생성 요청 - 주제: {request.topic}, 타임아웃: {timeout}초")
        
        quiz_request = QuizRequest(
            difficulty=DifficultyLevel.MEDIUM,
            quiz_count=3,
            topic=request.topic
        )
        
        quiz_response = await quiz_service.generate_quiz(quiz_request, timeout=timeout)
        return quiz_response
        
    except asyncio.TimeoutError:
        logger.error(f"보통 퀴즈 생성 타임아웃: {timeout}초")
        raise HTTPException(status_code=408, detail=f"퀴즈 생성에 너무 많은 시간이 걸렸습니다 ({timeout}초 초과)")
    except ValueError as e:
        logger.error(f"보통 퀴즈 생성 중 값 오류: {str(e)}")
        if "타임아웃" in str(e) or "시간이 걸렸습니다" in str(e):
            raise HTTPException(status_code=408, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"보통 퀴즈 생성 중 서버 오류: {str(e)}")
        raise HTTPException(status_code=500, detail="보통 퀴즈 생성 중 오류가 발생했습니다.")


@router.post(
    "/hard",
    response_model=HardQuizResponse,
    responses={
        400: {"model": ErrorResponse, "description": "잘못된 요청"},
        408: {"model": ErrorResponse, "description": "요청 타임아웃"},
        500: {"model": ErrorResponse, "description": "서버 오류"}
    },
    summary="어려운 난이도 퀴즈 생성 (4지선다)",
    description="10세 어린이를 위한 어려운 난이도의 경제 교육 4지선다 퀴즈를 생성합니다."
)
async def generate_hard_quiz(
    request: SimplifiedQuizRequest = SimplifiedQuizRequest(),
    timeout: float = Query(default=35.0, ge=5.0, le=120.0, description="타임아웃 시간 (초)"),
    quiz_service: QuizGeneratorService = Depends(get_quiz_service)
) -> HardQuizResponse:
    """어려운 난이도 퀴즈 생성 API"""
    try:
        logger.info(f"어려운 난이도 퀴즈 생성 요청 - 주제: {request.topic}, 타임아웃: {timeout}초")
        
        quiz_request = QuizRequest(
            difficulty=DifficultyLevel.HARD,
            quiz_count=3,
            topic=request.topic
        )
        
        quiz_response = await quiz_service.generate_quiz(quiz_request, timeout=timeout)
        return quiz_response
        
    except asyncio.TimeoutError:
        logger.error(f"어려운 퀴즈 생성 타임아웃: {timeout}초")
        raise HTTPException(status_code=408, detail=f"퀴즈 생성에 너무 많은 시간이 걸렸습니다 ({timeout}초 초과)")
    except ValueError as e:
        logger.error(f"어려운 퀴즈 생성 중 값 오류: {str(e)}")
        if "타임아웃" in str(e) or "시간이 걸렸습니다" in str(e):
            raise HTTPException(status_code=408, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"어려운 퀴즈 생성 중 서버 오류: {str(e)}")
        raise HTTPException(status_code=500, detail="어려운 퀴즈 생성 중 오류가 발생했습니다.")


@router.post(
    "/{difficulty}/{topic}",
    response_model=Union[EasyQuizResponse, MediumQuizResponse, HardQuizResponse],
    responses={
        400: {"model": ErrorResponse, "description": "잘못된 요청"},
        408: {"model": ErrorResponse, "description": "요청 타임아웃"},
        500: {"model": ErrorResponse, "description": "서버 오류"}
    },
    summary="난이도와 주제별 퀴즈 생성",
    description="URL 경로로 난이도와 주제를 지정하여 경제 퀴즈를 생성합니다."
)
async def generate_quiz_by_path(
    difficulty: str = Path(..., description="퀴즈 난이도 (easy/medium/hard)"),
    topic: str = Path(..., description="퀴즈 주제 (예: 용돈, 저축, 소비 등)"),
    timeout: float = Query(default=30.0, ge=5.0, le=120.0, description="타임아웃 시간 (초)"),
    quiz_service: QuizGeneratorService = Depends(get_quiz_service)
) -> Union[EasyQuizResponse, MediumQuizResponse, HardQuizResponse]:
    """URL 경로로 난이도와 주제를 지정한 퀴즈 생성"""
    try:
        # 난이도 매핑
        difficulty_map = {
            "easy": DifficultyLevel.EASY,
            "medium": DifficultyLevel.MEDIUM,
            "hard": DifficultyLevel.HARD
        }
        
        if difficulty.lower() not in difficulty_map:
            raise HTTPException(
                status_code=400,
                detail=f"지원하지 않는 난이도입니다. 사용 가능한 난이도: {list(difficulty_map.keys())}"
            )
        
        # URL 디코딩 (한글 주제 처리)
        from urllib.parse import unquote
        decoded_topic = unquote(topic)
        
        logger.info(f"경로 기반 퀴즈 생성 요청 - 난이도: {difficulty}, 주제: {decoded_topic}, 타임아웃: {timeout}초")
        
        # QuizRequest 객체 생성
        quiz_request = QuizRequest(
            difficulty=difficulty_map[difficulty.lower()],
            quiz_count=3,
            topic=decoded_topic
        )
        
        # 퀴즈 생성
        quiz_response = await quiz_service.generate_quiz(quiz_request, timeout=timeout)
        return quiz_response
        
    except asyncio.TimeoutError:
        logger.error(f"퀴즈 생성 타임아웃: {timeout}초")
        raise HTTPException(status_code=408, detail=f"퀴즈 생성에 너무 많은 시간이 걸렸습니다 ({timeout}초 초과)")
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"퀴즈 생성 중 값 오류: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"퀴즈 생성 중 서버 오류: {str(e)}")
        raise HTTPException(status_code=500, detail="퀴즈 생성 중 오류가 발생했습니다.")


@router.get(
    "/difficulty-levels",
    response_model=dict,
    summary="지원되는 난이도 목록",
    description="퀴즈 생성 시 사용할 수 있는 난이도 레벨을 반환합니다."
)
async def get_difficulty_levels():
    """지원되는 난이도 레벨 목록 반환"""
    return {
        "difficulty_levels": [
            {
                "level": 0,
                "name": "easy",
                "description": "5-7세 어린이용 OX 퀴즈",
                "format": "True/False"
            },
            {
                "level": 1,
                "name": "medium", 
                "description": "8-9세 어린이용 3지선다 퀴즈",
                "format": "Multiple Choice (3 options)"
            },
            {
                "level": 2,
                "name": "hard",
                "description": "10세 어린이용 4지선다 퀴즈", 
                "format": "Multiple Choice (4 options)"
            }
        ]
    }


@router.get(
    "/topics",
    response_model=dict,
    summary="추천 퀴즈 주제 목록",
    description="퀴즈 생성 시 사용할 수 있는 추천 경제 교육 주제를 반환합니다."
)
async def get_quiz_topics():
    """추천 퀴즈 주제 목록 반환"""
    return {
        "topics": [
            "용돈", "저축", "소비", "투자", "은행",
            "화폐", "물가", "시장", "거래",
            "예산", "경제활동", "직업", "수입", "지출"
        ],
        "description": "어린이 경제 교육에 적합한 주제들입니다. 이외의 주제도 자유롭게 입력할 수 있습니다."
    }


@router.get(
    "/health",
    summary="서비스 상태 확인",
    description="Quiz 생성 서비스의 상태를 확인합니다."
)
async def health_check():
    """서비스 헬스체크"""
    try:
        # 간단한 서비스 가용성 테스트
        quiz_service = QuizGeneratorService()
        return {
            "status": "healthy",
            "service": "quiz-generator",
            "message": "Quiz LLM 서비스가 정상적으로 작동중입니다.",
            "async_mode": True,
            "max_concurrent_requests": settings.max_concurrent_requests,
            "default_timeout": settings.default_timeout
        }
    except Exception as e:
        logger.error(f"헬스체크 실패: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail=f"Quiz 생성 서비스가 사용할 수 없습니다: {str(e)}"
        )


@router.get(
    "/performance",
    summary="비동기 성능 정보",
    description="현재 비동기 처리 성능 및 설정 정보를 반환합니다."
)
async def get_performance_info():
    """비동기 성능 정보 반환"""
    return {
        "async_settings": {
            "max_concurrent_requests": settings.max_concurrent_requests,
            "default_timeout": settings.default_timeout,
            "llm_timeout": settings.llm_timeout
        },
        "performance_tips": [
            "타임아웃 값을 조정하여 응답 속도를 최적화할 수 있습니다",
            "동시 요청 수가 제한되어 서버 안정성을 보장합니다",
            "비동기 처리로 여러 요청을 효율적으로 처리합니다"
        ]
    }
