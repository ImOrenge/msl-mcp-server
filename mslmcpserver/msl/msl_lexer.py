"""
MSL (Macro Scripting Language) Lexer - 어휘 분석기
게이머를 위한 직관적이고 강력한 매크로 언어의 토큰화를 수행합니다.

MSL 언어 구문:
- 연산자: , (순차), + (동시), > (홀드연결), | (병렬), ~ (토글), * (반복), & (연속)
- 타이밍: () 지연, [] 홀드, {} 간격, <> 페이드
- 요소: 키, 숫자, 변수($), 마우스좌표(@), 휠제어

예시:
- "W, A, S, D" - 순차 입력
- "Q + E" - 동시 입력
- "W > A > S" - 홀드 연결
- "Q * 3" - 반복
- "[SPACE, 500]" - 500ms 홀드
- "@(100,200)" - 마우스 좌표
- "wheel_up * 3" - 휠 업 3번
"""

import re
from enum import Enum
from typing import List, Optional, Union, Tuple, NamedTuple
from dataclasses import dataclass


class TokenType(Enum):
    """토큰 타입 정의"""
    # 기본 요소
    KEY = "KEY"  # 키 입력 (W, A, Space, Ctrl)
    NUMBER = "NUMBER"  # 숫자 (100, 3.5)
    VARIABLE = "VARIABLE"  # 변수 ($combo1)
    MOUSE_COORD = "MOUSE_COORD"  # 마우스 좌표 (@(100,200))
    WHEEL = "WHEEL"  # 휠 제어 (wheel_up, wheel_down)
    
    # 연산자
    COMMA = "COMMA"  # , (순차 실행)
    PLUS = "PLUS"  # + (동시 실행)
    GREATER = "GREATER"  # > (홀드 연결)
    PIPE = "PIPE"  # | (병렬 실행)
    TILDE = "TILDE"  # ~ (토글)
    STAR = "STAR"  # * (반복)
    AMPERSAND = "AMPERSAND"  # & (연속 입력)
    
    # 타이밍 제어
    LPAREN = "LPAREN"  # ( (지연 시작)
    RPAREN = "RPAREN"  # ) (지연 끝)
    LBRACKET = "LBRACKET"  # [ (홀드 시작)
    RBRACKET = "RBRACKET"  # ] (홀드 끝)
    LBRACE = "LBRACE"  # { (간격 시작)
    RBRACE = "RBRACE"  # } (간격 끝)
    LANGLE = "LANGLE"  # < (페이드 시작)
    RANGLE = "RANGLE"  # > (페이드 끝 또는 홀드 연결)
    
    # 기타
    WHITESPACE = "WHITESPACE"  # 공백
    NEWLINE = "NEWLINE"  # 줄바꿈
    EOF = "EOF"  # 파일 끝
    UNKNOWN = "UNKNOWN"  # 알 수 없는 토큰
    COMMENT = "COMMENT"  # 주석 (#)


@dataclass
class Token:
    """토큰 정보를 담는 클래스"""
    type: TokenType
    value: str
    line: int
    column: int
    position: int
    
    def __str__(self) -> str:
        return f"{self.type.value}('{self.value}') at {self.line}:{self.column}"
    
    def __repr__(self) -> str:
        return self.__str__()


class LexerError(Exception):
    """Lexer 오류 클래스"""
    
    def __init__(self, message: str, line: int, column: int, position: int):
        self.message = message
        self.line = line
        self.column = column
        self.position = position
        super().__init__(f"Lexer Error at {line}:{column}: {message}")


