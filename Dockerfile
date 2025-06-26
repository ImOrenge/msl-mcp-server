# 기본 이미지로 Python 3.11 사용
FROM python:3.11-slim

# 작업 디렉토리 설정
WORKDIR /app

# Poetry 설치
RUN pip install poetry

# 프로젝트 파일 복사
COPY pyproject.toml poetry.lock* ./
COPY README.md ./
COPY src ./src

# 의존성 설치
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

# 환경 변수 설정
ENV MSL_MCP_HOST=0.0.0.0
ENV MSL_MCP_PORT=8000
ENV MSL_MCP_LOG_LEVEL=info

# 포트 노출
EXPOSE 8000

# 서버 실행
CMD ["python", "src/main.py"] 