from typing import Dict, List, Optional, Any
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
import json
import logging
from datetime import datetime

class MCPContext(BaseModel):
    """MCP 컨텍스트 모델"""
    session_id: str
    user_id: Optional[str] = None
    language: str = "ko"
    timestamp: datetime = datetime.now()
    metadata: Dict[str, Any] = {}

class FastMCP:
    """FastMCP 서버 기본 클래스"""
    def __init__(self):
        self.app = FastAPI(title="MSL MCP Server")
        self.active_connections: Dict[str, WebSocket] = {}
        self.contexts: Dict[str, MCPContext] = {}
        
        # CORS 설정
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # 기본 라우트 설정
        self.setup_routes()
        
        # 로깅 설정
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger("FastMCP")

    def setup_routes(self):
        """기본 라우트 설정"""
        @self.app.get("/")
        async def root():
            return {"status": "ok", "message": "MSL MCP Server is running"}

        @self.app.websocket("/ws/{client_id}")
        async def websocket_endpoint(websocket: WebSocket, client_id: str):
            await self.handle_websocket_connection(websocket, client_id)

    async def handle_websocket_connection(self, websocket: WebSocket, client_id: str):
        """WebSocket 연결 처리"""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        
        # 컨텍스트 생성
        self.contexts[client_id] = MCPContext(
            session_id=client_id,
            timestamp=datetime.now()
        )
        
        try:
            while True:
                data = await websocket.receive_text()
                await self.handle_message(client_id, data)
        except WebSocketDisconnect:
            self.handle_disconnect(client_id)
        except Exception as e:
            self.logger.error(f"Error in WebSocket connection: {str(e)}")
            self.handle_disconnect(client_id)

    async def handle_message(self, client_id: str, message: str):
        """메시지 처리"""
        try:
            data = json.loads(message)
            # JSON-RPC 2.0 형식 검증
            if "jsonrpc" not in data or data["jsonrpc"] != "2.0":
                await self.send_error(client_id, -32600, "Invalid Request")
                return
            
            # 메시지 처리 로직
            response = await self.process_message(client_id, data)
            await self.send_response(client_id, response)
            
        except json.JSONDecodeError:
            await self.send_error(client_id, -32700, "Parse error")
        except Exception as e:
            self.logger.error(f"Error processing message: {str(e)}")
            await self.send_error(client_id, -32603, "Internal error")

    async def process_message(self, client_id: str, data: Dict):
        """메시지 처리 로직"""
        # 이 메서드는 하위 클래스에서 구현됩니다
        pass

    async def send_response(self, client_id: str, response: Dict):
        """응답 전송"""
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_text(json.dumps(response))

    async def send_error(self, client_id: str, code: int, message: str):
        """에러 응답 전송"""
        error_response = {
            "jsonrpc": "2.0",
            "error": {
                "code": code,
                "message": message
            },
            "id": None
        }
        await self.send_response(client_id, error_response)

    def handle_disconnect(self, client_id: str):
        """연결 종료 처리"""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
        if client_id in self.contexts:
            del self.contexts[client_id]
        self.logger.info(f"Client {client_id} disconnected")

    def get_app(self) -> FastAPI:
        """FastAPI 애플리케이션 반환"""
        return self.app 