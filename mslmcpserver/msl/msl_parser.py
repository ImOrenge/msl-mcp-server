"""
MSL (Macro Scripting Language) 파서 (Parser)
Lexer가 생성한 토큰을 받아서 AST(Abstract Syntax Tree)로 변환합니다.

파싱 우선순위 (높은 순):
1. 그룹화: ( )
2. 토글: ~
3. 반복: *
4. 연속입력: &
5. 홀드연결: >
6. 병렬실행: |
7. 동시실행: +
8. 순차실행: ,

타이밍 제어:
- (숫자): 지연 시간
- [숫자]: 홀드 시간
- {숫자}: 반복 간격
- <숫자>: 페이드 시간
"""

import re
from typing import List, Optional, Union, Dict
from .msl_lexer import MSLLexer, Token, TokenType
from .msl_ast import *


class ParseError(Exception):
    """MSL 파싱 오류 - 구문 분석 중 발생하는 오류를 처리합니다"""
    
    def __init__(self, message: str, token: Optional[Token] = None):
        """
        파싱 오류 초기화
        
        Args:
            message (str): 오류 메시지
            token (Token, optional): 오류가 발생한 토큰
        """
        self.message = message
        self.token = token
        
        if token:
            super().__init__(f"Line {token.line}, Column {token.column}: {message}")
        else:
            super().__init__(message)


