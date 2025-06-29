# MSL MCP Server Dockerfile
FROM python:3.11-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 업데이트 및 필요한 패키지 설치
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python 패키지 요구사항 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# 환경변수 설정
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# 기본 포트 노출 (MCP는 주로 stdio를 사용하지만 HTTP 서버 모드용)
EXPOSE 8000

# 헬스체크 추가
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# 기본 명령어 설정
CMD ["python", "server.py"]

# 라벨 추가
LABEL maintainer="MSL MCP Server"
LABEL version="1.0.0"
LABEL description="MSL (Macro Scripting Language) MCP Server with OpenAI Integration" 