from pydantic import BaseModel, Field
from typing import Optional, Literal
from enum import IntEnum


class DifficultyLevel(IntEnum):
    """퀴즈 난이도 레벨"""
    EASY = 0    # 하
    MEDIUM = 1  # 중
    HARD = 2    # 상


class QuizRequest(BaseModel):
    """퀴즈 생성 요청 모델"""
    difficulty: DifficultyLevel = Field(
        default=DifficultyLevel.EASY,
        description="퀴즈 난이도 (0: 하, 1: 중, 2: 상)"
    )
    quiz_count: int = Field(
        default=3,
        ge=1,
        le=10,
        description="생성할 퀴즈 개수 (1-10개)"
    )
    topic: Optional[str] = Field(
        default=None,
        description="특정 경제 주제 (예: 용돈, 저축, 소비 등)"
    )


class QuizResponse(BaseModel):
    """퀴즈 응답 모델"""
    difficulty: int = Field(description="퀴즈 난이도")
    Q1: str = Field(description="첫 번째 퀴즈 문제")
    A1: Literal["O", "X"] = Field(description="첫 번째 퀴즈 정답")
    Q2: str = Field(description="두 번째 퀴즈 문제")
    A2: Literal["O", "X"] = Field(description="두 번째 퀴즈 정답")
    Q3: str = Field(description="세 번째 퀴즈 문제")
    A3: Literal["O", "X"] = Field(description="세 번째 퀴즈 정답")


class ErrorResponse(BaseModel):
    """에러 응답 모델"""
    error: str = Field(description="에러 메시지")
    detail: Optional[str] = Field(default=None, description="에러 상세 정보")
