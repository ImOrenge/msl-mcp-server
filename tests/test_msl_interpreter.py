"""
MSL 인터프리터 테스트
"""
import pytest
from src.msl.interpreter import MSLInterpreter
from unittest.mock import patch, MagicMock

@pytest.fixture
def interpreter():
    """인터프리터 fixture"""
    return MSLInterpreter()

def test_interpreter_initialization(interpreter):
    """인터프리터 초기화 테스트"""
    assert interpreter is not None
    assert len(interpreter.commands) == 6  # 기본 명령어 6개
    assert all(callable(cmd) for cmd in interpreter.commands.values())

def test_execute_empty_program(interpreter):
    """빈 프로그램 실행 테스트"""
    ast = {
        "type": "program",
        "body": []
    }
    result = interpreter.execute(ast)
    assert result["success"] is True
    assert len(result["results"]) == 0
    assert len(result["errors"]) == 0

@patch("pyautogui.click")
def test_execute_click_command(mock_click, interpreter):
    """click 명령어 실행 테스트"""
    ast = {
        "type": "program",
        "body": [{
            "type": "command",
            "name": "click",
            "params": ["100", "200"]
        }]
    }
    result = interpreter.execute(ast)
    
    assert result["success"] is True
    assert len(result["results"]) == 1
    assert result["results"][0]["action"] == "click"
    assert result["results"][0]["position"] == (100, 200)
    mock_click.assert_called_once_with(x=100, y=200)

@patch("pyautogui.write")
def test_execute_type_command(mock_write, interpreter):
    """type 명령어 실행 테스트"""
    ast = {
        "type": "program",
        "body": [{
            "type": "command",
            "name": "type",
            "params": ["Hello", "World"]
        }]
    }
    result = interpreter.execute(ast)
    
    assert result["success"] is True
    assert len(result["results"]) == 1
    assert result["results"][0]["action"] == "type"
    assert result["results"][0]["text"] == "Hello World"
    mock_write.assert_called_once_with("Hello World")

@patch("time.sleep")
def test_execute_wait_command(mock_sleep, interpreter):
    """wait 명령어 실행 테스트"""
    ast = {
        "type": "program",
        "body": [{
            "type": "command",
            "name": "wait",
            "params": ["1.5"]
        }]
    }
    result = interpreter.execute(ast)
    
    assert result["success"] is True
    assert len(result["results"]) == 1
    assert result["results"][0]["action"] == "wait"
    assert result["results"][0]["seconds"] == 1.5
    mock_sleep.assert_called_once_with(1.5)

@patch("pyautogui.moveTo")
def test_execute_move_command(mock_move, interpreter):
    """move 명령어 실행 테스트"""
    ast = {
        "type": "program",
        "body": [{
            "type": "command",
            "name": "move",
            "params": ["300", "400"]
        }]
    }
    result = interpreter.execute(ast)
    
    assert result["success"] is True
    assert len(result["results"]) == 1
    assert result["results"][0]["action"] == "move"
    assert result["results"][0]["position"] == (300, 400)
    mock_move.assert_called_once_with(x=300, y=400)

@patch("pyautogui.press")
def test_execute_press_command(mock_press, interpreter):
    """press 명령어 실행 테스트"""
    ast = {
        "type": "program",
        "body": [{
            "type": "command",
            "name": "press",
            "params": ["enter"]
        }]
    }
    result = interpreter.execute(ast)
    
    assert result["success"] is True
    assert len(result["results"]) == 1
    assert result["results"][0]["action"] == "press"
    assert result["results"][0]["key"] == "enter"
    mock_press.assert_called_once_with("enter")

@patch("pyautogui.hotkey")
def test_execute_hotkey_command(mock_hotkey, interpreter):
    """hotkey 명령어 실행 테스트"""
    ast = {
        "type": "program",
        "body": [{
            "type": "command",
            "name": "hotkey",
            "params": ["ctrl", "c"]
        }]
    }
    result = interpreter.execute(ast)
    
    assert result["success"] is True
    assert len(result["results"]) == 1
    assert result["results"][0]["action"] == "hotkey"
    assert result["results"][0]["keys"] == ["ctrl", "c"]
    mock_hotkey.assert_called_once_with("ctrl", "c")

def test_execute_invalid_program(interpreter):
    """잘못된 프로그램 실행 테스트"""
    ast = {
        "type": "invalid",
        "body": []
    }
    result = interpreter.execute(ast)
    
    assert result["success"] is False
    assert len(result["results"]) == 0
    assert len(result["errors"]) == 1
    assert "Invalid AST" in result["errors"][0]

def test_execute_invalid_command(interpreter):
    """잘못된 명령어 실행 테스트"""
    ast = {
        "type": "program",
        "body": [{
            "type": "command",
            "name": "invalid_command",
            "params": []
        }]
    }
    result = interpreter.execute(ast)
    
    assert result["success"] is False
    assert len(result["results"]) == 0
    assert len(result["errors"]) == 1
    assert "Unknown command" in result["errors"][0] 