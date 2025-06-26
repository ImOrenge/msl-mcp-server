import pytest
from unittest.mock import Mock, patch, AsyncMock
from src.msl.interpreter import MSLInterpreter
from src.msl.generator import MSLGenerator
from src.prompt.analyzer import IntentAnalyzer
from src.msl.parser import MSLParser

@pytest.fixture
def interpreter():
    return MSLInterpreter()

@pytest.fixture
def generator():
    return MSLGenerator()

@pytest.fixture
def analyzer():
    return IntentAnalyzer()

@pytest.fixture
def parser():
    return MSLParser()

@pytest.fixture
def mock_pyautogui():
    with patch('src.msl.interpreter.pyautogui') as mock:
        yield mock

@pytest.fixture
def mock_websocket():
    with patch('fastapi.WebSocket') as mock:
        mock.send_json = AsyncMock()
        mock.receive_json = AsyncMock()
        yield mock

@pytest.fixture
def mock_analyzer():
    with patch('src.prompt.analyzer.IntentAnalyzer') as mock:
        analyzer = mock.return_value
        analyzer.analyze.return_value = Mock(
            action="click",
            parameters={"x": 100, "y": 200},
            confidence=1.0,
            original_text="100, 200 클릭해줘"
        )
        yield analyzer

@pytest.fixture
def mock_generator():
    with patch('src.msl.generator.MSLGenerator') as mock:
        generator = mock.return_value
        generator.generate.return_value = "click(100, 200)"
        yield generator

@pytest.fixture
def mock_interpreter():
    with patch('src.msl.interpreter.MSLInterpreter') as mock:
        interpreter = mock.return_value
        interpreter.execute.return_value = True
        interpreter.run_in_thread.return_value = True
        interpreter.stop.return_value = True
        yield interpreter

@pytest.fixture
def sample_intent():
    return {
        "action": "click",
        "parameters": {"x": 100, "y": 200},
        "confidence": 1.0,
        "original_text": "100, 200 클릭해줘"
    }

@pytest.fixture
def sample_script():
    return "click(100, 200)"

@pytest.fixture
def sample_voice_command():
    return "100, 200 클릭해줘"

@pytest.fixture
def sample_websocket_message():
    return {
        "type": "voice",
        "text": "100, 200 클릭해줘"
    }

@pytest.fixture
def sample_api_response():
    return {
        "script": "click(100, 200)",
        "status": "success"
    }

@pytest.fixture
def sample_node():
    from src.msl.parser import MSLNode, TokenType
    return MSLNode(TokenType.CLICK, {"x": 100, "y": 200})

@pytest.fixture
def sample_sequence():
    from src.msl.parser import MSLNode, TokenType
    sequence = MSLNode(TokenType.SEQUENCE)
    sequence.children = [
        MSLNode(TokenType.MOVE, {"x": 100, "y": 100}),
        MSLNode(TokenType.CLICK, {"x": 100, "y": 100}),
        MSLNode(TokenType.WAIT, {"seconds": 1.0}),
        MSLNode(TokenType.TYPE, {"text": "test"})
    ]
    return sequence 