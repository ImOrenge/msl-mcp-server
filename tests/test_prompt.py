import pytest
from src.prompt.analyzer import IntentAnalyzer, Intent
from src.msl.generator import MSLGenerator

def test_click_intent():
    analyzer = IntentAnalyzer()
    text = "로그인 버튼을 클릭해줘"
    intent = analyzer.analyze(text)
    
    assert intent is not None
    assert intent.action == "click"
    assert "target" in intent.parameters
    assert intent.parameters["target"] == "로그인 버튼"
    assert intent.confidence > 0.8
    assert intent.original_text == text

def test_type_intent():
    analyzer = IntentAnalyzer()
    text = "안녕하세요라고 입력해"
    intent = analyzer.analyze(text)
    
    assert intent is not None
    assert intent.action == "type"
    assert "text" in intent.parameters
    assert intent.parameters["text"] == "안녕하세요"
    assert intent.confidence > 0.8
    assert intent.original_text == text

def test_press_intent():
    analyzer = IntentAnalyzer()
    text = "엔터 키를 눌러줘"
    intent = analyzer.analyze(text)
    
    assert intent is not None
    assert intent.action == "press"
    assert "key" in intent.parameters
    assert intent.parameters["key"] == "enter"
    assert intent.confidence > 0.8
    assert intent.original_text == text

def test_wait_intent():
    analyzer = IntentAnalyzer()
    text = "2초 기다려줘"
    intent = analyzer.analyze(text)
    
    assert intent is not None
    assert intent.action == "wait"
    assert "seconds" in intent.parameters
    assert intent.parameters["seconds"] == 2
    assert intent.confidence > 0.8
    assert intent.original_text == text

def test_unknown_intent():
    analyzer = IntentAnalyzer()
    text = "이상한 명령어"
    intent = analyzer.analyze(text)
    
    assert intent is None

def test_msl_generator():
    generator = MSLGenerator()
    
    # 클릭 명령 생성
    click_intent = Intent(
        action="click",
        parameters={"x": 100, "y": 200},
        confidence=0.95,
        original_text="여기 클릭해줘"
    )
    assert generator.generate(click_intent) == "click(100, 200)"
    
    # 텍스트 입력 명령 생성
    type_intent = Intent(
        action="type",
        parameters={"text": "Hello, World!"},
        confidence=0.95,
        original_text="Hello, World!라고 입력해줘"
    )
    assert generator.generate(type_intent) == 'type("Hello, World!")'
    
    # 키 입력 명령 생성
    press_intent = Intent(
        action="press",
        parameters={"key": "enter"},
        confidence=0.95,
        original_text="엔터 키를 눌러줘"
    )
    assert generator.generate(press_intent) == 'press("enter")'
    
    # 대기 명령 생성
    wait_intent = Intent(
        action="wait",
        parameters={"seconds": 2},
        confidence=0.95,
        original_text="2초 기다려줘"
    )
    assert generator.generate(wait_intent) == "wait(2)"

def test_msl_generation_invalid():
    generator = MSLGenerator()
    intent = Intent(
        action="unknown",
        parameters={},
        confidence=0.1,
        original_text="이상한 명령어"
    )
    
    script = generator.generate(intent)
    assert script is None 