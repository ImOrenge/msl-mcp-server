import pytest
from src.prompt.analyzer import IntentAnalyzer, Intent

def test_click_command():
    analyzer = IntentAnalyzer()
    
    # 기본 클릭 명령
    intent = analyzer.analyze("클릭해")
    assert intent is not None
    assert intent.action == "click"
    
    # 좌표 클릭 명령
    intent = analyzer.analyze("100, 200 클릭해줘")
    assert intent is not None
    assert intent.action == "click"
    assert intent.parameters["x"] == 100
    assert intent.parameters["y"] == 200

def test_type_command():
    analyzer = IntentAnalyzer()
    
    # 따옴표로 감싼 텍스트
    intent = analyzer.analyze('"안녕하세요" 입력해줘')
    assert intent is not None
    assert intent.action == "type"
    assert intent.parameters["text"] == "안녕하세요"
    
    # 작은따옴표로 감싼 텍스트
    intent = analyzer.analyze("'Hello World' 입력")
    assert intent is not None
    assert intent.action == "type"
    assert intent.parameters["text"] == "Hello World"

def test_press_command():
    analyzer = IntentAnalyzer()
    
    # 키 입력 명령
    intent = analyzer.analyze("엔터 키 눌러줘")
    assert intent is not None
    assert intent.action == "press"
    assert intent.parameters["key"] == "엔터"

def test_wait_command():
    analyzer = IntentAnalyzer()
    
    # 초 단위 대기
    intent = analyzer.analyze("3초 기다려줘")
    assert intent is not None
    assert intent.action == "wait"
    assert intent.parameters["seconds"] == 3.0
    
    # 기본 대기
    intent = analyzer.analyze("잠깐 기다려")
    assert intent is not None
    assert intent.action == "wait"
    assert intent.parameters["seconds"] == 1.0

def test_move_command():
    analyzer = IntentAnalyzer()
    
    # 좌표 이동
    intent = analyzer.analyze("300, 400으로 이동해줘")
    assert intent is not None
    assert intent.action == "move"
    assert intent.parameters["x"] == 300
    assert intent.parameters["y"] == 400

def test_drag_command():
    analyzer = IntentAnalyzer()
    
    # 드래그 명령
    intent = analyzer.analyze("100, 200에서 300, 400으로 드래그해줘")
    assert intent is not None
    assert intent.action == "drag"
    assert intent.parameters["start_x"] == 100
    assert intent.parameters["start_y"] == 200
    assert intent.parameters["end_x"] == 300
    assert intent.parameters["end_y"] == 400

def test_scroll_command():
    analyzer = IntentAnalyzer()
    
    # 위로 스크롤
    intent = analyzer.analyze("위로 스크롤해줘")
    assert intent is not None
    assert intent.action == "scroll"
    assert intent.parameters["amount"] > 0
    
    # 아래로 스크롤
    intent = analyzer.analyze("아래로 스크롤")
    assert intent is not None
    assert intent.action == "scroll"
    assert intent.parameters["amount"] < 0

def test_hotkey_command():
    analyzer = IntentAnalyzer()
    
    # 단일 키
    intent = analyzer.analyze("컨트롤 키 눌러줘")
    assert intent is not None
    assert intent.action == "hotkey"
    assert intent.parameters["key1"] == "컨트롤"
    
    # 조합 키
    intent = analyzer.analyze("컨트롤 + C 눌러줘")
    assert intent is not None
    assert intent.action == "hotkey"
    assert intent.parameters["key1"] == "컨트롤"
    assert intent.parameters["key2"] == "C"

def test_invalid_commands():
    analyzer = IntentAnalyzer()
    
    # 잘못된 명령
    assert analyzer.analyze("") is None
    assert analyzer.analyze("안녕하세요") is None
    assert analyzer.analyze("abc, def 클릭해줘") is None  # 숫자가 아닌 좌표
    assert analyzer.analyze("-100, -200 클릭해줘") is None  # 음수 좌표 