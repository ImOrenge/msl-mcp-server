import pytest
from src.msl.parser import TokenType

def test_token_types():
    """토큰 타입 테스트"""
    # 기본 명령어 토큰
    assert TokenType.CLICK.value == "CLICK"
    assert TokenType.TYPE.value == "TYPE"
    assert TokenType.PRESS.value == "PRESS"
    assert TokenType.WAIT.value == "WAIT"
    assert TokenType.MOVE.value == "MOVE"
    assert TokenType.DRAG.value == "DRAG"
    assert TokenType.SCROLL.value == "SCROLL"
    assert TokenType.HOTKEY.value == "HOTKEY"

    # 구문 분석 토큰
    assert TokenType.LPAREN.value == "LPAREN"
    assert TokenType.RPAREN.value == "RPAREN"
    assert TokenType.COMMA.value == "COMMA"
    assert TokenType.NUMBER.value == "NUMBER"
    assert TokenType.STRING.value == "STRING"
    assert TokenType.IDENTIFIER.value == "IDENTIFIER"
    assert TokenType.EOF.value == "EOF"

def test_token_type_comparison():
    """토큰 타입 비교 테스트"""
    assert TokenType.CLICK != TokenType.TYPE
    assert TokenType.LPAREN != TokenType.RPAREN
    assert TokenType.NUMBER != TokenType.STRING

def test_token_type_string_representation():
    """토큰 타입 문자열 표현 테스트"""
    assert str(TokenType.CLICK) == "CLICK"
    assert str(TokenType.TYPE) == "TYPE"
    assert str(TokenType.PRESS) == "PRESS"

def test_token_type_command_group():
    """명령어 토큰 그룹 테스트"""
    command_tokens = {
        TokenType.CLICK,
        TokenType.TYPE,
        TokenType.PRESS,
        TokenType.WAIT,
        TokenType.MOVE,
        TokenType.DRAG,
        TokenType.SCROLL,
        TokenType.HOTKEY
    }
    
    # 모든 명령어 토큰이 고유한지 확인
    assert len(command_tokens) == 8

def test_token_type_syntax_group():
    """구문 분석 토큰 그룹 테스트"""
    syntax_tokens = {
        TokenType.LPAREN,
        TokenType.RPAREN,
        TokenType.COMMA,
        TokenType.NUMBER,
        TokenType.STRING,
        TokenType.IDENTIFIER,
        TokenType.EOF
    }
    
    # 모든 구문 분석 토큰이 고유한지 확인
    assert len(syntax_tokens) == 7 