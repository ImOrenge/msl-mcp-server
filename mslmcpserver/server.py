#!/usr/bin/env python3
"""
MSL MCP Server - 게이머를 위한 매크로 스크립팅 언어 도우미

이 서버는 다음 기능을 제공합니다:
- MSL 스크립트 파싱 및 검증
- 자연어 프롬프트에서 MSL 스크립트 자동 생성
- MSL 구문 최적화 및 설명
- 게임별 매크로 예제 제공
"""

import asyncio
import logging
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# MSL 도구들 임포트
from tools.parse_tool import ParseMSLTool
from tools.generate_tool import GenerateMSLTool
from tools.validate_tool import ValidateMSLTool
from tools.optimize_tool import OptimizeMSLTool
from tools.explain_tool import ExplainMSLTool
from tools.examples_tool import ExamplesMSLTool

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("msl-mcp-server")

# MCP 서버 인스턴스 생성
server = Server("msl-assistant")

# MSL 도구 인스턴스들
parse_tool = ParseMSLTool()
generate_tool = GenerateMSLTool()
validate_tool = ValidateMSLTool()
optimize_tool = OptimizeMSLTool()
explain_tool = ExplainMSLTool()
examples_tool = ExamplesMSLTool()


@server.list_tools()
async def list_tools() -> list[Tool]:
    """
    사용 가능한 MSL 도구 목록을 반환합니다.
    
    Returns:
        list[Tool]: 6개 MSL 도구의 정의 목록
    """
    return [
        Tool(
            name="parse_msl",
            description="MSL 스크립트를 파싱하고 AST 구조를 분석합니다. 구문 오류를 검출하고 토큰 분석 결과를 제공합니다.",
            inputSchema={
                "type": "object",
                "properties": {
                    "script": {
                        "type": "string",
                        "description": "분석할 MSL 스크립트 코드"
                    },
                    "detailed": {
                        "type": "boolean", 
                        "description": "상세한 AST 및 토큰 정보 포함 여부",
                        "default": False
                    }
                },
                "required": ["script"]
            }
        ),
        Tool(
            name="generate_msl",
            description="자연어 설명을 바탕으로 MSL 스크립트를 자동 생성합니다. Context7를 활용하여 게임별 최적화된 스크립트를 생성합니다.",
            inputSchema={
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "원하는 매크로 동작을 설명하는 자연어 프롬프트"
                    },
                    "game_type": {
                        "type": "string",
                        "description": "게임 타입 (fps, mmo, rts, moba, general)",
                        "default": "general"
                    },
                    "complexity": {
                        "type": "string",
                        "description": "스크립트 복잡도 (simple, medium, complex)",
                        "default": "medium"
                    }
                },
                "required": ["prompt"]
            }
        ),
        Tool(
            name="validate_msl",
            description="MSL 스크립트의 구문과 논리적 오류를 검증합니다. 성능 문제나 비효율적인 패턴을 진단합니다.",
            inputSchema={
                "type": "object",
                "properties": {
                    "script": {
                        "type": "string",
                        "description": "검증할 MSL 스크립트 코드"
                    },
                    "strict": {
                        "type": "boolean",
                        "description": "엄격한 검증 모드 활성화",
                        "default": False
                    }
                },
                "required": ["script"]
            }
        ),
        Tool(
            name="optimize_msl",
            description="MSL 스크립트를 최적화하여 성능을 개선하고 더 효율적인 구조로 변환합니다.",
            inputSchema={
                "type": "object",
                "properties": {
                    "script": {
                        "type": "string",
                        "description": "최적화할 MSL 스크립트 코드"
                    },
                    "target": {
                        "type": "string",
                        "description": "최적화 목표 (speed, readability, compatibility)",
                        "default": "speed"
                    }
                },
                "required": ["script"]
            }
        ),
        Tool(
            name="explain_msl",
            description="MSL 스크립트나 특정 구문을 상세히 설명합니다. 동작 방식과 매개변수를 분석하여 학습을 도와줍니다.",
            inputSchema={
                "type": "object",
                "properties": {
                    "input": {
                        "type": "string",
                        "description": "설명할 MSL 스크립트 또는 구문"
                    },
                    "detail_level": {
                        "type": "string",
                        "description": "설명 상세도 (basic, intermediate, advanced)",
                        "default": "intermediate"
                    }
                },
                "required": ["input"]
            }
        ),
        Tool(
            name="msl_examples",
            description="특정 카테고리나 게임 타입에 맞는 MSL 예제를 제공합니다. 학습 목적이나 템플릿으로 활용할 수 있습니다.",
            inputSchema={
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "예제 카테고리 (combat, movement, ui_interaction, combo, timing)",
                        "default": "all"
                    },
                    "game_type": {
                        "type": "string",
                        "description": "게임 타입 (fps, mmo, rts, moba, general)",
                        "default": "general"
                    },
                    "count": {
                        "type": "integer",
                        "description": "반환할 예제 개수",
                        "default": 5,
                        "minimum": 1,
                        "maximum": 20
                    }
                }
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """
    요청된 MSL 도구를 실행합니다.
    
    Args:
        name (str): 실행할 도구 이름
        arguments (dict): 도구 실행에 필요한 매개변수
        
    Returns:
        list[TextContent]: 도구 실행 결과
    """
    try:
        if name == "parse_msl":
            result = await parse_tool.execute(arguments)
        elif name == "generate_msl":
            result = await generate_tool.execute(arguments)
        elif name == "validate_msl":
            result = await validate_tool.execute(arguments)
        elif name == "optimize_msl":
            result = await optimize_tool.execute(arguments)
        elif name == "explain_msl":
            result = await explain_tool.execute(arguments)
        elif name == "msl_examples":
            result = await examples_tool.execute(arguments)
        else:
            return [TextContent(type="text", text=f"알 수 없는 도구: {name}")]
        
        return [TextContent(type="text", text=result)]
        
    except Exception as e:
        logger.error(f"도구 실행 중 오류 발생 ({name}): {e}")
        return [TextContent(type="text", text=f"오류: {str(e)}")]


async def main():
    """
    MSL MCP 서버를 시작합니다.
    """
    logger.info("MSL MCP 서버 시작 중...")
    logger.info("지원 도구: parse_msl, generate_msl, validate_msl, optimize_msl, explain_msl, msl_examples")
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream, write_stream, server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main()) 