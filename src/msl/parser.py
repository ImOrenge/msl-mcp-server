"""
MSL(Macro Script Language) 파서 구현
"""
from typing import Dict, Any, List, Optional
from enum import Enum, auto

class TokenType(Enum):
    """토큰 타입"""
    COMMAND = auto()
    PARAM = auto()
    COMMENT = auto()
    NEWLINE = auto()

class Token:
    """토큰 클래스"""
    def __init__(self, type: TokenType, value: str):
        self.type = type
        self.value = value

class MSLNode:
    """AST 노드 클래스"""
    def __init__(self, type: str, **kwargs):
        self.type = type
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def to_dict(self) -> Dict[str, Any]:
        """노드를 딕셔너리로 변환"""
        result = {'type': self.type}
        for key, value in self.__dict__.items():
            if key != 'type':
                if isinstance(value, MSLNode):
                    result[key] = value.to_dict()
                elif isinstance(value, list):
                    result[key] = [
                        item.to_dict() if isinstance(item, MSLNode) else item
                        for item in value
                    ]
                else:
                    result[key] = value
        return result

class MSLParser:
    def __init__(self):
        self.tokens = []
        self.current_pos = 0
    
    def parse(self, code: str) -> Dict[str, Any]:
        """
        MSL 코드를 파싱하여 AST(Abstract Syntax Tree)를 생성합니다.
        
        Args:
            code (str): 파싱할 MSL 코드
            
        Returns:
            Dict[str, Any]: 파싱된 AST
        """
        try:
            # 기본적인 명령어 파싱 구현
            commands = []
            for line in code.split('\n'):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # 주석 제거
                if '#' in line:
                    line = line[:line.index('#')].strip()
                
                # 명령어와 매개변수 분리
                parts = line.split()
                if not parts:
                    continue
                
                command = {
                    'type': 'command',
                    'name': parts[0],
                    'params': parts[1:]
                }
                commands.append(command)
            
            return {
                'type': 'program',
                'body': commands
            }
            
        except Exception as e:
            raise ValueError(f'Failed to parse MSL code: {str(e)}')
    
    def parse_invalid_command(self):
        """
        잘못된 명령어를 파싱할 때 예외를 발생시킵니다.
        """
        raise ValueError("Invalid command")

    def validate(self, ast: Dict[str, Any]) -> List[str]:
        """
        생성된 AST의 유효성을 검사합니다.
        
        Args:
            ast (Dict[str, Any]): 검사할 AST
            
        Returns:
            List[str]: 발견된 오류 메시지 목록
        """
        errors = []
        
        if ast['type'] != 'program':
            errors.append('Invalid AST: Root node must be of type "program"')
            
        for command in ast.get('body', []):
            if command['type'] != 'command':
                errors.append(f'Invalid command type: {command["type"]}')
            if not command.get('name'):
                errors.append('Command must have a name')
                
        return errors

# 모듈 레벨에서 클래스들을 내보냄
__all__ = ['TokenType', 'Token', 'MSLNode', 'MSLParser'] 