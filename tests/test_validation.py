import pytest
from src.msl.parser import MSLParser, MSLNode, TokenType
from src.msl.validator import MSLValidator

def test_click_command_validation():
    """클릭 명령 유효성 검사 테스트"""
    validator = MSLValidator()
    parser = MSLParser()

    # 유효한 좌표
    node = parser.parse("click(100, 200)")
    assert validator.validate(node) is True

    # 음수 좌표
    node = parser.parse("click(-100, -200)")
    assert validator.validate(node) is False

    # 화면 범위 초과
    node = parser.parse("click(99999, 99999)")
    assert validator.validate(node) is False

    # 소수점 좌표
    node = parser.parse("click(100.5, 200.5)")
    assert validator.validate(node) is False

def test_type_command_validation():
    """타이핑 명령 유효성 검사 테스트"""
    validator = MSLValidator()
    parser = MSLParser()

    # 유효한 문자열
    node = parser.parse('type("Hello, World!")')
    assert validator.validate(node) is True

    # 빈 문자열
    node = parser.parse('type("")')
    assert validator.validate(node) is False

    # 특수 문자 포함
    node = parser.parse('type("안녕하세요!")')
    assert validator.validate(node) is True

def test_press_command_validation():
    """키 입력 명령 유효성 검사 테스트"""
    validator = MSLValidator()
    parser = MSLParser()

    # 유효한 키 이름
    node = parser.parse('press("enter")')
    assert validator.validate(node) is True

    # 잘못된 키 이름
    node = parser.parse('press("invalid_key")')
    assert validator.validate(node) is False

    # 조합 키
    node = parser.parse('press("ctrl+c")')
    assert validator.validate(node) is True

def test_wait_command_validation():
    """대기 명령 유효성 검사 테스트"""
    validator = MSLValidator()
    parser = MSLParser()

    # 유효한 대기 시간
    node = parser.parse("wait(1)")
    assert validator.validate(node) is True

    # 음수 대기 시간
    node = parser.parse("wait(-1)")
    assert validator.validate(node) is False

    # 너무 긴 대기 시간
    node = parser.parse("wait(3600)")
    assert validator.validate(node) is False

def test_move_command_validation():
    """이동 명령 유효성 검사 테스트"""
    validator = MSLValidator()
    parser = MSLParser()

    # 유효한 좌표
    node = parser.parse("move(100, 200)")
    assert validator.validate(node) is True

    # 음수 좌표
    node = parser.parse("move(-100, -200)")
    assert validator.validate(node) is False

    # 화면 범위 초과
    node = parser.parse("move(99999, 99999)")
    assert validator.validate(node) is False

def test_drag_command_validation():
    """드래그 명령 유효성 검사 테스트"""
    validator = MSLValidator()
    parser = MSLParser()

    # 유효한 좌표
    node = parser.parse("drag(100, 200, 300, 400)")
    assert validator.validate(node) is True

    # 음수 좌표
    node = parser.parse("drag(-100, -200, -300, -400)")
    assert validator.validate(node) is False

    # 화면 범위 초과
    node = parser.parse("drag(99999, 99999, 99999, 99999)")
    assert validator.validate(node) is False

def test_scroll_command_validation():
    """스크롤 명령 유효성 검사 테스트"""
    validator = MSLValidator()
    parser = MSLParser()

    # 유효한 스크롤 값
    node = parser.parse("scroll(10)")
    assert validator.validate(node) is True

    # 음수 스크롤 값
    node = parser.parse("scroll(-10)")
    assert validator.validate(node) is True

    # 너무 큰 스크롤 값
    node = parser.parse("scroll(1000)")
    assert validator.validate(node) is False

def test_hotkey_command_validation():
    """단축키 명령 유효성 검사 테스트"""
    validator = MSLValidator()
    parser = MSLParser()

    # 유효한 단축키
    node = parser.parse('hotkey("ctrl", "c")')
    assert validator.validate(node) is True

    # 잘못된 키 이름
    node = parser.parse('hotkey("invalid", "key")')
    assert validator.validate(node) is False

    # 너무 많은 키 조합
    node = parser.parse('hotkey("ctrl", "alt", "shift", "a")')
    assert validator.validate(node) is False 