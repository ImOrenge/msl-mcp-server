import pytest
from src.msl.generator import MSLGenerator
from src.prompt.analyzer import Intent

@pytest.fixture
def generator():
    return MSLGenerator()

def test_click_command(generator):
    # 기본 클릭 명령
    intent = Intent(
        action="click",
        parameters={"x": 100, "y": 200},
        confidence=1.0,
        original_text="100, 200 클릭해줘"
    )
    script = generator.generate(intent)
    assert script == "click(100, 200)"

def test_type_command(generator):
    # 문자열 입력 명령
    intent = Intent(
        action="type",
        parameters={"text": "Hello, World!"},
        confidence=1.0,
        original_text='"Hello, World!" 입력해줘'
    )
    script = generator.generate(intent)
    assert script == 'type("Hello, World!")'

def test_press_command(generator):
    # 키 입력 명령
    intent = Intent(
        action="press",
        parameters={"key": "enter"},
        confidence=1.0,
        original_text="엔터 키 눌러줘"
    )
    script = generator.generate(intent)
    assert script == 'press("enter")'

def test_wait_command(generator):
    # 대기 명령
    intent = Intent(
        action="wait",
        parameters={"seconds": 3.0},
        confidence=1.0,
        original_text="3초 기다려줘"
    )
    script = generator.generate(intent)
    assert script == "wait(3)"

def test_move_command(generator):
    # 마우스 이동 명령
    intent = Intent(
        action="move",
        parameters={"x": 300, "y": 400},
        confidence=1.0,
        original_text="300, 400으로 이동해줘"
    )
    script = generator.generate(intent)
    assert script == "move(300, 400)"

def test_drag_command(generator):
    # 드래그 명령
    intent = Intent(
        action="drag",
        parameters={
            "start_x": 100,
            "start_y": 200,
            "end_x": 300,
            "end_y": 400
        },
        confidence=1.0,
        original_text="100, 200에서 300, 400으로 드래그해줘"
    )
    script = generator.generate(intent)
    assert script == "drag(100, 200, 300, 400)"

def test_scroll_command(generator):
    # 위로 스크롤
    intent = Intent(
        action="scroll",
        parameters={"amount": 100},
        confidence=1.0,
        original_text="위로 스크롤해줘"
    )
    script = generator.generate(intent)
    assert script == "scroll(100)"
    
    # 아래로 스크롤
    intent = Intent(
        action="scroll",
        parameters={"amount": -100},
        confidence=1.0,
        original_text="아래로 스크롤해줘"
    )
    script = generator.generate(intent)
    assert script == "scroll(-100)"

def test_hotkey_command(generator):
    # 단일 키
    intent = Intent(
        action="hotkey",
        parameters={"key1": "ctrl"},
        confidence=1.0,
        original_text="컨트롤 키 눌러줘"
    )
    script = generator.generate(intent)
    assert script == 'hotkey("ctrl")'
    
    # 조합 키
    intent = Intent(
        action="hotkey",
        parameters={"key1": "ctrl", "key2": "c"},
        confidence=1.0,
        original_text="컨트롤 + C 눌러줘"
    )
    script = generator.generate(intent)
    assert script == 'hotkey("ctrl", "c")'

def test_invalid_intent(generator):
    # 잘못된 의도
    assert generator.generate(None) is None
    
    # 잘못된 액션
    intent = Intent(
        action="invalid",
        parameters={},
        confidence=1.0,
        original_text="잘못된 명령"
    )
    assert generator.generate(intent) is None
    
    # 매개변수 누락
    intent = Intent(
        action="click",
        parameters={},
        confidence=1.0,
        original_text="클릭해줘"
    )
    assert generator.generate(intent) is None

def test_confidence_threshold(generator):
    # 낮은 신뢰도
    intent = Intent(
        action="click",
        parameters={"x": 100, "y": 200},
        confidence=0.3,  # 기본 임계값보다 낮음
        original_text="100, 200 클릭해줘"
    )
    assert generator.generate(intent) is None 