class MSLParser:
    """MSL 파서 - 토큰을 구문 트리로 변환하는 핵심 컴포넌트"""
    
    def __init__(self):
        """MSL Parser 초기화"""
        self.tokens: List[Token] = []
        self.current_position = 0
        self.current_token: Optional[Token] = None
        
        # 변수 저장소 (파싱 시점에는 체크만)
        self.variables: Dict[str, MSLNode] = {}
    
    def parse(self, text: str) -> MSLNode:
        """
        MSL 스크립트를 파싱하여 AST를 생성합니다.
        
        Args:
            text (str): MSL 스크립트 텍스트
            
        Returns:
            MSLNode: 루트 AST 노드
            
        Raises:
            ParseError: 파싱 오류 발생 시
            
        Example:
            >>> parser = MSLParser()
            >>> ast = parser.parse("W(500),A")
            >>> # SequentialNode with KeyNode and DelayNode
        """
        # 1. 토큰화
        lexer = MSLLexer()
        self.tokens = lexer.tokenize(text)
        
        # 2. 주석 및 공백 제거 - 파싱에 불필요한 토큰 제거
        self.tokens = [token for token in self.tokens 
                      if token.type not in [TokenType.COMMENT, TokenType.WHITESPACE]]
        
        # 3. 토큰 유효성 검사
        errors = lexer.validate_tokens(self.tokens)
        if errors:
            raise ParseError(f"토큰 오류: {', '.join(errors)}")
        
        # 4. 파싱 초기화
        self.current_position = 0
        self.current_token = self.tokens[0] if self.tokens else None
        
        # 5. 파싱 시작
        if not self.tokens or self.tokens[0].type == TokenType.EOF:
            raise ParseError("빈 스크립트입니다")
        
        try:
            ast = self.parse_expression()
            
            # 6. 모든 토큰이 소비되었는지 확인
            if self.current_token and self.current_token.type != TokenType.EOF:
                raise ParseError(f"예상치 못한 토큰: {self.current_token.value}", self.current_token)
            
            return ast
            
        except IndexError:
            raise ParseError("예상치 못한 스크립트 끝")
    
    def advance(self) -> Optional[Token]:
        """다음 토큰으로 이동합니다"""
        if self.current_position < len(self.tokens) - 1:
            self.current_position += 1
            self.current_token = self.tokens[self.current_position]
        else:
            self.current_token = None
        return self.current_token
    
    def peek(self, offset: int = 1) -> Optional[Token]:
        """앞으로 offset만큼 떨어진 토큰 확인 (이동하지 않음)"""
        pos = self.current_position + offset
        if 0 <= pos < len(self.tokens):
            return self.tokens[pos]
        return None
    
    def expect(self, token_type: TokenType) -> Token:
        """현재 토큰이 예상 타입인지 확인하고 다음으로 이동"""
        if not self.current_token or self.current_token.type != token_type:
            expected = token_type.value
            actual = self.current_token.value if self.current_token else "EOF"
            raise ParseError(f"예상: {expected}, 실제: {actual}", self.current_token)
        
        token = self.current_token
        self.advance()
        return token
    
    def match(self, *token_types: TokenType) -> bool:
        """현재 토큰이 주어진 타입들 중 하나인지 확인"""
        if not self.current_token:
            return False
        return self.current_token.type in token_types
    
    def parse_expression(self) -> MSLNode:
        """표현식 파싱 (최상위 레벨) - 순차 실행부터 시작"""
        return self.parse_sequential()
    
    def parse_sequential(self) -> MSLNode:
        """순차 실행 파싱 (가장 낮은 우선순위: ,) - W,A,S,D"""
        left = self.parse_simultaneous()
        
        if self.match(TokenType.SEQUENTIAL):
            sequential_node = SequentialNode(self._get_position())
            sequential_node.add_child(left)
            
            while self.match(TokenType.SEQUENTIAL):
                self.advance()  # , 소비
                right = self.parse_simultaneous()
                sequential_node.add_child(right)
            
            return sequential_node
        
        return left
    
    def parse_simultaneous(self) -> MSLNode:
        """동시 실행 파싱 (+) - Ctrl+C"""
        left = self.parse_parallel()
        
        if self.match(TokenType.SIMULTANEOUS):
            simultaneous_node = SimultaneousNode(self._get_position())
            simultaneous_node.add_child(left)
            
            while self.match(TokenType.SIMULTANEOUS):
                self.advance()  # + 소비
                right = self.parse_parallel()
                simultaneous_node.add_child(right)
            
            return simultaneous_node
        
        return left
    
    def parse_parallel(self) -> MSLNode:
        """병렬 실행 파싱 (|) - (W,A)|(S,D)"""
        left = self.parse_hold_chain()
        
        if self.match(TokenType.PARALLEL):
            parallel_node = ParallelNode(self._get_position())
            parallel_node.add_child(left)
            
            while self.match(TokenType.PARALLEL):
                self.advance()  # | 소비
                right = self.parse_hold_chain()
                parallel_node.add_child(right)
            
            return parallel_node
        
        return left
    
    def parse_hold_chain(self) -> MSLNode:
        """홀드 연결 파싱 (>) - W>A>S"""
        left = self.parse_continuous()
        
        if self.match(TokenType.HOLD_CHAIN):
            hold_chain_node = HoldChainNode(self._get_position())
            hold_chain_node.add_child(left)
            
            while self.match(TokenType.HOLD_CHAIN):
                self.advance()  # > 소비
                right = self.parse_continuous()
                hold_chain_node.add_child(right)
            
            return hold_chain_node
        
        return left
    
    def parse_continuous(self) -> MSLNode:
        """연속 입력 파싱 (&) - Space&1000"""
        left = self.parse_repeat()
        
        if self.match(TokenType.CONTINUOUS):
            self.advance()  # & 소비
            
            # 연속 시간 파싱
            if not self.match(TokenType.NUMBER):
                raise ParseError("연속 입력(&) 뒤에는 시간(숫자)이 와야 합니다", self.current_token)
            
            duration_token = self.expect(TokenType.NUMBER)
            duration = float(duration_token.value)
            
            continuous_node = ContinuousNode(self._get_position())
            continuous_node.add_child(left)
            continuous_node.duration = duration
            
            return continuous_node
        
        return left
    
    def parse_repeat(self) -> MSLNode:
        """반복 파싱 (*) - W*5"""
        left = self.parse_toggle()
        
        if self.match(TokenType.REPEAT):
            self.advance()  # * 소비
            
            # 반복 횟수 파싱
            if not self.match(TokenType.NUMBER):
                raise ParseError("반복(*) 뒤에는 횟수(숫자)가 와야 합니다", self.current_token)
            
            count_token = self.expect(TokenType.NUMBER)
            count = int(float(count_token.value))  # 소수점도 처리하되 정수로 변환
            
            repeat_node = RepeatNode(self._get_position())
            repeat_node.add_child(left)
            repeat_node.count = count
            
            # 반복 간격 파싱 {숫자}
            if self.match(TokenType.INTERVAL_START):
                self.advance()  # { 소비
                
                if not self.match(TokenType.NUMBER):
                    raise ParseError("반복 간격({) 뒤에는 시간(숫자)이 와야 합니다", self.current_token)
                
                interval_token = self.expect(TokenType.NUMBER)
                interval = float(interval_token.value)
                repeat_node.interval = interval
                
                self.expect(TokenType.INTERVAL_END)  # } 소비
            
            return repeat_node
        
        return left
    
    def parse_toggle(self) -> MSLNode:
        """토글 파싱 (~) - ~CapsLock"""
        if self.match(TokenType.TOGGLE):
            self.advance()  # ~ 소비
            
            base_node = self.parse_primary()
            
            toggle_node = ToggleNode(self._get_position())
            toggle_node.add_child(base_node)
            
            return toggle_node
        
        return self.parse_primary()
    
    def parse_primary(self) -> MSLNode:
        """기본 요소 파싱 - 키, 숫자, 변수, 마우스, 그룹 등"""
        if not self.current_token:
            raise ParseError("예상치 못한 스크립트 끝")
        
        # 그룹 처리 (...)
        if self.match(TokenType.DELAY_START):
            return self.parse_group()
        
        # 키 노드
        elif self.match(TokenType.KEY):
            key_token = self.expect(TokenType.KEY)
            key_node = KeyNode(self._get_position(key_token))
            key_node.key = key_token.value
            
            # 타이밍 수정자 확인
            return self.parse_timing_modifiers(key_node)
        
        # 변수 노드
        elif self.match(TokenType.VARIABLE):
            var_token = self.expect(TokenType.VARIABLE)
            var_node = VariableNode(self._get_position(var_token))
            var_node.name = var_token.value[1:]  # $ 제거
            
            return var_node
        
        # 마우스 좌표 노드
        elif self.match(TokenType.MOUSE_COORD):
            coord_token = self.expect(TokenType.MOUSE_COORD)
            
            # @(x,y) 파싱
            coord_str = coord_token.value[2:-1]  # @( 와 ) 제거
            x_str, y_str = coord_str.split(',')
            x = int(x_str.strip())
            y = int(y_str.strip())
            
            mouse_node = MouseNode(self._get_position(coord_token))
            mouse_node.x = x
            mouse_node.y = y
            
            return mouse_node
        
        # 휠 노드
        elif self.match(TokenType.WHEEL):
            wheel_token = self.expect(TokenType.WHEEL)
            
            # wheel+3 또는 wheel-2 파싱
            wheel_str = wheel_token.value
            direction = 1 if '+' in wheel_str else -1
            amount_str = wheel_str.split('+' if '+' in wheel_str else '-')[1]
            amount = int(amount_str) if amount_str else 1
            
            wheel_node = WheelNode(self._get_position(wheel_token))
            wheel_node.direction = direction
            wheel_node.amount = amount
            
            return wheel_node
        
        # 숫자 노드 (단독으로 사용되는 경우)
        elif self.match(TokenType.NUMBER):
            number_token = self.expect(TokenType.NUMBER)
            number_node = NumberNode(self._get_position(number_token))
            number_node.value = float(number_token.value)
            
            return number_node
        
        else:
            raise ParseError(f"예상치 못한 토큰: {self.current_token.value}", self.current_token)
    
    def parse_group(self) -> MSLNode:
        """그룹 파싱 (...) - 괄호로 묶인 표현식"""
        self.expect(TokenType.DELAY_START)  # ( 소비
        
        # 그룹 내부 표현식 파싱
        inner_expr = self.parse_expression()
        
        self.expect(TokenType.DELAY_END)  # ) 소비
        
        return inner_expr
    
    def parse_timing_modifiers(self, base_node: MSLNode) -> MSLNode:
        """타이밍 수정자 파싱 - 키 뒤에 오는 지연, 홀드 등"""
        result = base_node
        
        # 지연 시간 (숫자) - W(500)
        if self.match(TokenType.DELAY_START):
            self.advance()  # ( 소비
            
            if not self.match(TokenType.NUMBER):
                raise ParseError("지연 시간 괄호 안에는 숫자가 와야 합니다", self.current_token)
            
            delay_token = self.expect(TokenType.NUMBER)
            delay = float(delay_token.value)
            
            self.expect(TokenType.DELAY_END)  # ) 소비
            
            delay_node = DelayNode(self._get_position())
            delay_node.add_child(result)
            delay_node.duration = delay
            result = delay_node
        
        # 홀드 시간 [숫자] - W[1000]
        if self.match(TokenType.HOLD_START):
            self.advance()  # [ 소비
            
            if not self.match(TokenType.NUMBER):
                raise ParseError("홀드 시간 괄호 안에는 숫자가 와야 합니다", self.current_token)
            
            hold_token = self.expect(TokenType.NUMBER)
            hold_duration = float(hold_token.value)
            
            self.expect(TokenType.HOLD_END)  # ] 소비
            
            hold_node = HoldNode(self._get_position())
            hold_node.add_child(result)
            hold_node.duration = hold_duration
            result = hold_node
        
        # 페이드 시간 <숫자> - W<500>
        if self.match(TokenType.FADE_START):
            self.advance()  # < 소비
            
            if not self.match(TokenType.NUMBER):
                raise ParseError("페이드 시간 괄호 안에는 숫자가 와야 합니다", self.current_token)
            
            fade_token = self.expect(TokenType.NUMBER)
            fade_duration = float(fade_token.value)
            
            # fade end는 '>' 인데 이미 HOLD_CHAIN으로 사용되므로 특별 처리
            # 실제로는 구문 분석에서 처리가 복잡할 수 있으므로 일단 간단히 처리
            
            fade_node = FadeNode(self._get_position())
            fade_node.add_child(result)
            fade_node.duration = fade_duration
            result = fade_node
        
        return result
    
    def _get_position(self, token: Optional[Token] = None) -> Position:
        """현재 위치 정보 생성"""
        if token:
            return Position(token.line, token.column)
        elif self.current_token:
            return Position(self.current_token.line, self.current_token.column)
        else:
            return Position(1, 1)
    
    def analyze_syntax(self, text: str) -> Dict[str, any]:
        """
        MSL 스크립트의 구문을 분석하여 상세 정보를 반환합니다.
        
        Args:
            text (str): MSL 스크립트
            
        Returns:
            Dict: 분석 결과 (AST, 오류, 통계 등)
        """
        try:
            ast = self.parse(text)
            
            return {
                'success': True,
                'ast': ast,
                'errors': [],
                'warnings': [],
                'statistics': self._analyze_ast_statistics(ast)
            }
        
        except ParseError as e:
            return {
                'success': False,
                'ast': None,
                'errors': [str(e)],
                'warnings': [],
                'statistics': {}
            }
    
    def _analyze_ast_statistics(self, ast: MSLNode) -> Dict[str, int]:
        """AST 통계 분석"""
        stats = {
            'total_nodes': 0,
            'key_nodes': 0,
            'timing_nodes': 0,
            'operator_nodes': 0,
            'max_depth': 0
        }
        
        def count_nodes(node: MSLNode, depth: int = 0):
            stats['total_nodes'] += 1
            stats['max_depth'] = max(stats['max_depth'], depth)
            
            if isinstance(node, KeyNode):
                stats['key_nodes'] += 1
            elif isinstance(node, (DelayNode, HoldNode, FadeNode)):
                stats['timing_nodes'] += 1
            elif isinstance(node, (SequentialNode, SimultaneousNode, ParallelNode)):
                stats['operator_nodes'] += 1
            
            for child in node.children:
                count_nodes(child, depth + 1)
        
        count_nodes(ast)
        return stats


