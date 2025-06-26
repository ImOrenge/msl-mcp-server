"""
MSL 파서 테스트
"""
import pytest
from src.msl.parser import MSLParser

def test_parser_initialization():
    """파서 초기화 테스트"""
    parser = MSLParser()
    assert parser is not None
    assert parser.tokens == []
    assert parser.current_pos == 0

def test_parse_empty_code():
    """빈 코드 파싱 테스트"""
    parser = MSLParser()
    ast = parser.parse("")
    assert ast["type"] == "program"
    assert ast["body"] == []

def test_parse_single_command():
    """단일 명령어 파싱 테스트"""
    parser = MSLParser()
    code = "click 100 200"
    ast = parser.parse(code)
    
    assert ast["type"] == "program"
    assert len(ast["body"]) == 1
    
    command = ast["body"][0]
    assert command["type"] == "command"
    assert command["name"] == "click"
    assert command["params"] == ["100", "200"]

def test_parse_multiple_commands():
    """여러 명령어 파싱 테스트"""
    parser = MSLParser()
    code = """
    click 100 200
    type Hello World
    wait 1000
    """
    ast = parser.parse(code)
    
    assert ast["type"] == "program"
    assert len(ast["body"]) == 3
    
    commands = ast["body"]
    assert commands[0]["type"] == "command"
    assert commands[0]["name"] == "click"
    assert commands[0]["params"] == ["100", "200"]
    
    assert commands[1]["type"] == "command"
    assert commands[1]["name"] == "type"
    assert commands[1]["params"] == ["Hello", "World"]
    
    assert commands[2]["type"] == "command"
    assert commands[2]["name"] == "wait"
    assert commands[2]["params"] == ["1000"]

def test_parse_comments():
    """주석 파싱 테스트"""
    parser = MSLParser()
    code = """
    # This is a comment
    click 100 200  # Click at position
    type Hello  # Type text
    """
    ast = parser.parse(code)
    
    assert ast["type"] == "program"
    assert len(ast["body"]) == 2
    
    commands = ast["body"]
    assert commands[0]["type"] == "command"
    assert commands[0]["name"] == "click"
    assert commands[0]["params"] == ["100", "200"]
    
    assert commands[1]["type"] == "command"
    assert commands[1]["name"] == "type"
    assert commands[1]["params"] == ["Hello"]

def test_parse_invalid_command():
    """잘못된 명령어 파싱 테스트"""
    parser = MSLParser()
    code = "invalid_command 123"
    ast = parser.parse(code)
    
    # 파싱은 성공하지만 검증에서 실패해야 함
    errors = parser.validate(ast)
    assert len(errors) > 0
    assert "Unknown command" in errors[0] 