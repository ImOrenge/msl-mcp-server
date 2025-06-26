import pytest
from unittest.mock import Mock, patch
from src.msl.interpreter import MSLInterpreter
from src.msl.parser import MSLNode, TokenType

@pytest.fixture
def interpreter():
    return MSLInterpreter()

@pytest.fixture
def mock_pyautogui():
    with patch('src.msl.interpreter.pyautogui') as mock:
        yield mock

def test_click_command(interpreter, mock_pyautogui):
    # 클릭 명령 테스트
    node = MSLNode(TokenType.CLICK, {"x": 100, "y": 200})
    interpreter.execute(node)
    mock_pyautogui.click.assert_called_once_with(x=100, y=200)

def test_type_command(interpreter, mock_pyautogui):
    # 타이핑 명령 테스트
    node = MSLNode(TokenType.TYPE, {"text": "Hello, World!"})
    interpreter.execute(node)
    mock_pyautogui.write.assert_called_once_with("Hello, World!")

def test_press_command(interpreter, mock_pyautogui):
    # 키 입력 명령 테스트
    node = MSLNode(TokenType.PRESS, {"key": "enter"})
    interpreter.execute(node)
    mock_pyautogui.press.assert_called_once_with("enter")

def test_wait_command(interpreter, mock_pyautogui):
    # 대기 명령 테스트
    node = MSLNode(TokenType.WAIT, {"seconds": 3.0})
    interpreter.execute(node)
    mock_pyautogui.sleep.assert_called_once_with(3.0)

def test_move_command(interpreter, mock_pyautogui):
    # 마우스 이동 명령 테스트
    node = MSLNode(TokenType.MOVE, {"x": 300, "y": 400})
    interpreter.execute(node)
    mock_pyautogui.moveTo.assert_called_once_with(x=300, y=400)

def test_drag_command(interpreter, mock_pyautogui):
    # 드래그 명령 테스트
    node = MSLNode(TokenType.DRAG, {
        "start_x": 100,
        "start_y": 200,
        "end_x": 300,
        "end_y": 400
    })
    interpreter.execute(node)
    mock_pyautogui.moveTo.assert_called_once_with(x=100, y=200)
    mock_pyautogui.dragTo.assert_called_once_with(x=300, y=400)

def test_scroll_command(interpreter, mock_pyautogui):
    # 스크롤 명령 테스트
    node = MSLNode(TokenType.SCROLL, {"amount": 100})
    interpreter.execute(node)
    mock_pyautogui.scroll.assert_called_once_with(100)
    
    # 아래로 스크롤
    node = MSLNode(TokenType.SCROLL, {"amount": -100})
    interpreter.execute(node)
    mock_pyautogui.scroll.assert_called_with(-100)

def test_hotkey_command(interpreter, mock_pyautogui):
    # 단일 키 테스트
    node = MSLNode(TokenType.HOTKEY, {"key1": "ctrl"})
    interpreter.execute(node)
    mock_pyautogui.keyDown.assert_called_once_with("ctrl")
    mock_pyautogui.keyUp.assert_called_once_with("ctrl")
    
    mock_pyautogui.reset_mock()
    
    # 조합 키 테스트
    node = MSLNode(TokenType.HOTKEY, {"key1": "ctrl", "key2": "c"})
    interpreter.execute(node)
    mock_pyautogui.hotkey.assert_called_once_with("ctrl", "c")

def test_sequence_command(interpreter, mock_pyautogui):
    # 명령 시퀀스 테스트
    sequence = MSLNode(TokenType.SEQUENCE)
    sequence.children = [
        MSLNode(TokenType.MOVE, {"x": 100, "y": 100}),
        MSLNode(TokenType.CLICK, {"x": 100, "y": 100}),
        MSLNode(TokenType.WAIT, {"seconds": 1.0}),
        MSLNode(TokenType.TYPE, {"text": "test"})
    ]
    
    interpreter.execute(sequence)
    
    assert mock_pyautogui.moveTo.call_count == 1
    assert mock_pyautogui.click.call_count == 1
    assert mock_pyautogui.sleep.call_count == 1
    assert mock_pyautogui.write.call_count == 1

def test_stop_execution(interpreter, mock_pyautogui):
    # 실행 중지 테스트
    sequence = MSLNode(TokenType.SEQUENCE)
    sequence.children = [
        MSLNode(TokenType.WAIT, {"seconds": 1.0}),
        MSLNode(TokenType.WAIT, {"seconds": 1.0}),
        MSLNode(TokenType.WAIT, {"seconds": 1.0})
    ]
    
    # 첫 번째 대기 후 중지
    def stop_after_first_wait(*args, **kwargs):
        interpreter.stop_flag = True
    
    mock_pyautogui.sleep.side_effect = stop_after_first_wait
    interpreter.execute(sequence)
    
    # 첫 번째 대기만 실행되었는지 확인
    assert mock_pyautogui.sleep.call_count == 1

def test_error_handling(interpreter, mock_pyautogui):
    # 잘못된 매개변수 테스트
    node = MSLNode(TokenType.CLICK, {"x": "invalid", "y": 200})
    with pytest.raises(ValueError):
        interpreter.execute(node)
    
    # 잘못된 명령 타입 테스트
    node = MSLNode("INVALID_TYPE")
    with pytest.raises(ValueError):
        interpreter.execute(node)
    
    # PyAutoGUI 예외 처리 테스트
    mock_pyautogui.click.side_effect = Exception("PyAutoGUI Error")
    node = MSLNode(TokenType.CLICK, {"x": 100, "y": 200})
    with pytest.raises(Exception):
        interpreter.execute(node) 