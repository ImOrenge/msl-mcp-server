import uvicorn
import os
from src.server.app import app

if __name__ == "__main__":
    # 환경 변수 설정
    host = os.getenv("MSL_SERVER_HOST", "127.0.0.1")
    port = int(os.getenv("MSL_SERVER_PORT", "8000"))
    reload = os.getenv("MSL_SERVER_RELOAD", "true").lower() == "true"
    
    # 서버 실행
    uvicorn.run(
        "src.server.app:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    ) 