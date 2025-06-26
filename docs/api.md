# MSL MCP Server API 문서

## WebSocket API

### 연결

WebSocket 엔드포인트: `ws://localhost:8000/ws/{session_id}`

- `session_id`: 세션 식별자 (문자열)

### JSON-RPC 2.0 메시지 형식

모든 WebSocket 통신은 JSON-RPC 2.0 프로토콜을 따릅니다.

#### 요청 형식
```json
{
    "jsonrpc": "2.0",
    "method": "method_name",
    "params": {},
    "id": 1
}
```

#### 응답 형식
```json
{
    "jsonrpc": "2.0",
    "result": {},
    "id": 1
}
```

#### 에러 응답 형식
```json
{
    "jsonrpc": "2.0",
    "error": {
        "code": -32000,
        "message": "에러 메시지"
    },
    "id": 1
}
```

### 메소드

#### process_voice_command

음성 명령을 처리합니다.

요청:
```json
{
    "jsonrpc": "2.0",
    "method": "process_voice_command",
    "params": {
        "command_id": "cmd-1",
        "text": "메모장 실행",
        "language": "ko",
        "confidence": 0.95
    },
    "id": 1
}
```

응답:
```json
{
    "jsonrpc": "2.0",
    "result": {
        "success": true,
        "command_id": "cmd-1",
        "status": "completed"
    },
    "id": 1
}
```

#### execute_automation

Windows 자동화 명령을 실행합니다.

요청:
```json
{
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
```

응답:
```json
{
    "jsonrpc": "2.0",
    "result": {
        "success": true,
        "action": {
            "type": "window",
            "operation": "open",
            "target": "메모장"
        }
    },
    "id": 1
}
```

#### get_session_state

세션 상태를 조회합니다.

요청:
```json
{
    "jsonrpc": "2.0",
    "method": "get_session_state",
    "params": {},
    "id": 1
}
```

응답:
```json
{
    "jsonrpc": "2.0",
    "result": {
        "session_id": "session-1",
        "start_time": "2024-03-20T12:00:00Z",
        "last_activity": "2024-03-20T12:05:00Z",
        "commands": {
            "cmd-1": {
                "status": "completed",
                "start_time": "2024-03-20T12:01:00Z",
                "end_time": "2024-03-20T12:01:01Z"
            }
        }
    },
    "id": 1
}
```

## REST API

### 음성 명령 관리

#### POST /voice-command

새로운 음성 명령을 생성합니다.

요청:
```json
{
    "command_id": "cmd-1",
    "text": "메모장 실행",
    "language": "ko",
    "confidence": 0.95,
    "metadata": {}
}
```

응답:
```json
{
    "success": true,
    "command_id": "cmd-1"
}
```

#### GET /voice-command/{command_id}

음성 명령을 조회합니다.

응답:
```json
{
    "command_id": "cmd-1",
    "text": "메모장 실행",
    "language": "ko",
    "confidence": 0.95,
    "status": "completed",
    "created_at": "2024-03-20T12:00:00Z"
}
```

### 프롬프트 템플릿 관리

#### POST /prompt-template

새로운 프롬프트 템플릿을 생성합니다.

요청:
```json
{
    "template_id": "program-action",
    "template": "{{program}} {{action}}",
    "parameters": ["program", "action"],
    "description": "프로그램 실행 템플릿"
}
```

응답:
```json
{
    "success": true,
    "template_id": "program-action"
}
```

#### GET /prompt-template/{template_id}

프롬프트 템플릿을 조회합니다.

응답:
```json
{
    "template_id": "program-action",
    "template": "{{program}} {{action}}",
    "parameters": ["program", "action"],
    "description": "프로그램 실행 템플릿"
}
```

### 상태 관리

#### GET /health

서버 상태를 확인합니다.

응답:
```json
{
    "status": "ok",
    "version": "1.0.0",
    "timestamp": "2024-03-20T12:00:00Z"
}
```

## 에러 코드

| 코드 | 설명 |
|------|------|
| -32700 | Parse error |
| -32600 | Invalid Request |
| -32601 | Method not found |
| -32602 | Invalid params |
| -32603 | Internal error |
| -32000 | Server error |
| -32001 | Command not found |
| -32002 | Invalid command format |
| -32003 | Automation error |
| -32004 | Template not found | 