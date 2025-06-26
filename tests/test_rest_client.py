import pytest
from fastapi.testclient import TestClient
from src.server.app import app

client = TestClient(app)

def test_health_check():
    """상태 확인 엔드포인트 테스트"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_voice_command_success():
    """음성 명령 처리 성공 테스트"""
    response = client.post(
        "/api/voice",
        json={"text": "100, 200 클릭해줘"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "script" in data
    assert data["script"] == "click(100, 200)"

def test_voice_command_failure():
    """음성 명령 처리 실패 테스트"""
    response = client.post(
        "/api/voice",
        json={"text": "이해할 수 없는 명령"}
    )
    assert response.status_code == 400
    data = response.json()
    assert "error" in data
    assert "Failed to analyze command" in data["error"]

def test_script_execution_success():
    """스크립트 실행 성공 테스트"""
    response = client.post(
        "/api/script",
        json={"script": "click(100, 200)"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"

def test_script_execution_failure():
    """스크립트 실행 실패 테스트"""
    response = client.post(
        "/api/script",
        json={"script": "invalid_command()"}
    )
    assert response.status_code == 400
    data = response.json()
    assert "error" in data
    assert "Failed to execute script" in data["error"]

def test_stop_execution():
    """실행 중지 테스트"""
    response = client.post("/api/stop")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "stopped"

def test_invalid_request_body():
    """잘못된 요청 본문 테스트"""
    response = client.post(
        "/api/voice",
        json={"invalid": "format"}
    )
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data

def test_missing_required_field():
    """필수 필드 누락 테스트"""
    response = client.post(
        "/api/voice",
        json={}
    )
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data

def test_method_not_allowed():
    """허용되지 않은 메서드 테스트"""
    response = client.get("/api/voice")
    assert response.status_code == 405

def test_concurrent_requests():
    """동시 요청 테스트"""
    import concurrent.futures
    import time

    def make_request():
        return client.post(
            "/api/voice",
            json={"text": "100, 200 클릭해줘"}
        )

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(make_request) for _ in range(5)]
        responses = [f.result() for f in futures]

    for response in responses:
        assert response.status_code == 200
        data = response.json()
        assert "script" in data
        assert data["script"] == "click(100, 200)" 