import pytest
from src.msl.parser import MSLParser, MSLNode, TokenType

def test_click_command():
    parser = MSLParser()
    
    # 기본 클릭 명령
    ast = parser.parse("click(100, 200)")
    assert isinstance(ast, MSLNode)
    assert ast.type == TokenType.CLICK
    assert ast.parameters["x"] == 100
    assert ast.parameters["y"] == 200

def test_type_command():
    parser = MSLParser()
    
    # 문자열 입력 명령
    ast = parser.parse('type("Hello, World!")')
    assert isinstance(ast, MSLNode)
    assert ast.type == TokenType.TYPE
    assert ast.parameters["text"] == "Hello, World!"

def test_press_command():
    parser = MSLParser()
    
    # 키 입력 명령
    ast = parser.parse('press("enter")')
    assert isinstance(ast, MSLNode)
    assert ast.type == TokenType.PRESS
    assert ast.parameters["key"] == "enter"

def test_wait_command():
    parser = MSLParser()
    
    # 대기 명령
    ast = parser.parse("wait(3)")
    assert isinstance(ast, MSLNode)
    assert ast.type == TokenType.WAIT
    assert ast.parameters["seconds"] == 3.0

def test_move_command():
    parser = MSLParser()
    
    # 마우스 이동 명령
    ast = parser.parse("move(300, 400)")
    assert isinstance(ast, MSLNode)
    assert ast.type == TokenType.MOVE
    assert ast.parameters["x"] == 300
    assert ast.parameters["y"] == 400

def test_drag_command():
    parser = MSLParser()
    
    # 드래그 명령
    ast = parser.parse("drag(100, 200, 300, 400)")
    assert isinstance(ast, MSLNode)
    assert ast.type == TokenType.DRAG
    assert ast.parameters["start_x"] == 100
    assert ast.parameters["start_y"] == 200
    assert ast.parameters["end_x"] == 300
    assert ast.parameters["end_y"] == 400

def test_scroll_command():
    parser = MSLParser()
    
    # 스크롤 명령
    ast = parser.parse("scroll(100)")  # 위로 스크롤
    assert isinstance(ast, MSLNode)
    assert ast.type == TokenType.SCROLL
    assert ast.parameters["amount"] == 100
    
    ast = parser.parse("scroll(-100)")  # 아래로 스크롤
    assert isinstance(ast, MSLNode)
    assert ast.type == TokenType.SCROLL
    assert ast.parameters["amount"] == -100

def test_hotkey_command():
    parser = MSLParser()
    
    # 단일 키
    ast = parser.parse('hotkey("ctrl")')
    assert isinstance(ast, MSLNode)
    assert ast.type == TokenType.HOTKEY
    assert ast.parameters["key1"] == "ctrl"
    assert "key2" not in ast.parameters
    
    # 조합 키
    ast = parser.parse('hotkey("ctrl", "c")')
    assert isinstance(ast, MSLNode)
    assert ast.type == TokenType.HOTKEY
    assert ast.parameters["key1"] == "ctrl"
    assert ast.parameters["key2"] == "c"

def test_sequence_command():
    parser = MSLParser()
    
    # 명령 시퀀스
    script = """
    move(100, 100)
    click(100, 100)
    wait(1)
    type("test")
    """
    ast = parser.parse(script)
    assert isinstance(ast, MSLNode)
    assert ast.type == TokenType.SEQUENCE
    assert len(ast.children) == 4
    
    # 각 명령 확인
    assert ast.children[0].type == TokenType.MOVE
    assert ast.children[1].type == TokenType.CLICK
    assert ast.children[2].type == TokenType.WAIT
    assert ast.children[3].type == TokenType.TYPE

def test_invalid_commands():
    parser = MSLParser()
    
    # 잘못된 구문
    with pytest.raises(Exception):
        parser.parse("")
    
    with pytest.raises(Exception):
        parser.parse("invalid()")
    
    with pytest.raises(Exception):
        parser.parse("click()")  # 매개변수 누락
    
    with pytest.raises(Exception):
        parser.parse("click(a, b)")  # 잘못된 매개변수 타입
    
    with pytest.raises(Exception):
        parser.parse("click(100)")  # 매개변수 개수 부족
    
    with pytest.raises(Exception):
        parser.parse("click(100, 200, 300)")  # 매개변수 개수 초과 