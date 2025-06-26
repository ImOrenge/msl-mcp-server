"""
MSL 파싱 도구

MSL 스크립트를 파싱하고 AST(Abstract Syntax Tree)로 변환하는 도구입니다.
구문 오류 검증 및 파싱 결과 분석 기능을 제공합니다.
"""

import asyncio
import json
import traceback
from typing import Dict, Any, List, Optional
from mcp.types import TextContent, Tool

from ..msl.msl_lexer import MSLLexer  
from ..msl.msl_parser import MSLParser


class ParseTool:
    """MSL 스크립트 파싱 도구"""
    
    def __init__(self):
        self.lexer = MSLLexer()
        self.parser = MSLParser()
    
    @property
    def tool_definition(self) -> Tool:
        """도구 정의를 반환합니다."""
        return Tool(
            name="parse_msl",
            description="MSL(Macro Scripting Language) 스크립트를 파싱하고 구문 분석을 수행합니다. "
                       "입력된 MSL 스크립트의 구문 오류를 확인하고 AST(Abstract Syntax Tree)를 생성합니다.",
            inputSchema={
                "type": "object",
                "properties": {
                    "script": {
                        "type": "string",
                        "description": "파싱할 MSL 스크립트 텍스트입니다. "
                                     "예: 'ctrl+c, ctrl+v' 또는 'a+b > 500, c'"
                    },
                    "verbose": {
                        "type": "boolean", 
                        "description": "상세한 파싱 정보를 포함할지 여부입니다. "
                                     "true로 설정하면 토큰 정보와 AST 구조를 자세히 보여줍니다.",
                        "default": False
                    },
                    "validate_only": {
                        "type": "boolean",
                        "description": "파싱 결과 없이 구문 검증만 수행할지 여부입니다. "
                                     "true로 설정하면 오류 여부만 확인합니다.",
                        "default": False
                    }
                },
                "required": ["script"]
            }
        )
    
    async def execute(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """파싱 도구를 실행합니다."""
        try:
            script = arguments.get("script", "").strip()
            verbose = arguments.get("verbose", False)
            validate_only = arguments.get("validate_only", False)
            
            if not script:
                return [TextContent(
                    type="text",
                    text="❌ 오류: 파싱할 스크립트가 제공되지 않았습니다.\n\n"
                         "사용법: parse_msl(script='your_msl_script_here')"
                )]
            
            # 1. 어휘 분석 (토큰화)
            try:
                tokens = self.lexer.tokenize(script)
                token_list = list(tokens)  # 이터레이터를 리스트로 변환
            except Exception as e:
                return [TextContent(
                    type="text", 
                    text=f"❌ 어휘 분석 오류:\n{str(e)}\n\n"
                         f"입력 스크립트: '{script}'\n"
                         f"오류가 발생한 위치를 확인해주세요."
                )]
            
            # 검증만 수행하는 경우
            if validate_only:
                try:
                    # 파서로 구문 검증
                    ast = self.parser.parse(script)
                    return [TextContent(
                        type="text",
                        text=f"✅ 구문 검증 성공!\n\n"
                             f"입력 스크립트: '{script}'\n"
                             f"토큰 수: {len(token_list)}개\n"
                             f"구문 오류가 없습니다."
                    )]
                except Exception as e:
                    return [TextContent(
                        type="text",
                        text=f"❌ 구문 검증 실패:\n{str(e)}\n\n"
                             f"입력 스크립트: '{script}'\n"
                             f"구문 오류를 수정해주세요."
                    )]
            
            # 2. 구문 분석 (파싱)
            try:
                ast = self.parser.parse(script)
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"❌ 구문 분석 오류:\n{str(e)}\n\n"
                         f"입력 스크립트: '{script}'\n"
                         f"구문 오류를 확인해주세요."
                )]
            
            # 3. 결과 생성
            result = self._format_parse_result(script, token_list, ast, verbose)
            
            return [TextContent(type="text", text=result)]
            
        except Exception as e:
            error_msg = f"❌ 파싱 도구 실행 중 예상치 못한 오류가 발생했습니다:\n{str(e)}\n\n"
            error_msg += f"스택 트레이스:\n{traceback.format_exc()}"
            return [TextContent(type="text", text=error_msg)]
    
    def _format_parse_result(self, script: str, tokens: List, ast, verbose: bool) -> str:
        """파싱 결과를 포맷팅합니다."""
        result = "✅ MSL 스크립트 파싱 성공!\n\n"
        result += f"📝 입력 스크립트: '{script}'\n\n"
        
        # 기본 정보
        result += f"📊 파싱 정보:\n"
        result += f"• 토큰 수: {len(tokens)}개\n"
        result += f"• AST 노드 타입: {type(ast).__name__}\n\n"
        
        if verbose:
            # 상세 토큰 정보
            result += "🔍 토큰 분석 (상세):\n"
            for i, token in enumerate(tokens, 1):
                result += f"  {i:2d}. {token.type:<12} | '{token.value}'"
                if hasattr(token, 'lineno'):
                    result += f" | 줄:{token.lineno}"
                if hasattr(token, 'column'):
                    result += f" | 열:{token.column}"
                result += "\n"
            result += "\n"
            
            # AST 구조 정보
            result += "🌳 AST 구조 (상세):\n"
            result += self._format_ast_tree(ast, indent=2)
            result += "\n"
        else:
            # 간단한 토큰 정보
            result += "🔍 토큰 요약:\n"
            token_types = {}
            for token in tokens:
                token_types[token.type] = token_types.get(token.type, 0) + 1
            
            for token_type, count in token_types.items():
                result += f"  • {token_type}: {count}개\n"
            result += "\n"
        
        # 파싱 결과 요약
        result += "📋 파싱 요약:\n"
        result += f"• 상태: 성공\n"
        result += f"• 구문 오류: 없음\n"
        result += f"• 실행 가능: ✅\n\n"
        
        # 사용 가능한 다음 단계 안내
        result += "💡 다음 단계:\n"
        result += "• validate_msl: 더 상세한 검증 수행\n"
        result += "• optimize_msl: 스크립트 최적화\n"
        result += "• explain_msl: 스크립트 동작 설명"
        
        return result
    
    def _format_ast_tree(self, node, indent: int = 0) -> str:
        """AST 노드를 트리 형태로 포맷팅합니다."""
        if node is None:
            return " " * indent + "None\n"
        
        result = " " * indent + f"{type(node).__name__}\n"
        
        # 노드의 속성들을 재귀적으로 출력
        if hasattr(node, '__dict__'):
            for attr_name, attr_value in node.__dict__.items():
                if attr_name.startswith('_'):
                    continue
                    
                result += " " * (indent + 2) + f"{attr_name}: "
                
                if isinstance(attr_value, list):
                    result += f"[{len(attr_value)} items]\n"
                    for item in attr_value:
                        if hasattr(item, '__dict__'):  # AST 노드인 경우
                            result += self._format_ast_tree(item, indent + 4)
                        else:
                            result += " " * (indent + 4) + f"{repr(item)}\n"
                elif hasattr(attr_value, '__dict__'):  # AST 노드인 경우
                    result += "\n"
                    result += self._format_ast_tree(attr_value, indent + 4)
                else:
                    result += f"{repr(attr_value)}\n"
        
        return result 