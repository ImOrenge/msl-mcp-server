import uvicorn
import logging
from server.msl_mcp_server import MSLMCPServer

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 서버 인스턴스 생성
server = MSLMCPServer()
app = server.get_app()

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 