import pytest
from fastapi.testclient import TestClient
from src.server.fastmcp import FastMCP, MCPContext
import json
from datetime import datetime

@pytest.fixture
def app():
    server = FastMCP()
    return server.app

@pytest.fixture
def client(app):
    return TestClient(app)

def test_create_context():
    context = MCPContext(
        session_id="test-session",
        user_id="test-user",
        language="ko"
    )
    
    assert context.session_id == "test-session"
    assert context.user_id == "test-user"
    assert context.language == "ko"
    assert isinstance(context.timestamp, datetime)
    assert isinstance(context.metadata, dict)

def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

@pytest.mark.asyncio
async def test_websocket_connection(app):
    server = FastMCP()
    
    with TestClient(app) as client:
        with client.websocket_connect("/ws/test-session") as websocket:
            data = websocket.receive_json()
            assert data["type"] == "connection_established"
            assert "session_id" in data

@pytest.mark.asyncio
async def test_websocket_message(app):
    server = FastMCP()
    
    with TestClient(app) as client:
        with client.websocket_connect("/ws/test-session") as websocket:
            # 연결 확인 메시지 수신
            data = websocket.receive_json()
            
            # 테스트 메시지 전송
            test_message = {
                "jsonrpc": "2.0",
                "method": "echo",
                "params": {"message": "Hello, World!"},
                "id": 1
            }
            websocket.send_json(test_message)
            
            # 응답 확인
            response = websocket.receive_json()
            assert response["jsonrpc"] == "2.0"
            assert response["id"] == 1
            assert "result" in response

@pytest.mark.asyncio
async def test_multiple_websocket_connections(app):
    server = FastMCP()
    
    with TestClient(app) as client:
        # 여러 WebSocket 연결 생성
        connections = []
        for i in range(3):
            ws = client.websocket_connect(f"/ws/session-{i}")
            connections.append(ws)
        
        # 각 연결에서 초기 메시지 수신
        for ws in connections:
            with ws as websocket:
                data = websocket.receive_json()
                assert data["type"] == "connection_established"

def test_invalid_websocket_session(client):
    with pytest.raises(Exception):
        with client.websocket_connect("/ws/"):
            pass

def test_cors_headers(client):
    response = client.options("/health")
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers
    assert response.headers["access-control-allow-origin"] == "*"

@pytest.mark.asyncio
async def test_context_management(app):
    server = FastMCP()
    
    # 컨텍스트 생성
    context = MCPContext(
        session_id="test-session",
        user_id="test-user",
        language="ko"
    )
    
    # 컨텍스트 저장
    server.contexts[context.session_id] = context
    
    with TestClient(app) as client:
        with client.websocket_connect("/ws/test-session") as websocket:
            # 연결 확인
            data = websocket.receive_json()
            assert data["type"] == "connection_established"
            assert data["session_id"] == "test-session"
            
            # 컨텍스트 정보 요청
            request = {
                "jsonrpc": "2.0",
                "method": "get_context",
                "params": {},
                "id": 1
            }
            websocket.send_json(request)
            
            # 응답 확인
            response = websocket.receive_json()
            assert response["jsonrpc"] == "2.0"
            assert response["id"] == 1
            assert response["result"]["session_id"] == "test-session"
            assert response["result"]["user_id"] == "test-user"
            assert response["result"]["language"] == "ko"

@pytest.mark.asyncio
async def test_error_handling(app):
    server = FastMCP()
    
    with TestClient(app) as client:
        with client.websocket_connect("/ws/test-session") as websocket:
            # 연결 확인 메시지 수신
            websocket.receive_json()
            
            # 잘못된 요청 전송
            invalid_request = {
                "jsonrpc": "2.0",
                "method": "invalid_method",
                "params": {},
                "id": 1
            }
            websocket.send_json(invalid_request)
            
            # 에러 응답 확인
            response = websocket.receive_json()
            assert response["jsonrpc"] == "2.0"
            assert response["id"] == 1
            assert "error" in response
            assert response["error"]["code"] < 0
            assert "message" in response["error"]

@pytest.mark.asyncio
async def test_notification_handling(app):
    server = FastMCP()
    
    with TestClient(app) as client:
        with client.websocket_connect("/ws/test-session") as websocket:
            # 연결 확인 메시지 수신
            websocket.receive_json()
            
            # 알림 메시지 전송 (id 없음)
            notification = {
                "jsonrpc": "2.0",
                "method": "notify",
                "params": {"message": "test notification"}
            }
            websocket.send_json(notification)
            
            # 알림은 응답이 없어야 함
            with pytest.raises(Exception):
                websocket.receive_json(timeout=1.0)

@pytest.mark.asyncio
async def test_batch_request(app):
    server = FastMCP()
    
    with TestClient(app) as client:
        with client.websocket_connect("/ws/test-session") as websocket:
            # 연결 확인 메시지 수신
            websocket.receive_json()
            
            # 배치 요청 전송
            batch_request = [
                {
                    "jsonrpc": "2.0",
                    "method": "echo",
                    "params": {"message": "first"},
                    "id": 1
                },
                {
                    "jsonrpc": "2.0",
                    "method": "echo",
                    "params": {"message": "second"},
                    "id": 2
                }
            ]
            websocket.send_json(batch_request)
            
            # 배치 응답 확인
            response = websocket.receive_json()
            assert isinstance(response, list)
            assert len(response) == 2
            assert all(r["jsonrpc"] == "2.0" for r in response)
            assert response[0]["id"] == 1
            assert response[1]["id"] == 2 