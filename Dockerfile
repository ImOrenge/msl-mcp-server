# 기본 이미지로 Python 3.8 사용
FROM python:3.8-slim

# 작업 디렉토리 설정
WORKDIR /app

# Poetry 설치
RUN pip install poetry

# Poetry 가상 환경 비활성화 (Docker 내부에서는 불필요)
RUN poetry config virtualenvs.create false

# 프로젝트 파일 복사
COPY pyproject.toml poetry.lock ./
COPY src/ ./src/
COPY README.md ./

# 의존성 설치
RUN poetry install --no-dev

# 환경 변수 설정
ENV MSL_MCP_HOST=0.0.0.0
ENV MSL_MCP_PORT=8000
ENV MSL_MCP_LOG_LEVEL=info

# 포트 노출
EXPOSE 8000

# 서버 실행
CMD ["poetry", "run", "python", "src/main.py"] 