def demo_parser():
    """MSL Parser 데모 함수 - 다양한 MSL 스크립트 파싱 예제"""
    parser = MSLParser()
    
    demo_scripts = [
        # 기본 파싱 테스트
        ("기본 키", "W"),
        ("순차 실행", "W,A,S,D"),
        ("동시 실행", "Ctrl+C"),
        ("지연 시간", "W(500)"),
        ("홀드 시간", "W[1000]"),
        ("반복", "W*5"),
        ("연속 입력", "Space&2000"),
        ("토글", "~CapsLock"),
        
        # 복합 파싱 테스트
        ("게임 콤보", "Q(100)W(150)E(200)R"),
        ("복합 매크로", "Shift[2000]+(W,A,S,D)"),
        ("마우스 제어", "@(100,200)"),
        ("휠 제어", "wheel+3"),
        ("변수 사용", "$combo1"),
        
        # 복잡한 구조
        ("홀드 체인", "W>A>S>D"),
        ("병렬 실행", "(W,A)|(S,D)"),
        ("반복 간격", "W*5{200}"),
        
        # 오류 테스트
        ("잘못된 구문", "W("),
        ("빈 스크립트", ""),
    ]
    
    print("=== MSL Parser 데모 ===")
    print("MSL 스크립트를 구문 트리로 변환하는 예제\n")
    
    for name, script in demo_scripts:
        print(f"📝 {name}: {script}")
        
        try:
            result = parser.analyze_syntax(script)
            
            if result['success']:
                print("   ✅ 파싱 성공")
                print(f"   📊 통계: {result['statistics']}")
                print(f"   🌳 AST 루트: {type(result['ast']).__name__}")
            else:
                print("   ❌ 파싱 실패")
                for error in result['errors']:
                    print(f"      오류: {error}")
        
        except Exception as e:
            print(f"   💥 예외 발생: {e}")
        
        print()


if __name__ == "__main__":
    demo_parser() 