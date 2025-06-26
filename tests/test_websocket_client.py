import pytest
import asyncio
import json
from fastapi.testclient import TestClient
from fastapi.websockets import WebSocket
from src.server.app import app

@pytest.mark.asyncio
async def test_websocket_connection():
    """WebSocket 연결 테스트"""
    client = TestClient(app)
    with client.websocket_connect("/ws") as websocket:
        # 연결 확인
        assert websocket.can_receive()

@pytest.mark.asyncio
async def test_websocket_voice_command():
    """음성 명령 WebSocket 테스트"""
    client = TestClient(app)
    with client.websocket_connect("/ws") as websocket:
        # 음성 명령 전송
        websocket.send_json({
            "type": "voice",
            "text": "100, 200 클릭해줘"
        })

        # 스크립트 응답 확인
        response = websocket.receive_json()
        assert response["type"] == "script"
        assert response["script"] == "click(100, 200)"

        # 실행 결과 확인
        response = websocket.receive_json()
        assert response["type"] == "result"
        assert response["status"] == "success"

@pytest.mark.asyncio
async def test_websocket_script_command():
    """스크립트 명령 WebSocket 테스트"""
    client = TestClient(app)
    with client.websocket_connect("/ws") as websocket:
        # 스크립트 직접 전송
        websocket.send_json({
            "type": "script",
            "script": "click(100, 200)"
        })

        # 실행 결과 확인
        response = websocket.receive_json()
        assert response["type"] == "result"
        assert response["status"] == "success"

@pytest.mark.asyncio
async def test_websocket_invalid_command():
    """잘못된 명령 WebSocket 테스트"""
    client = TestClient(app)
    with client.websocket_connect("/ws") as websocket:
        # 잘못된 명령 전송
        websocket.send_json({
            "type": "voice",
            "text": "이해할 수 없는 명령"
        })

        # 오류 응답 확인
        response = websocket.receive_json()
        assert response["type"] == "error"
        assert "Failed to analyze command" in response["message"]

@pytest.mark.asyncio
async def test_websocket_invalid_message_format():
    """잘못된 메시지 형식 WebSocket 테스트"""
    client = TestClient(app)
    with client.websocket_connect("/ws") as websocket:
        # 잘못된 형식의 메시지 전송
        websocket.send_json({
            "invalid": "format"
        })

        # 오류 응답 확인
        response = websocket.receive_json()
        assert response["type"] == "error"
        assert "Invalid message format" in response["message"]

@pytest.mark.asyncio
async def test_websocket_stop_command():
    """중지 명령 WebSocket 테스트"""
    client = TestClient(app)
    with client.websocket_connect("/ws") as websocket:
        # 중지 명령 전송
        websocket.send_json({
            "type": "stop"
        })

        # 응답 확인
        response = websocket.receive_json()
        assert response["type"] == "result"
        assert response["status"] == "stopped" 