class MSLLexer:
    """MSL 어휘 분석기"""
    
    def __init__(self, text: str):
        """
        Lexer 초기화
        
        Args:
            text (str): 분석할 MSL 코드
        """
        self.text = text
        self.position = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []
        
        # 키워드 정의
        self.keywords = {
            # 특수 키
            'space', 'enter', 'tab', 'shift', 'ctrl', 'alt', 'esc',
            'up', 'down', 'left', 'right', 'home', 'end', 'pageup', 'pagedown',
            'insert', 'delete', 'backspace', 'capslock', 'numlock', 'scrolllock',
            
            # 펑션 키
            'f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'f10', 'f11', 'f12',
            
            # 마우스 버튼
            'lclick', 'rclick', 'mclick', 'mouse1', 'mouse2', 'mouse3', 'mouse4', 'mouse5',
            
            # 휠 제어
            'wheel_up', 'wheel_down'
        }
        
        # 정규 표현식 패턴
        self.patterns = {
            # 마우스 좌표: @(x,y)
            'mouse_coord': re.compile(r'@\s*\(\s*(\d+)\s*,\s*(\d+)\s*\)'),
            # 변수: $identifier
            'variable': re.compile(r'\$([a-zA-Z_][a-zA-Z0-9_]*)'),
            # 숫자: 정수 또는 소수
            'number': re.compile(r'\d+(\.\d+)?'),
            # 키/식별자: 문자로 시작하는 단어
            'identifier': re.compile(r'[a-zA-Z_][a-zA-Z0-9_]*'),
            # 공백
            'whitespace': re.compile(r'[ \t]+'),
            # 주석: # 부터 줄 끝까지
            'comment': re.compile(r'#.*'),
        }
    
    def current_char(self) -> Optional[str]:
        """현재 위치의 문자 반환"""
        if self.position >= len(self.text):
            return None
        return self.text[self.position]
    
    def peek_char(self, offset: int = 1) -> Optional[str]:
        """지정된 오프셋 위치의 문자 반환"""
        peek_position = self.position + offset
        if peek_position >= len(self.text):
            return None
        return self.text[peek_position]
    
    def advance(self) -> Optional[str]:
        """다음 문자로 이동하고 현재 문자 반환"""
        char = self.current_char()
        if char is not None:
            self.position += 1
            if char == '\n':
                self.line += 1
                self.column = 1
            else:
                self.column += 1
        return char
    
    def skip_whitespace(self):
        """공백 문자 건너뛰기"""
        while self.current_char() and self.current_char() in ' \t':
            self.advance()
    
    def read_string(self, pattern: re.Pattern) -> Optional[re.Match]:
        """정규 표현식 패턴으로 문자열 읽기"""
        remaining_text = self.text[self.position:]
        match = pattern.match(remaining_text)
        if match:
            for _ in range(len(match.group(0))):
                self.advance()
        return match
    
    def create_token(self, token_type: TokenType, value: str, start_pos: int = None) -> Token:
        """토큰 생성"""
        if start_pos is None:
            start_pos = self.position - len(value)
        
        # 시작 위치의 라인과 컬럼 계산
        start_line = self.line
        start_column = self.column - len(value)
        
        return Token(token_type, value, start_line, start_column, start_pos)
    
    def tokenize_mouse_coord(self) -> Token:
        """마우스 좌표 토큰화"""
        start_pos = self.position
        start_line = self.line
        start_column = self.column
        
        match = self.read_string(self.patterns['mouse_coord'])
        if match:
            full_match = match.group(0)
            x, y = match.groups()
            return Token(TokenType.MOUSE_COORD, f"@({x},{y})", start_line, start_column, start_pos)
        
        # 매치되지 않으면 @ 문자만 처리
        self.advance()
        return Token(TokenType.UNKNOWN, "@", start_line, start_column, start_pos)
    
    def tokenize_variable(self) -> Token:
        """변수 토큰화"""
        start_pos = self.position
        start_line = self.line
        start_column = self.column
        
        match = self.read_string(self.patterns['variable'])
        if match:
            variable_name = match.group(1)
            return Token(TokenType.VARIABLE, variable_name, start_line, start_column, start_pos)
        
        # 매치되지 않으면 $ 문자만 처리
        self.advance()
        return Token(TokenType.UNKNOWN, "$", start_line, start_column, start_pos)
    
    def tokenize_number(self) -> Token:
        """숫자 토큰화"""
        start_pos = self.position
        start_line = self.line
        start_column = self.column
        
        match = self.read_string(self.patterns['number'])
        if match:
            number_str = match.group(0)
            return Token(TokenType.NUMBER, number_str, start_line, start_column, start_pos)
        
        return None
    
    def tokenize_identifier(self) -> Token:
        """식별자 토큰화 (키 또는 휠 제어)"""
        start_pos = self.position
        start_line = self.line
        start_column = self.column
        
        match = self.read_string(self.patterns['identifier'])
        if match:
            identifier = match.group(0).lower()
            
            # 휠 제어인지 확인
            if identifier in ['wheel_up', 'wheel_down']:
                return Token(TokenType.WHEEL, identifier, start_line, start_column, start_pos)
            
            # 키워드 또는 일반 키로 처리
            return Token(TokenType.KEY, identifier, start_line, start_column, start_pos)
        
        return None
    
    def tokenize_comment(self) -> Token:
        """주석 토큰화"""
        start_pos = self.position
        start_line = self.line
        start_column = self.column
        
        match = self.read_string(self.patterns['comment'])
        if match:
            comment_text = match.group(0)
            return Token(TokenType.COMMENT, comment_text, start_line, start_column, start_pos)
        
        return None
    
    def tokenize_angle_bracket(self) -> Token:
        """< 또는 > 토큰화 (페이드 또는 홀드 연결)"""
        start_pos = self.position
        start_line = self.line
        start_column = self.column
        char = self.advance()
        
        if char == '<':
            return Token(TokenType.LANGLE, char, start_line, start_column, start_pos)
        elif char == '>':
            # > 는 두 가지 의미: 홀드 연결 또는 페이드 끝
            # 컨텍스트에 따라 파서에서 결정
            return Token(TokenType.GREATER, char, start_line, start_column, start_pos)
        
        return None
    
    def tokenize_single_char(self) -> Optional[Token]:
        """단일 문자 토큰화"""
        start_pos = self.position
        start_line = self.line
        start_column = self.column
        char = self.current_char()
        
        if char is None:
            return Token(TokenType.EOF, "", start_line, start_column, start_pos)
        
        self.advance()
        
        # 단일 문자 토큰 매핑
        single_char_tokens = {
            ',': TokenType.COMMA,
            '+': TokenType.PLUS,
            '|': TokenType.PIPE,
            '~': TokenType.TILDE,
            '*': TokenType.STAR,
            '&': TokenType.AMPERSAND,
            '(': TokenType.LPAREN,
            ')': TokenType.RPAREN,
            '[': TokenType.LBRACKET,
            ']': TokenType.RBRACKET,
            '{': TokenType.LBRACE,
            '}': TokenType.RBRACE,
            '\n': TokenType.NEWLINE,
        }
        
        token_type = single_char_tokens.get(char, TokenType.UNKNOWN)
        return Token(token_type, char, start_line, start_column, start_pos)
    
    def tokenize(self) -> List[Token]:
        """텍스트를 토큰으로 분해"""
        self.tokens = []
        
        while self.position < len(self.text):
            char = self.current_char()
            
            if char is None:
                break
            
            # 공백 처리
            if char in ' \t':
                self.skip_whitespace()
                continue
            
            # 주석 처리
            if char == '#':
                token = self.tokenize_comment()
                if token:
                    self.tokens.append(token)
                continue
            
            # 마우스 좌표 처리
            if char == '@':
                token = self.tokenize_mouse_coord()
                self.tokens.append(token)
                continue
            
            # 변수 처리
            if char == '$':
                token = self.tokenize_variable()
                self.tokens.append(token)
                continue
            
            # 각도 괄호 처리
            if char in '<>':
                token = self.tokenize_angle_bracket()
                if token:
                    self.tokens.append(token)
                continue
            
            # 숫자 처리
            if char.isdigit():
                token = self.tokenize_number()
                if token:
                    self.tokens.append(token)
                    continue
            
            # 식별자 (키 또는 휠) 처리
            if char.isalpha() or char == '_':
                token = self.tokenize_identifier()
                if token:
                    self.tokens.append(token)
                    continue
            
            # 단일 문자 토큰 처리
            token = self.tokenize_single_char()
            if token:
                self.tokens.append(token)
            else:
                # 알 수 없는 문자
                start_pos = self.position
                start_line = self.line
                start_column = self.column
                unknown_char = self.advance()
                self.tokens.append(Token(TokenType.UNKNOWN, unknown_char, start_line, start_column, start_pos))
        
        # EOF 토큰 추가
        self.tokens.append(Token(TokenType.EOF, "", self.line, self.column, self.position))
        return self.tokens
    
    def get_tokens_by_type(self, token_type: TokenType) -> List[Token]:
        """특정 타입의 토큰들 반환"""
        return [token for token in self.tokens if token.type == token_type]
    
    def get_line_tokens(self, line_number: int) -> List[Token]:
        """특정 라인의 토큰들 반환"""
        return [token for token in self.tokens if token.line == line_number]
    
    def print_tokens(self):
        """토큰 목록 출력"""
        print("=== 토큰 분석 결과 ===")
        for i, token in enumerate(self.tokens):
            print(f"{i:3d}: {token}")
    
    def get_token_statistics(self) -> dict:
        """토큰 통계 반환"""
        stats = {}
        for token in self.tokens:
            if token.type not in stats:
                stats[token.type] = 0
            stats[token.type] += 1
        return stats


