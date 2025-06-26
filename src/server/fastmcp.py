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
            allow_headers=["*"]
        )
        
        # 기본 라우트 설정
        self.setup_routes()
    
    def setup_routes(self):
        """기본 라우트 설정"""
        @self.app.get("/health")
        async def health_check():
            return {"status": "ok", "timestamp": datetime.now().isoformat()}
        
        @self.app.websocket("/ws/{session_id}")
        async def websocket_endpoint(websocket: WebSocket, session_id: str):
            await self.connect(websocket, session_id)
            try:
                while True:
                    data = await websocket.receive_json()
                    await self.handle_websocket_message(websocket, session_id, data)
            except WebSocketDisconnect:
                await self.disconnect(session_id)
    
    async def connect(self, websocket: WebSocket, session_id: str):
        """WebSocket 연결 처리"""
        await websocket.accept()
        self.active_connections[session_id] = websocket
        self.contexts[session_id] = MCPContext(session_id=session_id)
    
    async def disconnect(self, session_id: str):
        """WebSocket 연결 해제 처리"""
        if session_id in self.active_connections:
            del self.active_connections[session_id]
        if session_id in self.contexts:
            del self.contexts[session_id]
    
    async def handle_websocket_message(self, websocket: WebSocket, session_id: str, data: Dict):
        """WebSocket 메시지 처리"""
        try:
            if not isinstance(data, dict) or "jsonrpc" not in data:
                await self.send_error(websocket, -32600, "Invalid Request", None)
                return
            
            method = data.get("method")
            params = data.get("params", {})
            request_id = data.get("id")
            
            if not method:
                await self.send_error(websocket, -32600, "Method not specified", request_id)
                return
            
            result = await self.handle_rpc_method(session_id, method, params)
            await self.send_result(websocket, result, request_id)
            
        except Exception as e:
            await self.send_error(websocket, -32603, str(e), data.get("id"))
    
    async def handle_rpc_method(self, session_id: str, method: str, params: Dict) -> Any:
        """RPC 메소드 처리"""
        raise NotImplementedError("Subclasses must implement handle_rpc_method")
    
    async def send_result(self, websocket: WebSocket, result: Any, request_id: Any):
        """결과 전송"""
        await websocket.send_json({
            "jsonrpc": "2.0",
            "result": result,
            "id": request_id
        })
    
    async def send_error(self, websocket: WebSocket, code: int, message: str, request_id: Any):
        """에러 전송"""
        await websocket.send_json({
            "jsonrpc": "2.0",
            "error": {
                "code": code,
                "message": message
            },
            "id": request_id
        })
    
    def get_app(self) -> FastAPI:
        """FastAPI 앱 반환"""
        return self.app 