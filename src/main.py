import uvicorn
from server.msl_mcp_server import MSLMCPServer
import logging

def main():
    # 로깅 설정
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger("MSL-MCP")
    
    # 서버 인스턴스 생성
    server = MSLMCPServer()
    
    # 서버 설정
    host = "0.0.0.0"
    port = 8000
    
    # 시작 메시지
    logger.info(f"Starting MSL MCP Server on {host}:{port}")
    
    # 서버 실행
    uvicorn.run(
        server.get_app(),
        host=host,
        port=port,
        log_level="info"
    )

if __name__ == "__main__":
    main() 