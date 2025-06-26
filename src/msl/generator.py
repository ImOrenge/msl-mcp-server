from typing import Dict, Any, Optional, List
from prompt.analyzer import Intent

class MSLGenerator:
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
            params = intent.parameters.copy()
            
            # 특수 매개변수 처리
            if intent.action == 'click' and 'target' in params:
                # 여기서는 임시로 고정 좌표 사용
                params['x'] = 100
                params['y'] = 200
            
            # 템플릿에 매개변수 적용
            script = template.format(**params)
            return script
        except KeyError:
            # 필요한 매개변수가 없는 경우
            return None

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

    def generate_compound(self, intents: List[Intent]) -> Optional[str]:
        """여러 의도를 하나의 MSL 스크립트로 결합"""
        if not intents:
            return None

        scripts = []
        for intent in intents:
            script = self.generate(intent)
            if script:
                scripts.append(script)

        if not scripts:
            return None

        # 각 명령어를 새 줄로 구분
        return '\n'.join(scripts)

    def generate_with_error_handling(self, intent: Intent) -> Optional[str]:
        """에러 처리가 포함된 MSL 스크립트 생성"""
        script = self.generate(intent)
        if not script:
            return None

        # try-catch 블록으로 감싸기
        return f"""try {{
    {script}
}} catch (error) {{
    // 에러 처리
    print("Error: " + error)
}}"""

    def generate_with_retry(self, intent: Intent, max_retries: int = 3, delay: float = 1.0) -> Optional[str]:
        """재시도 로직이 포함된 MSL 스크립트 생성"""
        script = self.generate(intent)
        if not script:
            return None

        # 재시도 로직 추가
        return f"""retries = 0
while retries < {max_retries} {{
    try {{
        {script}
        break
    }} catch (error) {{
        retries = retries + 1
        if retries >= {max_retries} {{
            print("Max retries reached: " + error)
            break
        }}
        wait({delay})
    }}
}}"""

    def generate_with_conditions(self, intent: Intent, conditions: Dict[str, Any]) -> Optional[str]:
        """조건부 실행이 포함된 MSL 스크립트 생성"""
        script = self.generate(intent)
        if not script:
            return None

        condition_scripts = []
        for key, value in conditions.items():
            if isinstance(value, bool):
                condition_scripts.append(f"{key} == {str(value).lower()}")
            elif isinstance(value, (int, float)):
                condition_scripts.append(f"{key} == {value}")
            else:
                condition_scripts.append(f"{key} == \"{value}\"")

        if not condition_scripts:
            return script

        conditions_str = ' and '.join(condition_scripts)
        return f"""if {conditions_str} {{
    {script}
}}""" 