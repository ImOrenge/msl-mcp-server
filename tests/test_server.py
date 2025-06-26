import pytest
from fastapi.testclient import TestClient
from src.server.app import app
from src.msl.interpreter import MSLInterpreter
from src.msl.generator import MSLGenerator
from src.prompt.analyzer import IntentAnalyzer

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_voice_command():
    # 음성 명령 테스트
    response = client.post(
        "/api/voice",
        json={"text": "100, 200 클릭해줘"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "script" in data
    assert data["script"] == "click(100, 200)"

def test_invalid_voice_command():
    # 잘못된 음성 명령 테스트
    response = client.post(
        "/api/voice",
        json={"text": "잘못된 명령"}
    )
    assert response.status_code == 400
    assert "error" in response.json()

def test_script_execution():
    # 스크립트 실행 테스트
    response = client.post(
        "/api/script",
        json={"script": "click(100, 200)"}
    )
    assert response.status_code == 200
    assert response.json() == {"status": "success"}

def test_invalid_script():
    # 잘못된 스크립트 테스트
    response = client.post(
        "/api/script",
        json={"script": "invalid_command()"}
    )
    assert response.status_code == 400
    assert "error" in response.json()

def test_stop_execution():
    # 실행 중지 테스트
    response = client.post("/api/stop")
    assert response.status_code == 200
    assert response.json() == {"status": "stopped"}

@pytest.mark.asyncio
async def test_websocket_connection():
    # WebSocket 연결 테스트
    with client.websocket_connect("/ws") as websocket:
        # 음성 명령 전송
        await websocket.send_json({
            "type": "voice",
            "text": "100, 200 클릭해줘"
        })
        
        # 응답 확인
        response = await websocket.receive_json()
        assert response["type"] == "script"
        assert response["script"] == "click(100, 200)"
        
        # 스크립트 실행 결과 확인
        response = await websocket.receive_json()
        assert response["type"] == "result"
        assert response["status"] == "success"

@pytest.mark.asyncio
async def test_websocket_invalid_command():
    # 잘못된 명령 테스트
    with client.websocket_connect("/ws") as websocket:
        await websocket.send_json({
            "type": "voice",
            "text": "잘못된 명령"
        })
        
        response = await websocket.receive_json()
        assert response["type"] == "error"
        assert "error" in response

@pytest.mark.asyncio
async def test_websocket_stop():
    # 실행 중지 테스트
    with client.websocket_connect("/ws") as websocket:
        await websocket.send_json({"type": "stop"})
        
        response = await websocket.receive_json()
        assert response["type"] == "result"
        assert response["status"] == "stopped"

def test_concurrent_connections():
    # 동시 연결 테스트
    with client.websocket_connect("/ws") as ws1:
        with client.websocket_connect("/ws") as ws2:
            # 두 연결 모두 활성 상태 확인
            assert ws1._client is not None
            assert ws2._client is not None 