def demo_lexer():
    """Lexer 데모 함수"""
    print("=== MSL Lexer 데모 ===\n")
    
    # 테스트 케이스들
    test_cases = [
        # 기본 키 시퀀스
        "W, A, S, D",
        
        # 동시 입력
        "Q + E + R",
        
        # 홀드 연결
        "W > A > S > D",
        
        # 반복
        "SPACE * 3",
        
        # 병렬 실행
        "W | A | S",
        
        # 토글
        "~CAPSLOCK",
        
        # 연속 입력
        "Q & 100",
        
        # 타이밍 제어
        "[SPACE, 500], (200), {Q, 100}, <W, 300>",
        
        # 마우스 좌표
        "@(100, 200), @(300,400)",
        
        # 변수
        "$combo1, $movement_keys",
        
        # 휠 제어
        "wheel_up * 3, wheel_down",
        
        # 복합 매크로
        "W, (Q + E) * 2, [SPACE, 500], @(100,200), wheel_up, $combo1",
        
        # 주석 포함
        "W, A # 이동 키들\nQ + E # 스킬 조합",
        
        # 복잡한 매크로
        "~SHIFT > W > A, [SPACE, 1000] | Q & 50, @(200,300) + LCLICK * 3"
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"{i}. 테스트 케이스: '{test_case}'")
        
        try:
            lexer = MSLLexer(test_case)
            tokens = lexer.tokenize()
            
            # 의미있는 토큰만 출력 (공백, 주석, EOF 제외)
            meaningful_tokens = [
                token for token in tokens 
                if token.type not in [TokenType.WHITESPACE, TokenType.COMMENT, TokenType.EOF]
            ]
            
            print("   토큰들:")
            for token in meaningful_tokens:
                print(f"     {token.type.value}: '{token.value}'")
            
            # 통계
            stats = lexer.get_token_statistics()
            print(f"   토큰 수: {len(meaningful_tokens)}")
            print(f"   주요 타입: {', '.join([t.value for t in stats.keys() if stats[t] > 0 and t != TokenType.EOF])}")
            
        except Exception as e:
            print(f"   오류: {e}")
        
        print()


