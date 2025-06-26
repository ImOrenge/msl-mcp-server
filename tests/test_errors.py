import pytest
from src.msl.parser import MSLParser, MSLLexer
from src.msl.interpreter import MSLInterpreter
from src.prompt.analyzer import IntentAnalyzer
from src.msl.generator import MSLGenerator

def test_parser_syntax_error():
    """구문 분석 오류 테스트"""
    parser = MSLParser()
    
    # 괄호 누락
    with pytest.raises(SyntaxError) as exc_info:
        parser.parse("click100, 200)")
    assert "Expected '('" in str(exc_info.value)
    
    # 쉼표 누락
    with pytest.raises(SyntaxError) as exc_info:
        parser.parse("click(100 200)")
    assert "Expected ','" in str(exc_info.value)
    
    # 닫는 괄호 누락
    with pytest.raises(SyntaxError) as exc_info:
        parser.parse("click(100, 200")
    assert "Expected ')'" in str(exc_info.value)

def test_lexer_invalid_token():
    """잘못된 토큰 테스트"""
    lexer = MSLLexer()
    
    # 잘못된 명령어
    with pytest.raises(ValueError) as exc_info:
        list(lexer.tokenize("invalid(100)"))
    assert "Unknown command" in str(exc_info.value)
    
    # 잘못된 숫자 형식
    with pytest.raises(ValueError) as exc_info:
        list(lexer.tokenize("click(1.2.3, 200)"))
    assert "Invalid number" in str(exc_info.value)

def test_interpreter_execution_error():
    """실행 오류 테스트"""
    interpreter = MSLInterpreter()
    
    # 화면 범위 벗어난 좌표
    with pytest.raises(ValueError) as exc_info:
        interpreter.execute_command("click", {"x": -100, "y": -200})
    assert "Invalid coordinates" in str(exc_info.value)
    
    # 잘못된 키 이름
    with pytest.raises(ValueError) as exc_info:
        interpreter.execute_command("press", {"key": "invalid_key"})
    assert "Invalid key name" in str(exc_info.value)

def test_analyzer_intent_error():
    """의도 분석 오류 테스트"""
    analyzer = IntentAnalyzer()
    
    # 인식할 수 없는 명령
    result = analyzer.analyze("이해할 수 없는 명령")
    assert result is None
    
    # 잘못된 좌표 형식
    result = analyzer.analyze("abc, def 클릭해줘")
    assert result is None

def test_generator_error():
    """생성기 오류 테스트"""
    generator = MSLGenerator()
    
    # 지원하지 않는 명령
    with pytest.raises(ValueError) as exc_info:
        generator.generate_command("unsupported", {"param": "value"})
    assert "Unsupported command" in str(exc_info.value)
    
    # 필수 매개변수 누락
    with pytest.raises(ValueError) as exc_info:
        generator.generate_command("click", {})
    assert "Missing required parameters" in str(exc_info.value)

def test_integration_error_handling():
    """통합 오류 처리 테스트"""
    analyzer = IntentAnalyzer()
    generator = MSLGenerator()
    parser = MSLParser()
    interpreter = MSLInterpreter()
    
    # 전체 파이프라인 오류 처리
    command = "이해할 수 없는 명령"
    
    # 1. 의도 분석
    intent = analyzer.analyze(command)
    assert intent is None
    
    # 2. MSL 스크립트 생성
    script = generator.generate(intent) if intent else None
    assert script is None
    
    # 3. 구문 분석
    if script:
        with pytest.raises(SyntaxError):
            parser.parse(script)
    
    # 4. 실행
    if script:
        with pytest.raises(ValueError):
            interpreter.execute(script) 