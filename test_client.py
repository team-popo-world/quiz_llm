#!/usr/bin/env python3
"""
Quiz LLM API 테스트 클라이언트
"""

import sys
import os
import asyncio

# src 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.services import QuizGeneratorService
from src.models import QuizRequest, DifficultyLevel


async def test_quiz_generation():
    """퀴즈 생성 테스트"""
    print("=== Quiz LLM 테스트 시작 ===\n")
    
    # 서비스 인스턴스 생성
    quiz_service = QuizGeneratorService()
    
    # 각 난이도별 테스트
    difficulties = [
        (DifficultyLevel.EASY, "쉬움 (OX 퀴즈)", "용돈"),
        (DifficultyLevel.MEDIUM, "보통 (3지선다)", "저축"),
        (DifficultyLevel.HARD, "어려움 (4지선다)", "소비")
    ]
    
    for difficulty, desc, topic in difficulties:
        print(f"=== {desc} 테스트 ===")
        
        test_request = QuizRequest(
            difficulty=difficulty,
            quiz_count=3,
            topic=topic
        )
        
        print(f"테스트 요청:")
        print(f"- 난이도: {test_request.difficulty} ({desc})")
        print(f"- 퀴즈 개수: {test_request.quiz_count}")
        print(f"- 주제: {test_request.topic}")
        print("\n퀴즈 생성 중...\n")
        
        try:
            # 퀴즈 생성
            quiz_response = await quiz_service.generate_quiz(test_request)
            
            # 결과 출력
            print("=== 생성된 퀴즈 ===")
            print(f"난이도: {quiz_response.difficulty}")
            print()
            
            if difficulty == DifficultyLevel.EASY:
                # OX 퀴즈
                print(f"Q1: {quiz_response.Q1}")
                print(f"A1: {quiz_response.A1}")
                print()
                print(f"Q2: {quiz_response.Q2}")
                print(f"A2: {quiz_response.A2}")
                print()
                print(f"Q3: {quiz_response.Q3}")
                print(f"A3: {quiz_response.A3}")
            elif difficulty == DifficultyLevel.MEDIUM:
                # 3지선다
                print(f"Q1: {quiz_response.Q1}")
                for i, choice in enumerate(quiz_response.Q1_choices, 1):
                    mark = "★" if i == quiz_response.A1 else " "
                    print(f"  {mark} {i}. {choice}")
                print()
                print(f"Q2: {quiz_response.Q2}")
                for i, choice in enumerate(quiz_response.Q2_choices, 1):
                    mark = "★" if i == quiz_response.A2 else " "
                    print(f"  {mark} {i}. {choice}")
                print()
                print(f"Q3: {quiz_response.Q3}")
                for i, choice in enumerate(quiz_response.Q3_choices, 1):
                    mark = "★" if i == quiz_response.A3 else " "
                    print(f"  {mark} {i}. {choice}")
            else:  # HARD
                # 4지선다
                print(f"Q1: {quiz_response.Q1}")
                for i, choice in enumerate(quiz_response.Q1_choices, 1):
                    mark = "★" if i == quiz_response.A1 else " "
                    print(f"  {mark} {i}. {choice}")
                print()
                print(f"Q2: {quiz_response.Q2}")
                for i, choice in enumerate(quiz_response.Q2_choices, 1):
                    mark = "★" if i == quiz_response.A2 else " "
                    print(f"  {mark} {i}. {choice}")
                print()
                print(f"Q3: {quiz_response.Q3}")
                for i, choice in enumerate(quiz_response.Q3_choices, 1):
                    mark = "★" if i == quiz_response.A3 else " "
                    print(f"  {mark} {i}. {choice}")
            
            print(f"\n=== {desc} 테스트 완료 ===\n")
            
        except Exception as e:
            print(f"오류 발생: {str(e)}")
            print("Google API 키가 올바르게 설정되었는지 확인해주세요.\n")


def test_sync():
    """동기 방식 테스트"""
    print("=== 동기 방식 쉬운 퀴즈 생성 테스트 ===\n")
    
    quiz_service = QuizGeneratorService()
    
    test_request = QuizRequest(
        difficulty=DifficultyLevel.EASY,
        quiz_count=3
    )
    
    try:
        quiz_response = quiz_service.generate_quiz_sync(test_request)
        
        print("=== 생성된 퀴즈 (동기) ===")
        print(f"난이도: {quiz_response.difficulty}")
        print()
        print(f"Q1: {quiz_response.Q1}")
        print(f"A1: {quiz_response.A1}")
        print()
        print(f"Q2: {quiz_response.Q2}")
        print(f"A2: {quiz_response.A2}")
        print()
        print(f"Q3: {quiz_response.Q3}")
        print(f"A3: {quiz_response.A3}")
        print("\n=== 동기 테스트 완료 ===")
        
    except Exception as e:
        print(f"오류 발생: {str(e)}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Quiz LLM 테스트")
    parser.add_argument("--sync", action="store_true", help="동기 방식으로 테스트")
    parser.add_argument("--difficulty", choices=["easy", "medium", "hard"], 
                       help="특정 난이도만 테스트")
    args = parser.parse_args()
    
    if args.sync:
        test_sync()
    else:
        asyncio.run(test_quiz_generation())
