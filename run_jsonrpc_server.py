import os
import sys
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from src.msl.parser import MSLParser
from src.msl.interpreter import MSLInterpreter
import uvicorn

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

app = FastAPI()
parser = MSLParser()
interpreter = MSLInterpreter()

@app.post("/mcp")
async def handle_mcp_request(request: Request):
    """
    MCP 요청을 처리하는 메인 엔드포인트
    """
    try:
        # 요청 본문을 JSON으로 파싱
        request_data = await request.json()
        
        # JSON-RPC 2.0 형식 검증
        if request_data.get("jsonrpc") != "2.0":
            return JSONResponse(
                content={
                    "jsonrpc": "2.0",
                    "error": {"code": -32600, "message": "Invalid Request"},
                    "id": None
                }
            )
        
        method = request_data.get("method")
        params = request_data.get("params", {})
        req_id = request_data.get("id")
        
        # MCP 메서드 처리
        if method == "msl.parse":
            if "code" not in params:
                return JSONResponse(
                    content={
                        "jsonrpc": "2.0",
                        "error": {"code": -32602, "message": "Invalid params: 'code' is required"},
                        "id": req_id
                    }
                )
            
            # MSL 코드 파싱
            ast = parser.parse(params["code"])
            
            # 파싱 결과 검증
            errors = parser.validate(ast)
            if errors:
                return JSONResponse(
                    content={
                        "jsonrpc": "2.0",
                        "error": {"code": -32603, "message": "Parse errors", "data": errors},
                        "id": req_id
                    }
                )
            
            return JSONResponse(
                content={
                    "jsonrpc": "2.0",
                    "result": ast,
                    "id": req_id
                }
            )
            
        elif method == "msl.execute":
            if "ast" not in params:
                return JSONResponse(
                    content={
                        "jsonrpc": "2.0",
                        "error": {"code": -32602, "message": "Invalid params: 'ast' is required"},
                        "id": req_id
                    }
                )
            
            # MSL AST 실행
            result = interpreter.execute(params["ast"])
            
            if not result["success"]:
                return JSONResponse(
                    content={
                        "jsonrpc": "2.0",
                        "error": {"code": -32603, "message": "Execution errors", "data": result["errors"]},
                        "id": req_id
                    }
                )
            
            return JSONResponse(
                content={
                    "jsonrpc": "2.0",
                    "result": result,
                    "id": req_id
                }
            )
            
        else:
            return JSONResponse(
                content={
                    "jsonrpc": "2.0",
                    "error": {"code": -32601, "message": f"Method not found: {method}"},
                    "id": req_id
                }
            )
            
    except Exception as e:
        return JSONResponse(
            content={
                "jsonrpc": "2.0",
                "error": {"code": -32603, "message": str(e)},
                "id": None
            }
        )

if __name__ == "__main__":
    print("Starting MSL-MCP JSON-RPC Server...")
    print("Listening on http://0.0.0.0:8000/mcp")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True) 