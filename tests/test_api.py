import pytest
from fastapi.testclient import TestClient
from src.server.app import app

client = TestClient(app)

def test_health_check():
    """상태 확인 엔드포인트 테스트"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_voice_command_success(mock_analyzer, mock_generator):
    """음성 명령 처리 성공 테스트"""
    response = client.post(
        "/api/voice",
        json={"text": "100, 200 클릭해줘"}
    )
    assert response.status_code == 200
    assert response.json() == {"script": "click(100, 200)"}

def test_voice_command_failure(mock_analyzer):
    """음성 명령 처리 실패 테스트"""
    response = client.post(
        "/api/voice",
        json={"text": "잘못된 명령"}
    )
    assert response.status_code == 400
    assert "Failed to analyze command" in response.json()["detail"]

def test_script_execution_success(mock_interpreter):
    """스크립트 실행 성공 테스트"""
    response = client.post(
        "/api/script",
        json={"script": "click(100, 200)"}
    )
    assert response.status_code == 200
    assert response.json() == {"status": "success"}

def test_script_execution_failure(mock_interpreter):
    """스크립트 실행 실패 테스트"""
    # mock_interpreter가 False를 반환하도록 설정
    mock_interpreter.execute.return_value = False
    
    response = client.post(
        "/api/script",
        json={"script": "invalid_script"}
    )
    assert response.status_code == 400
    assert "error" in response.json()["detail"].lower()

def test_stop_execution():
    """실행 중지 테스트"""
    response = client.post("/api/stop")
    assert response.status_code == 200
    assert response.json() == {"status": "stopped"}

def test_invalid_voice_command_format():
    """잘못된 음성 명령 형식 테스트"""
    response = client.post(
        "/api/voice",
        json={"invalid": "format"}
    )
    assert response.status_code == 422  # Validation Error

def test_invalid_script_format():
    """잘못된 스크립트 형식 테스트"""
    response = client.post(
        "/api/script",
        json={"invalid": "format"}
    )
    assert response.status_code == 422  # Validation Error

def test_missing_text_in_voice_command():
    """음성 명령에서 텍스트 누락 테스트"""
    response = client.post(
        "/api/voice",
        json={}
    )
    assert response.status_code == 422  # Validation Error

def test_missing_script_in_script_command():
    """스크립트 명령에서 스크립트 누락 테스트"""
    response = client.post(
        "/api/script",
        json={}
    )
    assert response.status_code == 422  # Validation Error 