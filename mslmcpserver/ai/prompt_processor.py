"""
프롬프트 처리 모듈
자연어 프롬프트를 분석하고 MSL 생성을 위한 구조화된 정보로 변환
"""

import re
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass

@dataclass
class Intent:
    """사용자 의도를 나타내는 데이터 클래스"""
    action_type: str  # "create", "modify", "explain", "convert"
    target: str       # "script", "combo", "macro"
    details: Dict[str, Any]
    confidence: float

class PromptProcessor:
    """
    자연어 프롬프트를 분석하여 MSL 생성에 필요한 구조화된 정보를 추출하는 클래스
    """
    
    def __init__(self):
        """프롬프트 처리기 초기화"""
        self._init_patterns()
        self._init_mappings()
    
    def _init_patterns(self):
        """정규표현식 패턴들 초기화"""
        self.patterns = {
            # 의도 패턴
            "create_intent": re.compile(r'(만들|생성|작성|짜|만들어줘)', re.IGNORECASE),
            "modify_intent": re.compile(r'(수정|변경|바꿔|고쳐)', re.IGNORECASE),
            "explain_intent": re.compile(r'(설명|뜻|의미|어떻게)', re.IGNORECASE),
            
            # 액션 타입 패턴
            "sequential": re.compile(r'(순서대로|차례로|하나씩)', re.IGNORECASE),
            "concurrent": re.compile(r'(동시에|같이|함께)', re.IGNORECASE),
            "repetition": re.compile(r'(\d+)?(번|회)?\s*(반복|연타)', re.IGNORECASE),
            "hold": re.compile(r'(누르고\s*있|홀드)', re.IGNORECASE),
            
            # 키 패턴
            "key_reference": re.compile(r'([a-zA-Z0-9]|space|enter|shift|ctrl)', re.IGNORECASE),
            "korean_key": re.compile(r'(큐|더블유|이|알|스페이스|엔터)', re.IGNORECASE),
        }
    
    def _init_mappings(self):
        """키 매핑 초기화"""
        self.key_mappings = {
            "큐": "q", "더블유": "w", "이": "e", "알": "r",
            "스페이스": "space", "엔터": "enter",
            "시프트": "shift", "컨트롤": "ctrl"
        }
    
    async def analyze_prompt(self, prompt: str) -> Dict[str, Any]:
        """프롬프트를 분석합니다"""
        try:
            cleaned_prompt = self._preprocess_prompt(prompt)
            intent = await self._analyze_intent(cleaned_prompt)
            keys = await self._extract_keys(cleaned_prompt)
            actions = await self._extract_actions(cleaned_prompt)
            
            return {
                "success": True,
                "intent": intent,
                "keys": keys,
                "actions": actions,
                "confidence": 0.8
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _preprocess_prompt(self, prompt: str) -> str:
        """프롬프트 전처리"""
        return re.sub(r'\s+', ' ', prompt.strip())
    
    async def _analyze_intent(self, prompt: str) -> Intent:
        """의도 분석"""
        if self.patterns["create_intent"].search(prompt):
            action_type = "create"
        elif self.patterns["modify_intent"].search(prompt):
            action_type = "modify"
        else:
            action_type = "create"
        
        return Intent(
            action_type=action_type,
            target="script",
            details={},
            confidence=0.8
        )
    
    async def _extract_keys(self, prompt: str) -> List[str]:
        """키 추출"""
        keys = []
        
        # 영문 키 추출
        english_keys = self.patterns["key_reference"].findall(prompt)
        keys.extend([key.lower() for key in english_keys])
        
        # 한글 키 변환
        for korean, english in self.key_mappings.items():
            if korean in prompt:
                keys.append(english)
        
        return list(set(keys))
    
    async def _extract_actions(self, prompt: str) -> List[Dict[str, Any]]:
        """액션 추출"""
        actions = []
        
        if self.patterns["sequential"].search(prompt):
            actions.append({"type": "sequential", "operator": ","})
        
        if self.patterns["concurrent"].search(prompt):
            actions.append({"type": "concurrent", "operator": "+"})
        
        if self.patterns["repetition"].search(prompt):
            actions.append({"type": "repetition", "operator": "*"})
        
        if not actions:
            actions.append({"type": "sequential", "operator": ","})
        
        return actions 