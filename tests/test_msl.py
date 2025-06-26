import pytest
from src.msl.parser import MSLParser, Token, MSLNode, TokenType
from src.msl.interpreter import MSLInterpreter

def test_tokenize_basic():
    parser = MSLParser()
    source = 'click(100, 200)'
    tokens = parser.tokenize(source)
    
    assert len(tokens) > 0
    assert tokens[0].type == TokenType.IDENTIFIER
    assert tokens[0].value == 'click'

def test_parse_click_command():
    parser = MSLParser()
    source = 'click(100, 200)'
    ast = parser.parse(source)
    
    assert ast.type == 'Program'
    assert len(ast.children) == 1
    assert ast.children[0].type == 'ExpressionStatement'
    assert ast.children[0].children[0].type == 'CallExpression'
    assert ast.children[0].children[0].value == 'click'

def test_parse_type_command():
    parser = MSLParser()
    source = 'type("Hello, World!")'
    ast = parser.parse(source)
    
    assert ast.type == 'Program'
    assert len(ast.children) == 1
    assert ast.children[0].type == 'ExpressionStatement'
    assert ast.children[0].children[0].type == 'CallExpression'
    assert ast.children[0].children[0].value == 'type'

def test_parse_press_command():
    parser = MSLParser()
    source = 'press("enter")'
    ast = parser.parse(source)
    
    assert ast.type == 'Program'
    assert len(ast.children) == 1
    assert ast.children[0].type == 'ExpressionStatement'
    assert ast.children[0].children[0].type == 'CallExpression'
    assert ast.children[0].children[0].value == 'press'

def test_parse_wait_command():
    parser = MSLParser()
    source = 'wait(1.5)'
    ast = parser.parse(source)
    
    assert ast.type == 'Program'
    assert len(ast.children) == 1
    assert ast.children[0].type == 'ExpressionStatement'
    assert ast.children[0].children[0].type == 'CallExpression'
    assert ast.children[0].children[0].value == 'wait'

def test_interpreter_click():
    interpreter = MSLInterpreter()
    node = MSLNode(
        type='Program',
        value=None,
        children=[
            MSLNode(
                type='ExpressionStatement',
                value=None,
                children=[
                    MSLNode(
                        type='CallExpression',
                        value='click',
                        children=[
                            MSLNode(type='Number', value=100, children=[], line=1, column=6),
                            MSLNode(type='Number', value=200, children=[], line=1, column=11)
                        ],
                        line=1,
                        column=1
                    )
                ],
                line=1,
                column=1
            )
        ],
        line=1,
        column=1
    )
    
    # 실제 마우스 동작은 하지 않고 예외가 발생하지 않는지만 테스트
    try:
        interpreter.interpret(node)
    except Exception as e:
        pytest.fail(f"예외 발생: {str(e)}")

def test_interpreter_type():
    interpreter = MSLInterpreter()
    node = MSLNode(
        type='Program',
        value=None,
        children=[
            MSLNode(
                type='ExpressionStatement',
                value=None,
                children=[
                    MSLNode(
                        type='CallExpression',
                        value='type',
                        children=[
                            MSLNode(type='String', value='Hello', children=[], line=1, column=6)
                        ],
                        line=1,
                        column=1
                    )
                ],
                line=1,
                column=1
            )
        ],
        line=1,
        column=1
    )
    
    try:
        interpreter.interpret(node)
    except Exception as e:
        pytest.fail(f"예외 발생: {str(e)}")

def test_interpreter_press():
    interpreter = MSLInterpreter()
    node = MSLNode(
        type='Program',
        value=None,
        children=[
            MSLNode(
                type='ExpressionStatement',
                value=None,
                children=[
                    MSLNode(
                        type='CallExpression',
                        value='press',
                        children=[
                            MSLNode(type='String', value='enter', children=[], line=1, column=7)
                        ],
                        line=1,
                        column=1
                    )
                ],
                line=1,
                column=1
            )
        ],
        line=1,
        column=1
    )
    
    try:
        interpreter.interpret(node)
    except Exception as e:
        pytest.fail(f"예외 발생: {str(e)}")

def test_interpreter_wait():
    interpreter = MSLInterpreter()
    node = MSLNode(
        type='Program',
        value=None,
        children=[
            MSLNode(
                type='ExpressionStatement',
                value=None,
                children=[
                    MSLNode(
                        type='CallExpression',
                        value='wait',
                        children=[
                            MSLNode(type='Number', value=0.1, children=[], line=1, column=6)
                        ],
                        line=1,
                        column=1
                    )
                ],
                line=1,
                column=1
            )
        ],
        line=1,
        column=1
    )
    
    try:
        interpreter.interpret(node)
    except Exception as e:
        pytest.fail(f"예외 발생: {str(e)}") 