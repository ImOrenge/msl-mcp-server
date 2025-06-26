import uvicorn
import argparse
import logging
from pathlib import Path

def main():
    # 로깅 설정
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)

    # 명령행 인자 파싱
    parser = argparse.ArgumentParser(description='MSL-MCP-Server 실행')
    parser.add_argument('--host', default='127.0.0.1', help='서버 호스트 (기본값: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=8000, help='서버 포트 (기본값: 8000)')
    parser.add_argument('--reload', action='store_true', help='자동 리로드 활성화')
    parser.add_argument('--workers', type=int, default=1, help='워커 프로세스 수 (기본값: 1)')
    args = parser.parse_args()

    # 프로젝트 루트 디렉토리 설정
    project_root = Path(__file__).parent
    import sys
    sys.path.append(str(project_root))

    try:
        # 서버 실행
        logger.info(f"Starting server on {args.host}:{args.port}")
        uvicorn.run(
            "src.server.app:app",
            host=args.host,
            port=args.port,
            reload=args.reload,
            workers=args.workers,
            log_level="info"
        )
    except Exception as e:
        logger.error(f"Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 