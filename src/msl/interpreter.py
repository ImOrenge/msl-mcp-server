"""
MSL(Macro Script Language) 인터프리터 구현
"""
from typing import Dict, Any, List
import pyautogui
import time

class MSLInterpreter:
    def __init__(self):
        # 기본 명령어 매핑
        self.commands = {
            'click': self._cmd_click,
            'type': self._cmd_type,
            'wait': self._cmd_wait,
            'move': self._cmd_move,
            'press': self._cmd_press,
            'hotkey': self._cmd_hotkey
        }
    
    def execute(self, ast: Dict[str, Any]) -> Dict[str, Any]:
        """
        AST를 실행합니다.
        
        Args:
            ast (Dict[str, Any]): 실행할 AST
            
        Returns:
            Dict[str, Any]: 실행 결과
        """
        try:
            if ast['type'] != 'program':
                raise ValueError('Invalid AST: Root node must be of type "program"')
            
            results = []
            for command in ast['body']:
                if command['type'] != 'command':
                    raise ValueError(f'Invalid command type: {command["type"]}')
                
                cmd_name = command['name']
                if cmd_name not in self.commands:
                    raise ValueError(f'Unknown command: {cmd_name}')
                
                cmd_func = self.commands[cmd_name]
                result = cmd_func(command['params'])
                results.append(result)
            
            return {
                'success': True,
                'results': results,
                'errors': []
            }
            
        except Exception as e:
            return {
                'success': False,
                'results': [],
                'errors': [str(e)]
            }
    
    def _cmd_click(self, params: List[str]) -> Dict[str, Any]:
        """마우스 클릭"""
        if len(params) != 2:
            raise ValueError('Click command requires 2 parameters: x y')
        x, y = map(int, params)
        pyautogui.click(x, y)
        return {'action': 'click', 'x': x, 'y': y}
    
    def _cmd_type(self, params: List[str]) -> Dict[str, Any]:
        """텍스트 입력"""
        text = ' '.join(params)
        pyautogui.write(text)
        return {'action': 'type', 'text': text}
    
    def _cmd_wait(self, params: List[str]) -> Dict[str, Any]:
        """대기"""
        if len(params) != 1:
            raise ValueError('Wait command requires 1 parameter: seconds')
        seconds = float(params[0])
        time.sleep(seconds)
        return {'action': 'wait', 'seconds': seconds}
    
    def _cmd_move(self, params: List[str]) -> Dict[str, Any]:
        """마우스 이동"""
        if len(params) != 2:
            raise ValueError('Move command requires 2 parameters: x y')
        x, y = map(int, params)
        pyautogui.moveTo(x, y)
        return {'action': 'move', 'x': x, 'y': y}
    
    def _cmd_press(self, params: List[str]) -> Dict[str, Any]:
        """키 누르기"""
        if len(params) != 1:
            raise ValueError('Press command requires 1 parameter: key')
        key = params[0]
        pyautogui.press(key)
        return {'action': 'press', 'key': key}
    
    def _cmd_hotkey(self, params: List[str]) -> Dict[str, Any]:
        """단축키 입력"""
        if len(params) < 2:
            raise ValueError('Hotkey command requires at least 2 parameters: key1 key2 ...')
        pyautogui.hotkey(*params)
        return {'action': 'hotkey', 'keys': params} 