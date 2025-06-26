from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional
import json

app = FastAPI()

# JSON-RPC 메서드 저장소
rpc_methods = {}

def rpc_method(name: str):
    """JSON-RPC 메서드를 등록하기 위한 데코레이터"""
    def decorator(func):
        rpc_methods[name] = func
        return func
    return decorator

@rpc_method("echo")
async def echo(params: Dict[str, Any]) -> Dict[str, Any]:
    """테스트용 에코 메서드"""
    return params

@app.post("/jsonrpc")
async def handle_jsonrpc(request: Request) -> JSONResponse:
    """JSON-RPC 요청을 처리하는 엔드포인트"""
    try:
        # 요청 본문 파싱
        request_data = await request.json()
        
        # JSON-RPC 2.0 검증
        if request_data.get("jsonrpc") != "2.0":
            raise HTTPException(status_code=400, detail="Invalid JSON-RPC version")
        
        method = request_data.get("method")
        params = request_data.get("params", {})
        id = request_data.get("id")
        
        # 메서드 존재 여부 확인
        if method not in rpc_methods:
            return JSONResponse({
                "jsonrpc": "2.0",
                "error": {"code": -32601, "message": "Method not found"},
                "id": id
            })
        
        # 메서드 실행
        result = await rpc_methods[method](params)
        
        # 응답 반환
        return JSONResponse({
            "jsonrpc": "2.0",
            "result": result,
            "id": id
        })
        
    except json.JSONDecodeError:
        return JSONResponse({
            "jsonrpc": "2.0",
            "error": {"code": -32700, "message": "Parse error"},
            "id": None
        })
    except Exception as e:
        return JSONResponse({
            "jsonrpc": "2.0",
            "error": {"code": -32603, "message": str(e)},
            "id": None
        })

# MSL 관련 RPC 메서드들
@rpc_method("msl.parse")
async def parse_msl(params: Dict[str, Any]) -> Dict[str, Any]:
    """MSL 코드를 파싱하는 메서드"""
    code = params.get("code", "")
    # TODO: MSL 파서 구현 연동
    return {"parsed": True, "ast": {}}

@rpc_method("msl.execute")
async def execute_msl(params: Dict[str, Any]) -> Dict[str, Any]:
    """MSL 코드를 실행하는 메서드"""
    code = params.get("code", "")
    # TODO: MSL 실행기 구현 연동
    return {"executed": True, "result": {}}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 