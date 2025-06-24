from pydantic import BaseModel, Field
from typing import Optional, Literal, Union
from enum import IntEnum


class DifficultyLevel(IntEnum):
    """퀴즈 난이도 레벨"""
    EASY = 0    # 하 - OX 퀴즈
    MEDIUM = 1  # 중 - 3지선다
    HARD = 2    # 상 - 4지선다


class QuizRequest(BaseModel):
    """퀴즈 생성 요청 모델"""
    difficulty: DifficultyLevel = Field(
        default=DifficultyLevel.EASY,
        description="퀴즈 난이도 (0: 하-OX, 1: 중-3지선다, 2: 상-4지선다)"
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


class EasyQuizResponse(BaseModel):
    """쉬운 난이도 퀴즈 응답 모델 (OX 퀴즈)"""
    difficulty: int = Field(description="퀴즈 난이도")
    Q1: str = Field(description="첫 번째 퀴즈 문제")
    A1: Literal["O", "X"] = Field(description="첫 번째 퀴즈 정답")
    D1: str = Field(description="첫 번째 퀴즈 해설")
    Q2: str = Field(description="두 번째 퀴즈 문제")
    A2: Literal["O", "X"] = Field(description="두 번째 퀴즈 정답")
    D2: str = Field(description="두 번째 퀴즈 해설")
    Q3: str = Field(description="세 번째 퀴즈 문제")
    A3: Literal["O", "X"] = Field(description="세 번째 퀴즈 정답")
    D3: str = Field(description="세 번째 퀴즈 해설")


class MediumQuizResponse(BaseModel):
    """보통 난이도 퀴즈 응답 모델 (3지선다)"""
    difficulty: int = Field(description="퀴즈 난이도")
    Q1: str = Field(description="첫 번째 퀴즈 문제")
    Q1_choices: list[str] = Field(description="첫 번째 퀴즈 선택지 (3개)")
    A1: Literal[1, 2, 3] = Field(description="첫 번째 퀴즈 정답 (1, 2, 3)")
    D1: str = Field(description="첫 번째 퀴즈 해설")
    Q2: str = Field(description="두 번째 퀴즈 문제")
    Q2_choices: list[str] = Field(description="두 번째 퀴즈 선택지 (3개)")
    A2: Literal[1, 2, 3] = Field(description="두 번째 퀴즈 정답 (1, 2, 3)")
    D2: str = Field(description="두 번째 퀴즈 해설")
    Q3: str = Field(description="세 번째 퀴즈 문제")
    Q3_choices: list[str] = Field(description="세 번째 퀴즈 선택지 (3개)")
    A3: Literal[1, 2, 3] = Field(description="세 번째 퀴즈 정답 (1, 2, 3)")
    D3: str = Field(description="세 번째 퀴즈 해설")


class HardQuizResponse(BaseModel):
    """어려운 난이도 퀴즈 응답 모델 (4지선다)"""
    difficulty: int = Field(description="퀴즈 난이도")
    Q1: str = Field(description="첫 번째 퀴즈 문제")
    Q1_choices: list[str] = Field(description="첫 번째 퀴즈 선택지 (4개)")
    A1: Literal[1, 2, 3, 4] = Field(description="첫 번째 퀴즈 정답 (1, 2, 3, 4)")
    D1: str = Field(description="첫 번째 퀴즈 해설")
    Q2: str = Field(description="두 번째 퀴즈 문제")
    Q2_choices: list[str] = Field(description="두 번째 퀴즈 선택지 (4개)")
    A2: Literal[1, 2, 3, 4] = Field(description="두 번째 퀴즈 정답 (1, 2, 3, 4)")
    D2: str = Field(description="두 번째 퀴즈 해설")
    Q3: str = Field(description="세 번째 퀴즈 문제")
    Q3_choices: list[str] = Field(description="세 번째 퀴즈 선택지 (4개)")
    A3: Literal[1, 2, 3, 4] = Field(description="세 번째 퀴즈 정답 (1, 2, 3, 4)")
    D3: str = Field(description="세 번째 퀴즈 해설")


# 이전 버전과의 호환성을 위한 별칭
QuizResponse = Union[EasyQuizResponse, MediumQuizResponse, HardQuizResponse]


class ErrorResponse(BaseModel):
    """에러 응답 모델"""
    error: str = Field(description="에러 메시지")
    detail: Optional[str] = Field(default=None, description="에러 상세 정보")
