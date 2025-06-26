from typing import Dict, List, Optional, Any
from pydantic import BaseModel
from datetime import datetime

class VoiceCommand(BaseModel):
    """음성 명령 리소스 모델"""
    command_id: str
    text: str
    language: str = "ko"
    timestamp: datetime = datetime.now()
    metadata: Dict[str, Any] = {}

class ResourceManager:
    """리소스 관리자"""
    def __init__(self):
        self.voice_commands: Dict[str, VoiceCommand] = {}
        
    async def register_voice_command(self, command: VoiceCommand) -> bool:
        """음성 명령 등록"""
        try:
            self.voice_commands[command.command_id] = command
            return True
        except Exception:
            return False
            
    async def get_voice_command(self, command_id: str) -> Optional[VoiceCommand]:
        """음성 명령 조회"""
        return self.voice_commands.get(command_id)
        
    async def update_voice_command(self, command_id: str, command: VoiceCommand) -> bool:
        """음성 명령 업데이트"""
        if command_id in self.voice_commands:
            self.voice_commands[command_id] = command
            return True
        return False
        
    async def delete_voice_command(self, command_id: str) -> bool:
        """음성 명령 삭제"""
        try:
            if command_id in self.voice_commands:
                del self.voice_commands[command_id]
                return True
            return False
        except Exception:
            return False
        
    async def list_voice_commands(self) -> List[VoiceCommand]:
        """음성 명령 목록 조회"""
        return list(self.voice_commands.values())
        
    async def search_voice_commands(self, query: str) -> List[VoiceCommand]:
        """음성 명령 검색"""
        query = query.lower()
        return [
            command for command in self.voice_commands.values()
            if query in command.text.lower()
        ]
        
    async def clear_voice_commands(self) -> bool:
        """모든 음성 명령 삭제"""
        try:
            self.voice_commands.clear()
            return True
        except Exception:
            return False 