import uvicorn
import logging
import os
import json
from server.msl_mcp_server import MSLMCPServer
from server.fastmcp import MCPConfig

def load_config() -> MCPConfig:
    """Smithery 설정 로드"""
    config_path = os.environ.get("SMITHERY_CONFIG", "config.json")
    if os.path.exists(config_path):
        with open(config_path) as f:
            config_data = json.load(f)
            return MCPConfig(**config_data)
    return MCPConfig()

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 서버 인스턴스 생성
config = load_config()
server = MSLMCPServer(config=config)
app = server.get_app()

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level=config.logLevel.lower()
    ) 