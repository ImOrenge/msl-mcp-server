import pytest
from fastapi.testclient import TestClient
from src.server.msl_mcp_server import MSLMCPServer
from src.server.resources import VoiceCommand
from datetime import datetime
import json

@pytest.fixture
def app():
    server = MSLMCPServer()
    return server.app

@pytest.fixture
def client(app):
    return TestClient(app)

def test_create_voice_command(client):
    command = {
        "command_id": "test-1",
        "text": "메모장 창 열기",
        "language": "ko",
        "confidence": 0.95,
        "timestamp": datetime.now().isoformat(),
        "metadata": {}
    }
    
    response = client.post("/voice-command", json=command)
    assert response.status_code == 200
    assert response.json()["success"] == True

def test_get_voice_command(client):
    # 명령 생성
    command = {
        "command_id": "test-2",
        "text": "계산기 실행",
        "language": "ko",
        "confidence": 0.95,
        "timestamp": datetime.now().isoformat(),
        "metadata": {}
    }
    client.post("/voice-command", json=command)
    
    # 명령 조회
    response = client.get("/voice-command/test-2")
    assert response.status_code == 200
    data = response.json()
    assert data["command_id"] == "test-2"
    assert data["text"] == "계산기 실행"

def test_invalid_voice_command(client):
    # 잘못된 명령 형식
    command = {
        "command_id": "test-3",
        "text": ""  # 빈 텍스트
    }
    
    response = client.post("/voice-command", json=command)
    assert response.status_code == 422  # Validation Error

@pytest.mark.asyncio
async def test_websocket_voice_command(app):
    server = MSLMCPServer()
    
    with TestClient(app) as client:
        with client.websocket_connect("/ws/test-session") as websocket:
            # 연결 확인 메시지 수신
            websocket.receive_json()
            
            # 음성 명령 전송
            command = {
                "jsonrpc": "2.0",
                "method": "process_voice_command",
                "params": {
                    "command_id": "test-4",
                    "text": "브라우저 실행",
                    "language": "ko",
                    "confidence": 0.95
                },
                "id": 1
            }
            websocket.send_json(command)
            
            # 응답 확인
            response = websocket.receive_json()
            assert response["jsonrpc"] == "2.0"
            assert response["id"] == 1
            assert "result" in response

@pytest.mark.asyncio
async def test_windows_automation(app):
    server = MSLMCPServer()
    
    with TestClient(app) as client:
        with client.websocket_connect("/ws/test-session") as websocket:
            # 연결 확인 메시지 수신
            websocket.receive_json()
            
            # Windows 자동화 명령 전송
            command = {
                "jsonrpc": "2.0",
                "method": "execute_automation",
                "params": {
                    "action_type": "window",
                    "parameters": {
                        "operation": "open",
                        "title": "메모장"
                    }
                },
                "id": 1
            }
            websocket.send_json(command)
            
            # 응답 확인
            response = websocket.receive_json()
            assert response["jsonrpc"] == "2.0"
            assert response["id"] == 1
            assert "result" in response
            assert response["result"]["success"] == True

def test_prompt_template(client):
    # 프롬프트 템플릿 생성
    template = {
        "template_id": "test-template",
        "template": "{{program}} {{action}}",
        "parameters": ["program", "action"],
        "description": "프로그램 실행 템플릿"
    }
    
    response = client.post("/prompt-template", json=template)
    assert response.status_code == 200
    
    # 템플릿 조회
    response = client.get("/prompt-template/test-template")
    assert response.status_code == 200
    data = response.json()
    assert data["template_id"] == "test-template"
    assert data["parameters"] == ["program", "action"]

@pytest.mark.asyncio
async def test_session_state_tracking(app):
    server = MSLMCPServer()
    
    with TestClient(app) as client:
        with client.websocket_connect("/ws/test-session") as websocket:
            # 연결 확인 메시지 수신
            websocket.receive_json()
            
            # 상태 조회 요청
            request = {
                "jsonrpc": "2.0",
                "method": "get_session_state",
                "params": {},
                "id": 1
            }
            websocket.send_json(request)
            
            # 응답 확인
            response = websocket.receive_json()
            assert response["jsonrpc"] == "2.0"
            assert response["id"] == 1
            assert "result" in response
            assert "session_id" in response["result"]
            assert "commands" in response["result"]

@pytest.mark.asyncio
async def test_error_handling_and_recovery(app):
    server = MSLMCPServer()
    
    with TestClient(app) as client:
        with client.websocket_connect("/ws/test-session") as websocket:
            # 연결 확인 메시지 수신
            websocket.receive_json()
            
            # 잘못된 Windows 자동화 명령 전송
            command = {
                "jsonrpc": "2.0",
                "method": "execute_automation",
                "params": {
                    "action_type": "invalid_type",
                    "parameters": {}
                },
                "id": 1
            }
            websocket.send_json(command)
            
            # 에러 응답 확인
            response = websocket.receive_json()
            assert response["jsonrpc"] == "2.0"
            assert response["id"] == 1
            assert "error" in response
            assert "code" in response["error"]
            assert "message" in response["error"]
            
            # 정상 명령으로 복구
            command = {
                "jsonrpc": "2.0",
                "method": "execute_automation",
                "params": {
                    "action_type": "window",
                    "parameters": {
                        "operation": "open",
                        "title": "메모장"
                    }
                },
                "id": 2
            }
            websocket.send_json(command)
            
            # 정상 응답 확인
            response = websocket.receive_json()
            assert response["jsonrpc"] == "2.0"
            assert response["id"] == 2
            assert "result" in response
            assert response["result"]["success"] == True

@pytest.mark.asyncio
async def test_concurrent_command_processing(app):
    server = MSLMCPServer()
    
    with TestClient(app) as client:
        with client.websocket_connect("/ws/test-session") as websocket:
            # 연결 확인 메시지 수신
            websocket.receive_json()
            
            # 여러 명령 동시 전송
            commands = []
            for i in range(5):
                command = {
                    "jsonrpc": "2.0",
                    "method": "process_voice_command",
                    "params": {
                        "command_id": f"test-concurrent-{i}",
                        "text": f"테스트 명령 {i}",
                        "language": "ko",
                        "confidence": 0.95
                    },
                    "id": i + 1
                }
                commands.append(command)
                websocket.send_json(command)
            
            # 모든 응답 수신 및 확인
            responses = []
            for _ in range(len(commands)):
                response = websocket.receive_json()
                responses.append(response)
            
            # 응답 검증
            assert len(responses) == len(commands)
            for i, response in enumerate(responses):
                assert response["jsonrpc"] == "2.0"
                assert response["id"] == i + 1
                assert "result" in response 