from fastapi import APIRouter, HTTPException, Depends, Query
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
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"퀴즈 생성 중 서버 오류: {str(e)}")
        raise HTTPException(status_code=500, detail="퀴즈 생성 중 오류가 발생했습니다.")


@router.post(
    "/easy",
    response_model=EasyQuizResponse,
    responses={
        400: {"model": ErrorResponse, "description": "잘못된 요청"},
        500: {"model": ErrorResponse, "description": "서버 오류"}
    },
    summary="쉬운 난이도 퀴즈 생성 (OX 퀴즈)",
    description="5-7세 어린이를 위한 쉬운 난이도의 경제 교육 OX 퀴즈를 생성합니다."
)
async def generate_easy_quiz(
    request: SimplifiedQuizRequest = SimplifiedQuizRequest(),
    quiz_service: QuizGeneratorService = Depends(get_quiz_service)
) -> EasyQuizResponse:
    """쉬운 난이도 퀴즈 생성 API"""
    try:
        logger.info(f"쉬운 난이도 퀴즈 생성 요청 - 주제: {request.topic}")
        
        quiz_request = QuizRequest(
            difficulty=DifficultyLevel.EASY,
            quiz_count=3,
            topic=request.topic
        )
        
        quiz_response = await quiz_service.generate_quiz(quiz_request)
        return quiz_response
        
    except ValueError as e:
        logger.error(f"쉬운 퀴즈 생성 중 값 오류: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"쉬운 퀴즈 생성 중 서버 오류: {str(e)}")
        raise HTTPException(status_code=500, detail="퀴즈 생성 중 오류가 발생했습니다.")


@router.post(
    "/medium",
    response_model=MediumQuizResponse,
    responses={
        400: {"model": ErrorResponse, "description": "잘못된 요청"},
        500: {"model": ErrorResponse, "description": "서버 오류"}
    },
    summary="보통 난이도 퀴즈 생성 (3지선다)",
    description="8-9세 어린이를 위한 보통 난이도의 경제 교육 3지선다 퀴즈를 생성합니다."
)
async def generate_medium_quiz(
    request: SimplifiedQuizRequest = SimplifiedQuizRequest(),
    quiz_service: QuizGeneratorService = Depends(get_quiz_service)
) -> MediumQuizResponse:
    """보통 난이도 퀴즈 생성 API"""
    try:
        logger.info(f"보통 난이도 퀴즈 생성 요청 - 주제: {request.topic}")
        
        quiz_request = QuizRequest(
            difficulty=DifficultyLevel.MEDIUM,
            quiz_count=3,
            topic=request.topic
        )
        
        quiz_response = await quiz_service.generate_quiz(quiz_request)
        return quiz_response
        
    except ValueError as e:
        logger.error(f"보통 퀴즈 생성 중 값 오류: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"보통 퀴즈 생성 중 서버 오류: {str(e)}")
        raise HTTPException(status_code=500, detail="퀴즈 생성 중 오류가 발생했습니다.")


@router.post(
    "/hard",
    response_model=HardQuizResponse,
    responses={
        400: {"model": ErrorResponse, "description": "잘못된 요청"},
        500: {"model": ErrorResponse, "description": "서버 오류"}
    },
    summary="어려운 난이도 퀴즈 생성 (4지선다)",
    description="10세 어린이를 위한 어려운 난이도의 경제 교육 4지선다 퀴즈를 생성합니다."
)
async def generate_hard_quiz(
    request: SimplifiedQuizRequest = SimplifiedQuizRequest(),
    quiz_service: QuizGeneratorService = Depends(get_quiz_service)
) -> HardQuizResponse:
    """어려운 난이도 퀴즈 생성 API"""
    try:
        logger.info(f"어려운 난이도 퀴즈 생성 요청 - 주제: {request.topic}")
        
        quiz_request = QuizRequest(
            difficulty=DifficultyLevel.HARD,
            quiz_count=3,
            topic=request.topic
        )
        
        quiz_response = await quiz_service.generate_quiz(quiz_request)
        return quiz_response
        
    except ValueError as e:
        logger.error(f"어려운 퀴즈 생성 중 값 오류: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"어려운 퀴즈 생성 중 서버 오류: {str(e)}")
        raise HTTPException(status_code=500, detail="퀴즈 생성 중 오류가 발생했습니다.")


@router.get(
    "/difficulty-levels",
    summary="지원하는 난이도 레벨 조회",
    description="사용 가능한 퀴즈 난이도 레벨을 조회합니다."
)
async def get_difficulty_levels():
    """지원하는 난이도 레벨 조회"""
    return {
        "difficulty_levels": [
            {
                "level": 0, 
                "name": "하", 
                "description": "5-7세 어린이 수준",
                "format": "OX 퀴즈",
                "endpoint": "/quiz/easy"
            },
            {
                "level": 1, 
                "name": "중", 
                "description": "8-9세 어린이 수준",
                "format": "3지선다",
                "endpoint": "/quiz/medium"
            },
            {
                "level": 2, 
                "name": "상", 
                "description": "10세 어린이 수준",
                "format": "4지선다",
                "endpoint": "/quiz/hard"
            }
        ]
    }


@router.get(
    "/topics",
    summary="추천 주제 목록 조회",
    description="경제 퀴즈에 사용할 수 있는 추천 주제 목록을 조회합니다."
)
async def get_recommended_topics():
    """추천 주제 목록 조회"""
    return {
        "topics": [
            "용돈",
            "저축",
            "소비",
            "필요와 욕구",
            "사고팔기",
            "돈의 종류",
            "은행",
            "계획적인 소비",
            "아껴쓰기",
            "돈의 가치"
        ]
    }
