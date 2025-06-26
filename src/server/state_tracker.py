from typing import Dict, List, Optional, Any
from pydantic import BaseModel
import logging
from datetime import datetime
import json
import asyncio
from pathlib import Path

class CommandState(BaseModel):
    """명령 상태 모델"""
    command_id: str
    status: str  # pending, processing, completed, failed
    start_time: datetime
    end_time: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class SessionState(BaseModel):
    """세션 상태 모델"""
    session_id: str
    user_id: Optional[str] = None
    start_time: datetime
    last_activity: datetime
    commands: Dict[str, CommandState] = {}
    metadata: Dict[str, Any] = {}

class StateTracker:
    """상태 추적 시스템"""
    def __init__(self, storage_dir: str = ".taskmaster/state"):
        self.logger = logging.getLogger("StateTracker")
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.active_sessions: Dict[str, SessionState] = {}
        self.load_state()
        
    def load_state(self):
        """저장된 상태 로드"""
        try:
            for file in self.storage_dir.glob("*.json"):
                with open(file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    session = SessionState(**data)
                    self.active_sessions[session.session_id] = session
        except Exception as e:
            self.logger.error(f"Error loading state: {str(e)}")
            
    async def save_state(self):
        """상태 저장"""
        try:
            for session_id, session in self.active_sessions.items():
                file_path = self.storage_dir / f"{session_id}.json"
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(session.dict(), f, default=str, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving state: {str(e)}")
            
    async def create_session(self, session_id: str, user_id: Optional[str] = None) -> SessionState:
        """새 세션 생성"""
        now = datetime.now()
        session = SessionState(
            session_id=session_id,
            user_id=user_id,
            start_time=now,
            last_activity=now
        )
        self.active_sessions[session_id] = session
        await self.save_state()
        return session
        
    async def get_session(self, session_id: str) -> Optional[SessionState]:
        """세션 조회"""
        return self.active_sessions.get(session_id)
        
    async def update_session(self, session_id: str, metadata: Dict[str, Any]) -> Optional[SessionState]:
        """세션 업데이트"""
        session = await self.get_session(session_id)
        if session:
            session.metadata.update(metadata)
            session.last_activity = datetime.now()
            await self.save_state()
        return session
        
    async def start_command(self, session_id: str, command_id: str) -> Optional[CommandState]:
        """명령 시작"""
        session = await self.get_session(session_id)
        if not session:
            return None
            
        command_state = CommandState(
            command_id=command_id,
            status="pending",
            start_time=datetime.now()
        )
        session.commands[command_id] = command_state
        await self.save_state()
        return command_state
        
    async def update_command_status(
        self,
        session_id: str,
        command_id: str,
        status: str,
        result: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None
    ) -> Optional[CommandState]:
        """명령 상태 업데이트"""
        session = await self.get_session(session_id)
        if not session or command_id not in session.commands:
            return None
            
        command_state = session.commands[command_id]
        command_state.status = status
        if status in ["completed", "failed"]:
            command_state.end_time = datetime.now()
        if result:
            command_state.result = result
        if error:
            command_state.error = error
            
        await self.save_state()
        return command_state
        
    async def get_command_history(
        self,
        session_id: str,
        status: Optional[str] = None,
        limit: int = 10
    ) -> List[CommandState]:
        """명령 이력 조회"""
        session = await self.get_session(session_id)
        if not session:
            return []
            
        commands = list(session.commands.values())
        if status:
            commands = [cmd for cmd in commands if cmd.status == status]
            
        return sorted(
            commands,
            key=lambda x: x.start_time,
            reverse=True
        )[:limit]
        
    async def cleanup_old_sessions(self, max_age_hours: int = 24):
        """오래된 세션 정리"""
        now = datetime.now()
        to_remove = []
        
        for session_id, session in self.active_sessions.items():
            age = (now - session.last_activity).total_seconds() / 3600
            if age > max_age_hours:
                to_remove.append(session_id)
                
        for session_id in to_remove:
            del self.active_sessions[session_id]
            file_path = self.storage_dir / f"{session_id}.json"
            if file_path.exists():
                file_path.unlink()
                
        if to_remove:
            await self.save_state() 