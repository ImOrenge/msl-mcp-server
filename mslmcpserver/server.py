#!/usr/bin/env python3
"""
MSL (Macro Scripting Language) MCP Server

OpenAI API를 이용한 AI 기반 MSL 스크립트 생성 및 분석 서버
Model Context Protocol (MCP)를 통해 클라이언트와 통신합니다.

이 서버는 다음 기능을 제공합니다:
- MSL 스크립트 파싱 및 검증
- 자연어 프롬프트에서 MSL 스크립트 자동 생성
- MSL 구문 최적화 및 설명
- 게임별 매크로 예제 제공
"""

import os
import sys
import logging
from pathlib import Path

# Headless 환경 대응: GUI 관련 라이브러리 문제 방지
def setup_headless_environment():
    """Headless 환경에서 GUI 라이브러리 문제를 방지하는 설정"""
    os.environ.setdefault('DISPLAY', ':99')
    os.environ.setdefault('MPLBACKEND', 'Agg')
    os.environ.setdefault('NO_AT_BRIDGE', '1')
    
    # pyautogui가 import될 수도 있는 경우를 대비해 fail-safe 비활성화
    try:
        import pyautogui
        pyautogui.FAILSAFE = False
        pyautogui.PAUSE = 0.1
    except (ImportError, Exception):
        # pyautogui가 없거나 설정 실패해도 계속 진행
        pass

# 실행 환경 설정
setup_headless_environment()

# 이제 안전하게 다른 모듈들 import
import asyncio
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

# MCP 관련 import
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
    import mcp.server.session
except ImportError as e:
    logging.error(f"MCP 라이브러리 import 실패: {e}")
    logging.error("pip install mcp 명령으로 MCP 라이브러리를 설치하세요.")
    sys.exit(1)

# 로컬 모듈 import
try:
    from tools.parse_tool import parse_msl
    from tools.generate_tool import generate_msl  
    from tools.validate_tool import validate_msl
    from tools.optimize_tool import optimize_msl
    from tools.explain_tool import explain_msl
    from tools.examples_tool import msl_examples
    from config.settings import get_settings
except ImportError as e:
    logging.error(f"로컬 모듈 import 실패: {e}")
    logging.error("MSL MCP 서버 구조를 확인하세요.")
    sys.exit(1)

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('msl_mcp_server.log', encoding='utf-8') if os.path.exists('.') else logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# 전역 설정 로드
try:
    settings = get_settings()
    logger.info(f"설정 로드 완료: OpenAI 모델 = {settings.openai_model}")
except Exception as e:
    logger.error(f"설정 로드 실패: {e}")
    sys.exit(1)

# MCP 서버 인스턴스 생성
server = Server("msl-mcp-server")

# MSL 도구 인스턴스들
parse_tool = parse_msl
generate_tool = generate_msl
validate_tool = validate_msl
optimize_tool = optimize_msl
explain_tool = explain_msl
examples_tool = msl_examples


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
            result = await parse_tool(arguments)
        elif name == "generate_msl":
            result = await generate_tool(arguments)
        elif name == "validate_msl":
            result = await validate_tool(arguments)
        elif name == "optimize_msl":
            result = await optimize_tool(arguments)
        elif name == "explain_msl":
            result = await explain_tool(arguments)
        elif name == "msl_examples":
            result = await examples_tool(arguments)
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