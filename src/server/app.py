from fastapi import FastAPI, WebSocket, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import json
import asyncio
import logging
import threading
from concurrent.futures import ThreadPoolExecutor
from msl.parser import MSLParser
from msl.interpreter import MSLInterpreter
from msl.generator import MSLGenerator
from prompt.analyzer import IntentAnalyzer, Intent

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# FastAPI 앱 생성
app = FastAPI(
    title="MSL-MCP-Server",
    description="MSL(Macro Script Language) 스크립트를 처리하는 서버",
    version="1.0.0"
)

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# 전역 객체 초기화
parser = MSLParser()
interpreter = MSLInterpreter()
generator = MSLGenerator()
analyzer = IntentAnalyzer()
executor = ThreadPoolExecutor(max_workers=4)

class VoiceCommand(BaseModel):
    text: str

class ScriptCommand(BaseModel):
    script: str

class WebSocketMessage(BaseModel):
    type: str
    text: Optional[str] = None
    script: Optional[str] = None

def run_in_thread(script: str) -> bool:
    """스크립트를 별도 스레드에서 실행"""
    try:
        # 스크립트 파싱
        ast = parser.parse(script)
        if not ast:
            logger.error(f"Failed to parse script: {script}")
            return False

        # 스크립트 실행
        interpreter.stop_flag = False
        result = interpreter.execute(ast)
        return result

    except Exception as e:
        logger.error(f"Error executing script: {e}")
        return False

@app.get("/health")
async def health_check():
    """서버 상태 확인"""
    return {"status": "ok"}

@app.post("/api/voice")
async def process_voice(command: VoiceCommand, background_tasks: BackgroundTasks):
    """음성 명령 처리"""
    try:
        # 의도 분석
        intent = analyzer.analyze(command.text)
        if not intent:
            raise HTTPException(status_code=400, detail="Failed to analyze command")

        # MSL 스크립트 생성
        script = generator.generate(intent)
        if not script:
            raise HTTPException(status_code=400, detail="Failed to generate script")

        return {"script": script}

    except Exception as e:
        logger.error(f"Error processing voice command: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/script")
async def execute_script(command: ScriptCommand, background_tasks: BackgroundTasks):
    """MSL 스크립트 실행"""
    try:
        # 스크립트를 백그라운드에서 실행
        background_tasks.add_task(run_in_thread, command.script)
        return {"status": "success"}

    except Exception as e:
        logger.error(f"Error executing script: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/stop")
async def stop_execution():
    """실행 중인 스크립트 중지"""
    interpreter.stop_flag = True
    return {"status": "stopped"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket 연결 처리"""
    await websocket.accept()
    
    try:
        while True:
            # 메시지 수신
            data = await websocket.receive_json()
            message = WebSocketMessage(**data)

            if message.type == "voice":
                # 음성 명령 처리
                intent = analyzer.analyze(message.text)
                if not intent:
                    await websocket.send_json({
                        "type": "error",
                        "error": "Failed to analyze command"
                    })
                    continue

                script = generator.generate(intent)
                if not script:
                    await websocket.send_json({
                        "type": "error",
                        "error": "Failed to generate script"
                    })
                    continue

                # 생성된 스크립트 전송
                await websocket.send_json({
                    "type": "script",
                    "script": script
                })

                # 스크립트 실행
                future = executor.submit(run_in_thread, script)
                result = future.result()

                # 실행 결과 전송
                await websocket.send_json({
                    "type": "result",
                    "status": "success" if result else "error"
                })

            elif message.type == "script":
                # 스크립트 직접 실행
                if not message.script:
                    await websocket.send_json({
                        "type": "error",
                        "error": "Script is required"
                    })
                    continue

                future = executor.submit(run_in_thread, message.script)
                result = future.result()

                await websocket.send_json({
                    "type": "result",
                    "status": "success" if result else "error"
                })

            elif message.type == "stop":
                # 실행 중지
                interpreter.stop_flag = True
                await websocket.send_json({
                    "type": "result",
                    "status": "stopped"
                })

            else:
                await websocket.send_json({
                    "type": "error",
                    "error": "Invalid message type"
                })

    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.close()

@app.on_event("shutdown")
async def shutdown_event():
    """서버 종료 시 정리 작업"""
    executor.shutdown(wait=True)
    logger.info("Server shutting down") 