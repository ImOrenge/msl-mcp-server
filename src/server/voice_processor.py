from typing import Dict, List, Optional, Any
import logging
from pydantic import BaseModel
import re
from datetime import datetime

class VoiceCommand(BaseModel):
    """음성 명령 모델"""
    command_id: str
    text: str
    language: str = "ko"
    confidence: float
    timestamp: datetime = datetime.now()
    metadata: Dict[str, Any] = {}

class CommandIntent(BaseModel):
    """명령 의도 모델"""
    intent_type: str
    parameters: Dict[str, Any] = {}
    confidence: float
    original_command: VoiceCommand

class VoiceProcessor:
    """음성 명령 처리기"""
    def __init__(self):
        self.logger = logging.getLogger("VoiceProcessor")
        self.command_patterns: Dict[str, List[str]] = {
            "window": [
                r"(?P<title>[\w\s]+)\s*(창|윈도우)\s*(열기|닫기|최소화|최대화)",
                r"(?P<title>[\w\s]+)\s*(프로그램|앱)\s*(실행|종료)"
            ],
            "type": [
                r"(?P<text>[\w\s]+)\s*(입력|타이핑)",
                r"(?P<text>[\w\s]+)\s*써"
            ],
            "hotkey": [
                r"(?P<keys>[\w\s]+)\s*(단축키|핫키)",
                r"(?P<keys>[\w\s]+)\s*키\s*(누르기|입력)"
            ],
            "click": [
                r"(?P<target>[\w\s]+)\s*(클릭|선택)",
                r"(?P<target>[\w\s]+)\s*(누르기|터치)"
            ]
        }
        
    async def process_command(self, command: VoiceCommand) -> Optional[CommandIntent]:
        """음성 명령 처리"""
        try:
            # 명령 텍스트 정규화
            normalized_text = self._normalize_text(command.text)
            
            # 의도 분석
            intent = self._analyze_intent(normalized_text)
            if not intent:
                self.logger.warning(f"No intent found for command: {normalized_text}")
                return None
                
            # 파라미터 추출
            parameters = self._extract_parameters(normalized_text, intent)
            
            return CommandIntent(
                intent_type=intent,
                parameters=parameters,
                confidence=command.confidence,
                original_command=command
            )
            
        except Exception as e:
            self.logger.error(f"Error processing command: {str(e)}")
            return None
            
    def _normalize_text(self, text: str) -> str:
        """텍스트 정규화"""
        # 소문자 변환
        text = text.lower()
        # 불필요한 공백 제거
        text = re.sub(r'\s+', ' ', text).strip()
        # 특수문자 처리
        text = re.sub(r'[^\w\s가-힣]', '', text)
        return text
        
    def _analyze_intent(self, text: str) -> Optional[str]:
        """의도 분석"""
        for intent, patterns in self.command_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text):
                    return intent
        return None
        
    def _extract_parameters(self, text: str, intent: str) -> Dict[str, Any]:
        """파라미터 추출"""
        parameters = {}
        
        for pattern in self.command_patterns[intent]:
            match = re.search(pattern, text)
            if match:
                parameters.update(match.groupdict())
                
                # 특별한 파라미터 처리
                if intent == "window":
                    operation = "open"
                    if "닫기" in text or "종료" in text:
                        operation = "close"
                    elif "최소화" in text:
                        operation = "minimize"
                    elif "최대화" in text:
                        operation = "maximize"
                    parameters["operation"] = operation
                    
                elif intent == "hotkey":
                    keys = parameters.get("keys", "").split()
                    parameters["keys"] = keys
                    
                elif intent == "click":
                    parameters["target_type"] = "text"
                    if "이미지" in text or "그림" in text:
                        parameters["target_type"] = "image"
                        
                break
                
        return parameters 