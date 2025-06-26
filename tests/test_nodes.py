import pytest
from src.msl.parser import MSLNode, TokenType

def test_node_creation():
    """노드 생성 테스트"""
    # 클릭 노드
    click_node = MSLNode(TokenType.CLICK, {"x": 100, "y": 200})
    assert click_node.type == TokenType.CLICK
    assert click_node.parameters == {"x": 100, "y": 200}

    # 타이핑 노드
    type_node = MSLNode(TokenType.TYPE, {"text": "Hello, World!"})
    assert type_node.type == TokenType.TYPE
    assert type_node.parameters == {"text": "Hello, World!"}

    # 키 입력 노드
    press_node = MSLNode(TokenType.PRESS, {"key": "enter"})
    assert press_node.type == TokenType.PRESS
    assert press_node.parameters == {"key": "enter"}

def test_node_equality():
    """노드 비교 테스트"""
    node1 = MSLNode(TokenType.CLICK, {"x": 100, "y": 200})
    node2 = MSLNode(TokenType.CLICK, {"x": 100, "y": 200})
    node3 = MSLNode(TokenType.CLICK, {"x": 300, "y": 400})
    node4 = MSLNode(TokenType.TYPE, {"text": "Hello"})

    assert node1 == node2
    assert node1 != node3
    assert node1 != node4

def test_node_string_representation():
    """노드 문자열 표현 테스트"""
    node = MSLNode(TokenType.CLICK, {"x": 100, "y": 200})
    assert str(node) == "MSLNode(type=CLICK, parameters={'x': 100, 'y': 200})"
    assert repr(node) == "MSLNode(type=CLICK, parameters={'x': 100, 'y': 200})"

def test_node_parameter_validation():
    """노드 매개변수 검증 테스트"""
    with pytest.raises(ValueError):
        MSLNode(TokenType.CLICK, {})  # 필수 매개변수 누락

    with pytest.raises(ValueError):
        MSLNode(TokenType.CLICK, {"x": "invalid"})  # 잘못된 매개변수 타입

    with pytest.raises(ValueError):
        MSLNode(TokenType.TYPE, {})  # 필수 매개변수 누락

def test_node_sequence():
    """노드 시퀀스 테스트"""
    nodes = [
        MSLNode(TokenType.CLICK, {"x": 100, "y": 200}),
        MSLNode(TokenType.TYPE, {"text": "Hello"}),
        MSLNode(TokenType.PRESS, {"key": "enter"})
    ]

    # 시퀀스 순서 확인
    assert nodes[0].type == TokenType.CLICK
    assert nodes[1].type == TokenType.TYPE
    assert nodes[2].type == TokenType.PRESS

    # 시퀀스 매개변수 확인
    assert nodes[0].parameters == {"x": 100, "y": 200}
    assert nodes[1].parameters == {"text": "Hello"}
    assert nodes[2].parameters == {"key": "enter"} 