# Quiz LLM API

10세 이하 어린이를 위한 경제 교육 퀴즈 생성 API

## 기능

- **LLM 기반 퀴즈 생성**: Gemini 2.5 Flash Preview 모델을 사용하여 고품질 경제 퀴즈 생성
- **난이도별 퀴즈 형태**: 
  - **하(0)**: OX 퀴즈 (5-7세)
  - **중(1)**: 3지선다 (8-9세) 
  - **상(2)**: 4지선다 (10세)
- **주제별 퀴즈**: 용돈, 저축, 소비 등 다양한 경제 주제
- **API 형태 제공**: FastAPI 기반의 RESTful API

## 설치 및 실행

### 1. 환경 설정

```bash
# Python 3.10 이상 필요
uv sync  # 의존성 설치
```

### 2. 환경 변수 설정

`.env` 파일을 생성하고 Google AI API 키를 설정하세요:

```env
# Google AI API Key (필수)
GOOGLE_API_KEY=your_google_api_key_here

# Server Configuration
HOST=0.0.0.0
PORT=8000

# Quiz Configuration
DEFAULT_DIFFICULTY=0
DEFAULT_QUIZ_COUNT=3
```

### 3. 서버 실행

```bash
# 개발 모드로 실행
uv run python main.py

# 또는 직접 실행
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 4. API 문서 확인

서버 실행 후 브라우저에서 다음 URL을 방문하세요:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API 사용법

### 1. 난이도별 퀴즈 생성 (추천)

#### 쉬운 난이도 (5-7세) - OX 퀴즈
```bash
curl -X POST "http://localhost:8000/quiz/easy" \
  -H "Content-Type: application/json" \
  -d '{"topic": "용돈"}'
```

**응답 예시:**
```json
{
  "difficulty": 0,
  "Q1": "용돈을 받으면 모두 사탕에 써도 됩니다.",
  "A1": "X",
  "Q2": "용돈을 저금통에 모으는 것은 저축입니다.",
  "A2": "O",
  "Q3": "필요한 것과 갖고 싶은 것을 구분하는 것이 중요합니다.",
  "A3": "O"
}
```

#### 보통 난이도 (8-9세) - 3지선다
```bash
curl -X POST "http://localhost:8000/quiz/medium" \
  -H "Content-Type: application/json" \
  -d '{"topic": "저축"}'
```

**응답 예시:**
```json
{
  "difficulty": 1,
  "Q1": "저축을 하는 가장 좋은 이유는 무엇일까요?",
  "Q1_choices": ["친구들에게 자랑하기 위해", "나중에 큰 것을 사기 위해", "돈을 많이 보기 위해"],
  "A1": 2,
  "Q2": "용돈을 저축할 때 가장 안전한 곳은?",
  "Q2_choices": ["책상 서랍", "저금통이나 은행", "가방 속"],
  "A2": 2,
  "Q3": "한 달에 1000원씩 저축하면 1년에 얼마를 모을 수 있을까요?",
  "Q3_choices": ["10000원", "12000원", "15000원"],
  "A3": 2
}
```

#### 어려운 난이도 (10세) - 4지선다
```bash
curl -X POST "http://localhost:8000/quiz/hard" \
  -H "Content-Type: application/json" \
  -d '{"topic": "소비"}'
```

**응답 예시:**
```json
{
  "difficulty": 2,
  "Q1": "현명한 소비를 위해 가장 중요한 것은?",
  "Q1_choices": ["가격이 가장 싼 것 선택", "브랜드가 유명한 것 선택", "필요성과 예산 고려", "친구가 추천하는 것 선택"],
  "A1": 3,
  "Q2": "같은 물건을 살 때 어떻게 해야 할까요?",
  "Q2_choices": ["가장 가까운 곳에서 구매", "가격 비교 후 구매", "광고를 많이 본 곳에서 구매", "가장 예쁜 포장지 선택"],
  "A2": 2,
  "Q3": "용돈으로 물건을 살 때 가장 먼저 생각해야 할 것은?",
  "Q3_choices": ["친구들이 좋아하는지", "정말 필요한 물건인지", "색깔이 예쁜지", "크기가 큰지"],
  "A3": 2
}
```

#### 주제 없이 생성
```bash
curl -X POST "http://localhost:8000/quiz/easy" \
  -H "Content-Type: application/json" \
  -d '{}'
```

### 2. 범용 퀴즈 생성

```bash
curl -X POST "http://localhost:8000/quiz/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "difficulty": 0,
    "quiz_count": 3,
    "topic": "용돈"
  }'
```

**응답 예시 (난이도에 따라 다름):**
```json
{
  "difficulty": 0,
  "Q1": "용돈을 받으면 모두 사탕에 써도 됩니다.",
  "A1": "X",
  "Q2": "용돈을 저금통에 모으는 것은 저축입니다.",
  "A2": "O",
  "Q3": "필요한 것과 갖고 싶은 것을 구분하는 것이 중요합니다.",
  "A3": "O"
}
```

### 3. 지원하는 난이도 확인

```bash
curl -X GET "http://localhost:8000/quiz/difficulty-levels"
```

### 4. 추천 주제 확인

```bash
curl -X GET "http://localhost:8000/quiz/topics"
```

## 엔드포인트 목록

| 엔드포인트 | 메서드 | 설명 | 대상 연령 | 퀴즈 형태 |
|-----------|--------|------|----------|-----------|
| `/quiz/easy` | POST | 쉬운 난이도 퀴즈 생성 | 5-7세 | OX 퀴즈 |
| `/quiz/medium` | POST | 보통 난이도 퀴즈 생성 | 8-9세 | 3지선다 |
| `/quiz/hard` | POST | 어려운 난이도 퀴즈 생성 | 10세 | 4지선다 |
| `/quiz/generate` | POST | 범용 퀴즈 생성 (난이도 직접 지정) | 전체 | 난이도별 |
| `/quiz/difficulty-levels` | GET | 난이도 레벨 조회 | - | - |
| `/quiz/topics` | GET | 추천 주제 조회 | - | - |

## 테스트

테스트 클라이언트를 사용하여 기능을 확인할 수 있습니다:

```bash
# 비동기 테스트
uv run python test_client.py

# 동기 테스트
uv run python test_client.py --sync
```

## 프로젝트 구조

```
quiz_llm/
├── src/
│   ├── __init__.py
│   ├── app.py              # FastAPI 앱 설정
│   ├── api/                # API 엔드포인트
│   │   ├── __init__.py
│   │   └── quiz.py
│   ├── config/             # 설정 관리
│   │   ├── __init__.py
│   │   └── settings.py
│   ├── models/             # 데이터 모델
│   │   ├── __init__.py
│   │   └── quiz.py
│   └── services/           # 비즈니스 로직
│       ├── __init__.py
│       └── quiz_generator.py
├── main.py                 # 메인 실행 파일
├── test_client.py          # 테스트 클라이언트
├── pyproject.toml          # 프로젝트 설정
├── .env                    # 환경 변수
└── README.md
```

## 개발 정보

- **언어**: Python 3.10+
- **프레임워크**: FastAPI
- **LLM**: Google Gemini 2.5 Flash Preview
- **패키지 관리**: uv
- **의존성**: langchain, langchain-google-genai, pydantic

## 라이선스

MIT License