from typing import Dict, Optional
import json
import logging
from .fastmcp import FastMCP, MCPContext
from .resources import ResourceManager, VoiceCommand
from .tools import ToolManager, ToolContext, ToolResult
from .prompts import PromptManager, Prompt

class MSLMCPServer(FastMCP):
    """MSL MCP 서버 구현"""
    def __init__(self):
        super().__init__()
        
        # 매니저 초기화
        self.resource_manager = ResourceManager()
        self.tool_manager = ToolManager()
        self.prompt_manager = PromptManager()
        
        # 추가 라우트 설정
        self.setup_additional_routes()
        
    def setup_additional_routes(self):
        """추가 라우트 설정"""
        @self.app.post("/voice-command")
        async def create_voice_command(command: VoiceCommand):
            success = await self.resource_manager.register_voice_command(command)
            if success:
                return {"status": "success", "command_id": command.command_id}
            return {"status": "error", "message": "Failed to register command"}
            
        @self.app.get("/voice-commands")
        async def list_voice_commands():
            commands = await self.resource_manager.list_voice_commands()
            return {"status": "success", "commands": commands}
            
    async def process_message(self, client_id: str, data: Dict) -> Dict:
        """JSON-RPC 메시지 처리"""
        try:
            # 메시지 ID 확인
            msg_id = data.get("id")
            
            # 메서드 확인
            method = data.get("method")
            if not method:
                return self.create_error_response(-32600, "Method not found", msg_id)
                
            # 파라미터 확인
            params = data.get("params", {})
            
            # 메서드 처리
            result = await self.handle_method(client_id, method, params)
            
            # 응답 생성
            return {
                "jsonrpc": "2.0",
                "result": result,
                "id": msg_id
            }
            
        except Exception as e:
            self.logger.error(f"Error processing message: {str(e)}")
            return self.create_error_response(-32603, str(e), data.get("id"))
            
    async def handle_method(self, client_id: str, method: str, params: Dict) -> Dict:
        """메서드 처리"""
        if method == "execute_command":
            return await self.handle_execute_command(client_id, params)
        elif method == "get_command_status":
            return await self.handle_get_command_status(client_id, params)
        else:
            raise Exception(f"Unknown method: {method}")
            
    async def handle_execute_command(self, client_id: str, params: Dict) -> Dict:
        """명령 실행 처리"""
        try:
            # 음성 명령 생성
            command_text = params.get("command")
            if not command_text:
                raise ValueError("Command text is required")
                
            command = VoiceCommand(
                command_id=f"cmd_{client_id}_{len(self.resource_manager.voice_commands)}",
                text=command_text
            )
            
            # 음성 명령 등록
            await self.resource_manager.register_voice_command(command)
            
            # 프롬프트 생성
            prompt = await self.prompt_manager.create_prompt(
                "voice_command",
                {"command": command_text}
            )
            
            if not prompt:
                raise Exception("Failed to create prompt")
                
            # 도구 실행
            tool_context = ToolContext(
                tool_id="windows_automation",
                parameters={"command": command_text}
            )
            
            result = await self.tool_manager.execute_tool(tool_context)
            
            return {
                "command_id": command.command_id,
                "status": "success" if result.success else "error",
                "result": result.result,
                "error": result.error
            }
            
        except Exception as e:
            self.logger.error(f"Error executing command: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
            
    async def handle_get_command_status(self, client_id: str, params: Dict) -> Dict:
        """명령 상태 조회 처리"""
        command_id = params.get("command_id")
        if not command_id:
            raise ValueError("Command ID is required")
            
        command = await self.resource_manager.get_voice_command(command_id)
        if not command:
            return {
                "status": "error",
                "error": "Command not found"
            }
            
        return {
            "command_id": command_id,
            "status": "completed",  # 실제 구현에서는 상태 추적 필요
            "command": command
        }
        
    def create_error_response(self, code: int, message: str, id: Optional[str] = None) -> Dict:
        """에러 응답 생성"""
        return {
            "jsonrpc": "2.0",
            "error": {
                "code": code,
                "message": message
            },
            "id": id
        } 