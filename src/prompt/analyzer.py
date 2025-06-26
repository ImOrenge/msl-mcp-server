from dataclasses import dataclass
from typing import Dict, Any, Optional
import re

@dataclass
class Intent:
    """의도 분석 결과를 나타내는 클래스"""
    action: str
    parameters: Dict[str, Any]
    confidence: float
    original_text: str

class IntentAnalyzer:
    """한국어 음성 명령을 분석하여 의도를 추출하는 클래스"""
    def __init__(self):
        # 기본 명령어 패턴
        self.patterns = {
            'click': [
                r'클릭\s*(?:해|해줘|하세요|해주세요)?$',
                r'(?:여기|저기)\s*클릭\s*(?:해|해줘|하세요|해주세요)?$',
                r'(?:좌표|위치)?\s*(\d+)\s*[,，]\s*(\d+)\s*(?:클릭|눌러)?\s*(?:해|해줘|하세요|해주세요)?$'
            ],
            'type': [
                r'입력\s*(?:해|해줘|하세요|해주세요)?$',
                r'(?:\"([^\"]+)\"|\'([^\']+)\')\s*(?:입력|타이핑)?\s*(?:해|해줘|하세요|해주세요)?$',
                r'([^\s]+)\s*(?:입력|타이핑)?\s*(?:해|해줘|하세요|해주세요)?$'
            ],
            'press': [
                r'(?:키|버튼)?\s*([^\s]+)\s*(?:눌러|누르기|누르세요|눌러주세요)$',
                r'([^\s]+)\s*(?:키|버튼)?\s*(?:눌러|누르기|누르세요|눌러주세요)$'
            ],
            'wait': [
                r'(\d+(?:\.\d+)?)\s*(?:초|분)?\s*기다려?(?:줘|주세요|요)?$',
                r'잠깐\s*(?:기다려|대기|멈춰)?(?:줘|주세요|요)?$'
            ],
            'move': [
                r'(?:마우스)?\s*이동\s*(?:해|해줘|하세요|해주세요)?$',
                r'(?:좌표|위치)?\s*(\d+)\s*[,，]\s*(\d+)(?:로|으로)?\s*(?:이동|움직여)?\s*(?:해|해줘|하세요|해주세요)?$'
            ],
            'drag': [
                r'드래그\s*(?:해|해줘|하세요|해주세요)?$',
                r'(\d+)\s*[,，]\s*(\d+)\s*에서\s*(\d+)\s*[,，]\s*(\d+)(?:로|으로)?\s*드래그\s*(?:해|해줘|하세요|해주세요)?$'
            ],
            'scroll': [
                r'(?:위로|아래로)?\s*스크롤\s*(?:해|해줘|하세요|해주세요)?$',
                r'(\d+)\s*(?:만큼)?\s*(?:위로|아래로)\s*스크롤\s*(?:해|해줘|하세요|해주세요)?$'
            ],
            'hotkey': [
                r'(?:단축키|핫키)\s*([^\s]+)\s*(?:\+\s*([^\s]+))?\s*(?:눌러|누르기|누르세요|눌러주세요)$'
            ]
        }

    def analyze(self, text: str) -> Optional[Intent]:
        """음성 명령을 분석하여 의도 추출"""
        text = text.strip()
        
        for action, patterns in self.patterns.items():
            for pattern in patterns:
                match = re.match(pattern, text, re.IGNORECASE)
                if match:
                    # 매개변수 추출
                    params = {}
                    groups = match.groups()
                    
                    if action == 'click' and len(groups) == 2:
                        params['x'] = int(groups[0])
                        params['y'] = int(groups[1])
                    elif action == 'type' and groups:
                        params['text'] = next(g for g in groups if g is not None)
                    elif action == 'press' and groups:
                        params['key'] = groups[0]
                    elif action == 'wait' and groups:
                        params['seconds'] = float(groups[0]) if groups[0] else 1.0
                    elif action == 'move' and len(groups) == 2:
                        params['x'] = int(groups[0])
                        params['y'] = int(groups[1])
                    elif action == 'drag' and len(groups) == 4:
                        params['start_x'] = int(groups[0])
                        params['start_y'] = int(groups[1])
                        params['end_x'] = int(groups[2])
                        params['end_y'] = int(groups[3])
                    elif action == 'scroll' and groups:
                        amount = int(groups[0]) if groups[0] else 1
                        if '위로' in text:
                            amount = abs(amount)
                        elif '아래로' in text:
                            amount = -abs(amount)
                        params['amount'] = amount
                    elif action == 'hotkey' and groups:
                        params['key1'] = groups[0]
                        if len(groups) > 1 and groups[1]:
                            params['key2'] = groups[1]

                    return Intent(
                        action=action,
                        parameters=params,
                        confidence=0.8,  # 임시 신뢰도 값
                        original_text=text
                    )
        
        return None 