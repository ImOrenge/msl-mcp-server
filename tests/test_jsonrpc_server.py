"""
JSON-RPC 서버 테스트
"""
import pytest
from fastapi.testclient import TestClient
from run_jsonrpc_server import app

client = TestClient(app)

def test_jsonrpc_invalid_request():
    """잘못된 JSON-RPC 요청 테스트"""
    response = client.post("/mcp", json={})
    assert response.status_code == 200
    data = response.json()
    assert data["jsonrpc"] == "2.0"
    assert data["error"]["code"] == -32600
    assert "Invalid Request" in data["error"]["message"]

def test_jsonrpc_parse_method():
    """msl.parse 메서드 테스트"""
    request = {
        "jsonrpc": "2.0",
        "method": "msl.parse",
        "params": {
            "code": "click 100 200\ntype Hello World"
        },
        "id": 1
    }
    response = client.post("/mcp", json=request)
    assert response.status_code == 200
    data = response.json()
    
    assert data["jsonrpc"] == "2.0"
    assert data["id"] == 1
    assert "result" in data
    assert data["result"]["type"] == "program"
    assert len(data["result"]["body"]) == 2

def test_jsonrpc_parse_method_missing_code():
    """msl.parse 메서드 - code 파라미터 누락 테스트"""
    request = {
        "jsonrpc": "2.0",
        "method": "msl.parse",
        "params": {},
        "id": 1
    }
    response = client.post("/mcp", json=request)
    assert response.status_code == 200
    data = response.json()
    
    assert data["jsonrpc"] == "2.0"
    assert data["id"] == 1
    assert "error" in data
    assert data["error"]["code"] == -32602
    assert "code' is required" in data["error"]["message"]

def test_jsonrpc_execute_method():
    """msl.execute 메서드 테스트"""
    request = {
        "jsonrpc": "2.0",
        "method": "msl.execute",
        "params": {
            "ast": {
                "type": "program",
                "body": [{
                    "type": "command",
                    "name": "click",
                    "params": ["100", "200"]
                }]
            }
        },
        "id": 1
    }
    response = client.post("/mcp", json=request)
    assert response.status_code == 200
    data = response.json()
    
    assert data["jsonrpc"] == "2.0"
    assert data["id"] == 1
    assert "result" in data
    assert data["result"]["success"] is True

def test_jsonrpc_execute_method_missing_ast():
    """msl.execute 메서드 - ast 파라미터 누락 테스트"""
    request = {
        "jsonrpc": "2.0",
        "method": "msl.execute",
        "params": {},
        "id": 1
    }
    response = client.post("/mcp", json=request)
    assert response.status_code == 200
    data = response.json()
    
    assert data["jsonrpc"] == "2.0"
    assert data["id"] == 1
    assert "error" in data
    assert data["error"]["code"] == -32602
    assert "ast' is required" in data["error"]["message"]

def test_jsonrpc_method_not_found():
    """존재하지 않는 메서드 테스트"""
    request = {
        "jsonrpc": "2.0",
        "method": "unknown.method",
        "params": {},
        "id": 1
    }
    response = client.post("/mcp", json=request)
    assert response.status_code == 200
    data = response.json()
    
    assert data["jsonrpc"] == "2.0"
    assert data["id"] == 1
    assert "error" in data
    assert data["error"]["code"] == -32601
    assert "Method not found" in data["error"]["message"]

def test_jsonrpc_parse_and_execute():
    """파싱 후 실행 통합 테스트"""
    # 1. 먼저 코드 파싱
    parse_request = {
        "jsonrpc": "2.0",
        "method": "msl.parse",
        "params": {
            "code": "click 100 200\nwait 1"
        },
        "id": 1
    }
    response = client.post("/mcp", json=parse_request)
    assert response.status_code == 200
    parse_data = response.json()
    assert "result" in parse_data
    
    # 2. 파싱된 AST로 실행
    execute_request = {
        "jsonrpc": "2.0",
        "method": "msl.execute",
        "params": {
            "ast": parse_data["result"]
        },
        "id": 2
    }
    response = client.post("/mcp", json=execute_request)
    assert response.status_code == 200
    execute_data = response.json()
    
    assert execute_data["jsonrpc"] == "2.0"
    assert execute_data["id"] == 2
    assert "result" in execute_data
    assert execute_data["result"]["success"] is True 