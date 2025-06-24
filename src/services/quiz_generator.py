from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, SystemMessage
from langchain.prompts import ChatPromptTemplate
from src.config import settings
from src.models import (
    QuizRequest, 
    EasyQuizResponse, 
    MediumQuizResponse, 
    HardQuizResponse,
    QuizResponse,
    DifficultyLevel
)
import json
import logging
import asyncio
from typing import Optional, Union
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)


class QuizGeneratorService:
    """LLM을 사용한 퀴즈 생성 서비스 (비동기 처리)"""
    
    def __init__(self):
        """서비스 초기화"""
        self.llm = ChatGoogleGenerativeAI(
            model=settings.model_name,
            google_api_key=settings.google_api_key,
            temperature=settings.temperature,
            max_tokens=settings.max_tokens
        )
        
        # 동시성 제한을 위한 세마포어 (설정에서 가져옴)
        self._semaphore = asyncio.Semaphore(settings.max_concurrent_requests)
        
        # 난이도별 설명
        self.difficulty_descriptions = {
            DifficultyLevel.EASY: "매우 쉬운 수준으로, 5-7세 어린이도 이해할 수 있는",
            DifficultyLevel.MEDIUM: "보통 수준으로, 8-9세 어린이가 이해할 수 있는", 
            DifficultyLevel.HARD: "어려운 수준으로, 10세 어린이가 도전할 수 있는"
        }
    
    def _create_easy_prompt(self, request: QuizRequest) -> str:
        """쉬운 난이도(OX 퀴즈) 프롬프트 생성"""
        topic_instruction = ""
        if request.topic:
            topic_instruction = f"주제는 '{request.topic}'에 관련된 내용으로 하세요."
        
        prompt = f"""
당신은 10세 이하 어린이를 위한 경제 교육 퀴즈를 만드는 전문가입니다.

다음 조건에 맞는 OX 퀴즈 3개를 생성해주세요:

**조건:**
- 난이도: 매우 쉬운 수준으로, 5-7세 어린이도 이해할 수 있는 경제 개념
- 대상: 5-7세 어린이
- 형식: OX 퀴즈 (정답은 반드시 'O' 또는 'X'만 사용)
- 개수: 정확히 3개
{topic_instruction}

**주제 범위:**
- 용돈과 돈의 개념
- 저축의 중요성
- 현명한 소비
- 간단한 경제 활동 (사고팔기 등)

**응답 형식:**
반드시 아래 JSON 형식으로만 응답해주세요. 다른 설명이나 텍스트는 포함하지 마세요.

{{
"difficulty": 0,
"Q1": "첫 번째 퀴즈 문제",
"A1": "O",
"D1": "첫 번째 퀴즈 해설 (왜 이 답이 맞는지 어린이가 이해하기 쉽게 설명)",
"Q2": "두 번째 퀴즈 문제", 
"A2": "X",
"D2": "두 번째 퀴즈 해설 (왜 이 답이 맞는지 어린이가 이해하기 쉽게 설명)",
"Q3": "세 번째 퀴즈 문제",
"A3": "O",
"D3": "세 번째 퀴즈 해설 (왜 이 답이 맞는지 어린이가 이해하기 쉽게 설명)"
}}

**주의사항:**
- 문제는 어린이가 이해하기 쉬운 단어로 작성
- 일상생활과 연관된 구체적인 예시 사용
- 정답은 반드시 'O' 또는 'X'만 사용
- 해설은 어린이가 쉽게 이해할 수 있도록 간단명료하게 작성
- JSON 형식을 정확히 지켜주세요
"""
        return prompt
    
    def _create_medium_prompt(self, request: QuizRequest) -> str:
        """보통 난이도(3지선다) 프롬프트 생성"""
        topic_instruction = ""
        if request.topic:
            topic_instruction = f"주제는 '{request.topic}'에 관련된 내용으로 하세요."
        
        prompt = f"""
당신은 10세 이하 어린이를 위한 경제 교육 퀴즈를 만드는 전문가입니다.

다음 조건에 맞는 3지선다 퀴즈 3개를 생성해주세요:

**조건:**
- 난이도: 보통 수준으로, 8-9세 어린이가 이해할 수 있는 경제 개념
- 대상: 8-9세 어린이
- 형식: 3지선다 (선택지 3개 중 정답 1개)
- 개수: 정확히 3개
{topic_instruction}

**주제 범위:**
- 용돈 관리와 계획
- 저축의 방법과 이유
- 소비의 우선순위
- 경제 활동의 기본 원리

**응답 형식:**
반드시 아래 JSON 형식으로만 응답해주세요. 다른 설명이나 텍스트는 포함하지 마세요.

{{
"difficulty": 1,
"Q1": "첫 번째 퀴즈 문제",
"Q1_choices": ["선택지 1", "선택지 2", "선택지 3"],
"A1": 1,
"D1": "첫 번째 퀴즈 해설 (왜 이 답이 맞는지 어린이가 이해하기 쉽게 설명)",
"Q2": "두 번째 퀴즈 문제",
"Q2_choices": ["선택지 1", "선택지 2", "선택지 3"],
"A2": 2,
"D2": "두 번째 퀴즈 해설 (왜 이 답이 맞는지 어린이가 이해하기 쉽게 설명)",
"Q3": "세 번째 퀴즈 문제",
"Q3_choices": ["선택지 1", "선택지 2", "선택지 3"],
"A3": 3,
"D3": "세 번째 퀴즈 해설 (왜 이 답이 맞는지 어린이가 이해하기 쉽게 설명)"
}}

**주의사항:**
- 문제는 8-9세 어린이가 이해할 수 있는 수준으로 작성
- 선택지는 명확하고 구별되도록 작성
- 정답 번호는 1, 2, 3 중 하나 (1번이 첫 번째 선택지)
- 해설은 어린이가 쉽게 이해할 수 있도록 간단명료하게 작성
- JSON 형식을 정확히 지켜주세요
"""
        return prompt
    
    def _create_hard_prompt(self, request: QuizRequest) -> str:
        """어려운 난이도(4지선다) 프롬프트 생성"""
        topic_instruction = ""
        if request.topic:
            topic_instruction = f"주제는 '{request.topic}'에 관련된 내용으로 하세요."
        
        prompt = f"""
당신은 10세 이하 어린이를 위한 경제 교육 퀴즈를 만드는 전문가입니다.

다음 조건에 맞는 4지선다 퀴즈 3개를 생성해주세요:

**조건:**
- 난이도: 어려운 수준으로, 10세 어린이가 도전할 수 있는 경제 개념
- 대상: 10세 어린이
- 형식: 4지선다 (선택지 4개 중 정답 1개)
- 개수: 정확히 3개
{topic_instruction}

**주제 범위:**
- 복잡한 용돈 관리 상황
- 저축과 투자의 기본 개념
- 합리적 소비 판단
- 경제 활동의 원인과 결과
- 돈의 가치와 물가 개념

**응답 형식:**
반드시 아래 JSON 형식으로만 응답해주세요. 다른 설명이나 텍스트는 포함하지 마세요.

{{
"difficulty": 2,
"Q1": "첫 번째 퀴즈 문제",
"Q1_choices": ["선택지 1", "선택지 2", "선택지 3", "선택지 4"],
"A1": 1,
"D1": "첫 번째 퀴즈 해설 (왜 이 답이 맞는지 어린이가 이해하기 쉽게 설명)",
"Q2": "두 번째 퀴즈 문제",
"Q2_choices": ["선택지 1", "선택지 2", "선택지 3", "선택지 4"],
"A2": 2,
"D2": "두 번째 퀴즈 해설 (왜 이 답이 맞는지 어린이가 이해하기 쉽게 설명)",
"Q3": "세 번째 퀴즈 문제",
"Q3_choices": ["선택지 1", "선택지 2", "선택지 3", "선택지 4"],
"A3": 3,
"D3": "세 번째 퀴즈 해설 (왜 이 답이 맞는지 어린이가 이해하기 쉽게 설명)"
}}

**주의사항:**
- 문제는 10세 어린이가 충분히 고민할 수 있는 수준으로 작성
- 선택지는 모두 그럴듯하되 정답은 명확하게 구별되도록 작성
- 정답 번호는 1, 2, 3, 4 중 하나 (1번이 첫 번째 선택지)
- 해설은 어린이가 쉽게 이해할 수 있도록 간단명료하게 작성
- JSON 형식을 정확히 지켜주세요
"""
        return prompt
    
    async def generate_quiz(
        self, 
        request: QuizRequest, 
        timeout: Optional[float] = None
    ) -> Union[EasyQuizResponse, MediumQuizResponse, HardQuizResponse]:
        """비동기 퀴즈 생성 (타임아웃 및 동시성 제한 포함)"""
        if timeout is None:
            timeout = settings.default_timeout
            
        async with self._semaphore:  # 동시성 제한
            try:
                return await asyncio.wait_for(
                    self._generate_quiz_internal(request),
                    timeout=timeout
                )
            except asyncio.TimeoutError:
                logger.error(f"퀴즈 생성 타임아웃: {timeout}초 초과")
                raise ValueError(f"퀴즈 생성에 너무 많은 시간이 걸렸습니다 ({timeout}초 초과)")
            except Exception as e:
                logger.error(f"퀴즈 생성 실패: {str(e)}")
                raise
    
    async def _generate_quiz_internal(
        self, 
        request: QuizRequest
    ) -> Union[EasyQuizResponse, MediumQuizResponse, HardQuizResponse]:
        """내부 퀴즈 생성 로직"""
        try:
            # 난이도별 프롬프트 선택
            if request.difficulty == DifficultyLevel.EASY:
                prompt = self._create_easy_prompt(request)
            elif request.difficulty == DifficultyLevel.MEDIUM:
                prompt = self._create_medium_prompt(request)
            elif request.difficulty == DifficultyLevel.HARD:
                prompt = self._create_hard_prompt(request)
            else:
                raise ValueError(f"지원하지 않는 난이도입니다: {request.difficulty}")
            
            # LLM 비동기 호출
            messages = [HumanMessage(content=prompt)]
            response = await self.llm.ainvoke(messages)
            
            # 응답 처리
            return self._parse_response(response, request.difficulty)
            
        except Exception as e:
            logger.error(f"퀴즈 생성 실패: {str(e)}")
            raise
    
    def _parse_response(
        self, 
        response, 
        difficulty: DifficultyLevel
    ) -> Union[EasyQuizResponse, MediumQuizResponse, HardQuizResponse]:
        """LLM 응답 파싱"""
        # 응답 텍스트 정리
        response_text = response.content.strip()
        
        # JSON 블록이 있다면 추출
        if "```json" in response_text:
            start = response_text.find("```json") + 7
            end = response_text.find("```", start)
            response_text = response_text[start:end].strip()
        elif "```" in response_text:
            start = response_text.find("```") + 3
            end = response_text.find("```", start)
            response_text = response_text[start:end].strip()
        
        # JSON 파싱
        try:
            quiz_data = json.loads(response_text)
        except json.JSONDecodeError as e:
            logger.error(f"JSON 파싱 실패: {e}, 응답: {response_text}")
            raise ValueError("LLM 응답을 JSON으로 파싱할 수 없습니다.")
        
        # 난이도별 응답 모델로 변환
        if difficulty == DifficultyLevel.EASY:
            quiz_response = EasyQuizResponse(**quiz_data)
        elif difficulty == DifficultyLevel.MEDIUM:
            quiz_response = MediumQuizResponse(**quiz_data)
        else:  # HARD
            quiz_response = HardQuizResponse(**quiz_data)
        
        logger.info(f"퀴즈 생성 성공 - 난이도: {difficulty}")
        return quiz_response
