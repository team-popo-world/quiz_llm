from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, SystemMessage
from langchain.prompts import ChatPromptTemplate
from src.config import settings
from src.models import QuizRequest, QuizResponse, DifficultyLevel
import json
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class QuizGeneratorService:
    """LLM을 사용한 퀴즈 생성 서비스"""
    
    def __init__(self):
        """서비스 초기화"""
        self.llm = ChatGoogleGenerativeAI(
            model=settings.model_name,
            google_api_key=settings.google_api_key,
            temperature=settings.temperature,
            max_tokens=settings.max_tokens
        )
        
        # 난이도별 설명
        self.difficulty_descriptions = {
            DifficultyLevel.EASY: "매우 쉬운 수준으로, 5-7세 어린이도 이해할 수 있는",
            DifficultyLevel.MEDIUM: "보통 수준으로, 8-9세 어린이가 이해할 수 있는", 
            DifficultyLevel.HARD: "어려운 수준으로, 10세 어린이가 도전할 수 있는"
        }
    
    def _create_prompt(self, request: QuizRequest) -> str:
        """퀴즈 생성을 위한 프롬프트 생성"""
        difficulty_desc = self.difficulty_descriptions.get(
            DifficultyLevel(request.difficulty), 
            "적절한 수준의"
        )
        
        topic_instruction = ""
        if request.topic:
            topic_instruction = f"주제는 '{request.topic}'에 관련된 내용으로 하세요."
        
        prompt = f"""
당신은 10세 이하 어린이를 위한 경제 교육 퀴즈를 만드는 전문가입니다.

다음 조건에 맞는 OX 퀴즈 3개를 생성해주세요:

**조건:**
- 난이도: {difficulty_desc} 경제 개념
- 대상: 10세 이하 어린이
- 형식: OX 퀴즈 (정답은 반드시 'O' 또는 'X'만 사용)
- 개수: 정확히 3개
{topic_instruction}

**주제 범위:**
- 용돈과 돈의 개념
- 저축의 중요성
- 현명한 소비
- 필요와 욕구의 구분
- 간단한 경제 활동 (사고팔기 등)

**응답 형식:**
반드시 아래 JSON 형식으로만 응답해주세요. 다른 설명이나 텍스트는 포함하지 마세요.

{{
"difficulty": {request.difficulty},
"Q1": "첫 번째 퀴즈 문제",
"A1": "O",
"Q2": "두 번째 퀴즈 문제", 
"A2": "X",
"Q3": "세 번째 퀴즈 문제",
"A3": "O"
}}

**주의사항:**
- 문제는 어린이가 이해하기 쉬운 단어로 작성
- 일상생활과 연관된 구체적인 예시 사용
- 정답은 반드시 'O' 또는 'X'만 사용
- JSON 형식을 정확히 지켜주세요
"""
        return prompt
    
    async def generate_quiz(self, request: QuizRequest) -> QuizResponse:
        """퀴즈 생성"""
        try:
            prompt = self._create_prompt(request)
            
            # LLM 호출
            messages = [HumanMessage(content=prompt)]
            response = await self.llm.ainvoke(messages)
            
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
            
            # QuizResponse 모델로 변환
            quiz_response = QuizResponse(**quiz_data)
            
            logger.info(f"퀴즈 생성 성공 - 난이도: {request.difficulty}")
            return quiz_response
            
        except Exception as e:
            logger.error(f"퀴즈 생성 실패: {str(e)}")
            raise
    
    def generate_quiz_sync(self, request: QuizRequest) -> QuizResponse:
        """동기 방식 퀴즈 생성"""
        try:
            prompt = self._create_prompt(request)
            
            # LLM 호출 (동기)
            messages = [HumanMessage(content=prompt)]
            response = self.llm.invoke(messages)
            
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
            
            # QuizResponse 모델로 변환
            quiz_response = QuizResponse(**quiz_data)
            
            logger.info(f"퀴즈 생성 성공 - 난이도: {request.difficulty}")
            return quiz_response
            
        except Exception as e:
            logger.error(f"퀴즈 생성 실패: {str(e)}")
            raise