def validate_msl_syntax(text: str) -> Tuple[bool, List[str]]:
    """MSL 구문의 기본 유효성 검사"""
    try:
        lexer = MSLLexer(text)
        tokens = lexer.tokenize()
        errors = []
        
        # 괄호 균형 검사
        bracket_pairs = {
            TokenType.LPAREN: TokenType.RPAREN,
            TokenType.LBRACKET: TokenType.RBRACKET,
            TokenType.LBRACE: TokenType.RBRACE,
            TokenType.LANGLE: TokenType.RANGLE,
        }
        
        stack = []
        for token in tokens:
            if token.type in bracket_pairs:
                stack.append((token.type, token))
            elif token.type in bracket_pairs.values():
                if not stack:
                    errors.append(f"닫는 괄호가 매칭되지 않음: {token}")
                    continue
                
                open_type, open_token = stack.pop()
                expected_close = bracket_pairs[open_type]
                if token.type != expected_close:
                    errors.append(f"괄호 타입 불일치: {open_token} vs {token}")
        
        # 닫히지 않은 괄호 검사
        for open_type, open_token in stack:
            errors.append(f"닫히지 않은 괄호: {open_token}")
        
        # 알 수 없는 토큰 검사
        unknown_tokens = lexer.get_tokens_by_type(TokenType.UNKNOWN)
        for token in unknown_tokens:
            errors.append(f"알 수 없는 토큰: {token}")
        
        return len(errors) == 0, errors
        
    except Exception as e:
        return False, [f"렉서 오류: {e}"]


if __name__ == "__main__":
    demo_lexer()
    
    print("\n=== 구문 유효성 검사 테스트 ===")
    
    # 유효성 검사 테스트
    syntax_tests = [
        ("올바른 구문", "W, A, [SPACE, 500]", True),
        ("괄호 불균형", "W, [A, 500", False),
        ("알 수 없는 토큰", "W, A, @#$%", False),
        ("정상적인 복합", "(Q + E) * 3, @(100,200)", True),
    ]
    
    for name, text, expected_valid in syntax_tests:
        is_valid, errors = validate_msl_syntax(text)
        status = "✓" if is_valid == expected_valid else "✗"
        print(f"{status} {name}: '{text}' - {'유효' if is_valid else '오류'}")
        if errors:
            for error in errors:
                print(f"    - {error}") 