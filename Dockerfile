# Quiz LLM API Dockerfile
# Python 3.11 slim 이미지 사용 (더 가볍고 빠름)
FROM python:3.11-slim

# 메타데이터 설정
LABEL maintainer="Quiz LLM API Team"
LABEL description="LLM-based quiz generation API for children's economic education"
LABEL version="0.1.0"

# 환경 변수 설정
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 시스템 의존성 설치 (필요한 최소한의 패키지만)
RUN apt-get update && apt-get install -y \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 작업 디렉토리 설정
WORKDIR /app

# uv 설치 (Python 패키지 관리자)
RUN pip install uv

# 의존성 파일들 먼저 복사 (Docker 레이어 캐싱 최적화)
COPY pyproject.toml uv.lock* ./

# 의존성 설치
RUN uv sync --frozen

# 애플리케이션 소스 코드 복사
COPY . .

# 비루트 사용자 생성 및 권한 설정 (보안)
RUN groupadd -r appuser && useradd -r -g appuser -m appuser
RUN chown -R appuser:appuser /app
USER appuser

# 포트 노출
EXPOSE 8000

# 헬스체크 설정
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/docs || exit 1

# 애플리케이션 실행
CMD ["uv", "run", "python", "main.py"]
