from typing import Dict, Any, Optional
from .analyzer import Intent

class PromptGenerator:
    def __init__(self):
        # 기본 MSL 템플릿
        self.templates = {
            'click': 'click({x}, {y})',
            'type': 'type("{text}")',
            'press': 'press("{key}")',
            'wait': 'wait({seconds})',
            'move': 'move({x}, {y})',
            'drag': 'drag({start_x}, {start_y}, {end_x}, {end_y})',
            'scroll': 'scroll({amount})',
            'hotkey': 'hotkey("{key1}", "{key2}")'
        }

    def generate(self, intent: Intent) -> Optional[str]:
        """의도 분석 결과를 MSL 스크립트로 변환"""
        if not intent or not intent.action or not intent.parameters:
            return None

        template = self.templates.get(intent.action)
        if not template:
            return None

        try:
            # 매개변수 전처리
            processed_params = self._process_parameters(intent.parameters)
            # 템플릿에 매개변수 적용
            script = template.format(**processed_params)
            return script
        except KeyError as e:
            # 필요한 매개변수가 없는 경우
            return None
        except Exception as e:
            # 기타 오류
            return None

    def _process_parameters(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """매개변수 전처리"""
        processed = {}
        for key, value in params.items():
            # 문자열 이스케이프
            if isinstance(value, str):
                processed[key] = value.replace('"', '\\"')
            # 숫자 형식 변환
            elif isinstance(value, (int, float)):
                processed[key] = str(value)
            # 기타 타입은 그대로 사용
            else:
                processed[key] = value
        return processed

    def add_template(self, action: str, template: str) -> None:
        """새로운 템플릿 추가"""
        self.templates[action] = template

    def remove_template(self, action: str) -> None:
        """템플릿 제거"""
        if action in self.templates:
            del self.templates[action]

    def get_template(self, action: str) -> Optional[str]:
        """템플릿 조회"""
        return self.templates.get(action)

    def list_templates(self) -> Dict[str, str]:
        """모든 템플릿 조회"""
        return self.templates.copy() 