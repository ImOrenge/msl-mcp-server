# MSL MCP Server Dockerfile - Smithery Compatible
FROM python:3.11-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 업데이트 및 필요한 패키지 설치
# headless 환경을 위한 virtual display 패키지 포함
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    xvfb \
    x11-utils \
    libgtk-3-0 \
    libx11-6 \
    && rm -rf /var/lib/apt/lists/*

# Headless 환경을 위한 DISPLAY 환경변수 설정
ENV DISPLAY=:99
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# pyautogui 관련 GUI 오류 방지를 위한 설정
ENV MPLBACKEND=Agg
ENV NO_AT_BRIDGE=1

# Python 패키지 요구사항 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# MSL 관련 파일 구조 확인 및 정리
RUN find /app -name "*.py" -type f -exec python -m py_compile {} \; || echo "일부 파일 컴파일 실패 (정상)"

# 기본 포트 노출 (MCP는 주로 stdio를 사용하지만 HTTP 서버 모드용)
EXPOSE 8000

# Xvfb 가상 디스플레이 시작 스크립트 생성
RUN echo '#!/bin/bash\n\
# Start Xvfb virtual display in background\n\
Xvfb :99 -screen 0 1024x768x24 -ac +extension GLX +render -noreset &\n\
export DISPLAY=:99\n\
# Wait for Xvfb to start\n\
sleep 2\n\
# Start the main application\n\
exec python server.py "$@"' > /app/start.sh && \
chmod +x /app/start.sh

# 헬스체크 추가 - GUI 관련 import 없이 기본 체크
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; import importlib; importlib.import_module('server'); sys.exit(0)" || exit 1

# 기본 명령어 설정 - Xvfb와 함께 실행
CMD ["/app/start.sh"]

# 라벨 추가
LABEL maintainer="MSL MCP Server"
LABEL version="1.0.0"
LABEL description="MSL (Macro Scripting Language) MCP Server with OpenAI Integration"
LABEL smithery.compatible="true" 