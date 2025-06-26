import pytest
from src.msl.parser import MSLLexer, Token, TokenType

def test_lexer_click_command():
    """클릭 명령 렉서 테스트"""
    lexer = MSLLexer("click(100, 200)")
    tokens = list(lexer.tokenize())

    assert len(tokens) == 6
    assert tokens[0] == Token(TokenType.CLICK, "click")
    assert tokens[1] == Token(TokenType.LPAREN, "(")
    assert tokens[2] == Token(TokenType.NUMBER, "100")
    assert tokens[3] == Token(TokenType.COMMA, ",")
    assert tokens[4] == Token(TokenType.NUMBER, "200")
    assert tokens[5] == Token(TokenType.RPAREN, ")")

def test_lexer_type_command():
    """타이핑 명령 렉서 테스트"""
    lexer = MSLLexer('type("Hello, World!")')
    tokens = list(lexer.tokenize())

    assert len(tokens) == 4
    assert tokens[0] == Token(TokenType.TYPE, "type")
    assert tokens[1] == Token(TokenType.LPAREN, "(")
    assert tokens[2] == Token(TokenType.STRING, "Hello, World!")
    assert tokens[3] == Token(TokenType.RPAREN, ")")

def test_lexer_press_command():
    """키 입력 명령 렉서 테스트"""
    lexer = MSLLexer('press("enter")')
    tokens = list(lexer.tokenize())

    assert len(tokens) == 4
    assert tokens[0] == Token(TokenType.PRESS, "press")
    assert tokens[1] == Token(TokenType.LPAREN, "(")
    assert tokens[2] == Token(TokenType.STRING, "enter")
    assert tokens[3] == Token(TokenType.RPAREN, ")")

def test_lexer_wait_command():
    """대기 명령 렉서 테스트"""
    lexer = MSLLexer("wait(1.5)")
    tokens = list(lexer.tokenize())

    assert len(tokens) == 4
    assert tokens[0] == Token(TokenType.WAIT, "wait")
    assert tokens[1] == Token(TokenType.LPAREN, "(")
    assert tokens[2] == Token(TokenType.NUMBER, "1.5")
    assert tokens[3] == Token(TokenType.RPAREN, ")")

def test_lexer_invalid_command():
    """잘못된 명령 렉서 테스트"""
    lexer = MSLLexer("invalid()")
    with pytest.raises(ValueError):
        list(lexer.tokenize())

def test_lexer_whitespace_handling():
    """공백 처리 렉서 테스트"""
    lexer = MSLLexer("  click  (  100  ,  200  )  ")
    tokens = list(lexer.tokenize())

    assert len(tokens) == 6
    assert tokens[0] == Token(TokenType.CLICK, "click")
    assert tokens[1] == Token(TokenType.LPAREN, "(")
    assert tokens[2] == Token(TokenType.NUMBER, "100")
    assert tokens[3] == Token(TokenType.COMMA, ",")
    assert tokens[4] == Token(TokenType.NUMBER, "200")
    assert tokens[5] == Token(TokenType.RPAREN, ")")

def test_lexer_string_escaping():
    """문자열 이스케이프 렉서 테스트"""
    lexer = MSLLexer('type("Hello\\"World")')
    tokens = list(lexer.tokenize())

    assert len(tokens) == 4
    assert tokens[2] == Token(TokenType.STRING, 'Hello"World') 