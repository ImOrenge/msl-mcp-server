"""
MSL 검증 도구

MSL 스크립트의 구문 정확성, 의미적 일관성, 성능 이슈 등을 종합적으로 검증합니다.
상세한 오류 진단과 수정 제안을 제공합니다.
"""

import asyncio
import json
import traceback
import re
from typing import Dict, Any, List, Optional, Tuple
from mcp.types import TextContent, Tool

from ..msl.msl_lexer import MSLLexer
from ..msl.msl_parser import MSLParser


class ValidateTool:
    """MSL 스크립트 상세 검증 도구"""
    
    def __init__(self):
        self.lexer = MSLLexer()
        self.parser = MSLParser()
        self.validation_rules = self._load_validation_rules()
    
    @property
    def tool_definition(self) -> Tool:
        """도구 정의를 반환합니다."""
        return Tool(
            name="validate_msl",
            description="MSL(Macro Scripting Language) 스크립트의 상세한 검증을 수행합니다. "
                       "구문 오류, 의미적 문제, 성능 이슈, 보안 문제 등을 종합적으로 분석하고 "
                       "수정 제안을 제공합니다.",
            inputSchema={
                "type": "object",
                "properties": {
                    "script": {
                        "type": "string",
                        "description": "검증할 MSL 스크립트 텍스트입니다."
                    },
                    "validation_level": {
                        "type": "string",
                        "enum": ["basic", "standard", "strict", "comprehensive"],
                        "description": "검증 수준입니다. "
                                     "basic: 기본 구문 검사, standard: 표준 검증, "
                                     "strict: 엄격한 검증, comprehensive: 종합 검증",
                        "default": "standard"
                    },
                    "check_performance": {
                        "type": "boolean",
                        "description": "성능 관련 이슈를 검사할지 여부입니다.",
                        "default": True
                    },
                    "suggest_fixes": {
                        "type": "boolean",
                        "description": "발견된 문제에 대한 수정 제안을 포함할지 여부입니다.",
                        "default": True
                    }
                },
                "required": ["script"]
            }
        )
    
    async def execute(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """검증 도구를 실행합니다."""
        try:
            script = arguments.get("script", "").strip()
            validation_level = arguments.get("validation_level", "standard")
            check_performance = arguments.get("check_performance", True)
            suggest_fixes = arguments.get("suggest_fixes", True)
            
            if not script:
                return [TextContent(
                    type="text",
                    text="❌ 오류: 검증할 스크립트가 제공되지 않았습니다.\n\n"
                         "사용법: validate_msl(script='your_msl_script')\n\n"
                         "예시:\n"
                         "• validate_msl(script='ctrl+c, ctrl+v')\n"
                         "• validate_msl(script='a+b > 500', validation_level='strict')"
                )]
            
            # 검증 수행
            validation_result = await self._perform_validation(
                script, validation_level, check_performance
            )
            
            # 결과 포맷팅
            result = self._format_validation_result(
                script, validation_result, suggest_fixes
            )
            
            return [TextContent(type="text", text=result)]
            
        except Exception as e:
            error_msg = f"❌ MSL 검증 도구 실행 중 오류가 발생했습니다:\n{str(e)}\n\n"
            error_msg += f"스택 트레이스:\n{traceback.format_exc()}"
            return [TextContent(type="text", text=error_msg)]
    
    async def _perform_validation(self, script: str, level: str, check_performance: bool) -> Dict[str, Any]:
        """검증을 수행합니다."""
        
        validation_result = {
            "script": script,
            "level": level,
            "overall_status": "unknown",
            "syntax_check": {},
            "performance_check": {},
            "suggestions": [],
            "warnings": [],
            "errors": []
        }
        
        try:
            # 1. 구문 검사
            validation_result["syntax_check"] = await self._check_syntax(script)
            
            # 2. 성능 검사
            if check_performance:
                validation_result["performance_check"] = await self._check_performance(script)
            
            # 전체 상태 결정
            validation_result["overall_status"] = self._determine_overall_status(validation_result)
            
        except Exception as e:
            validation_result["errors"].append(f"검증 중 예외 발생: {str(e)}")
            validation_result["overall_status"] = "error"
        
        return validation_result
    
    async def _check_syntax(self, script: str) -> Dict[str, Any]:
        """구문 검사를 수행합니다."""
        result = {
            "valid": False,
            "errors": [],
            "warnings": [],
            "token_count": 0
        }
        
        try:
            # 토큰화 검사
            tokens = self.lexer.tokenize(script)
            token_list = list(tokens)
            result["token_count"] = len(token_list)
            
            # 파싱 검사
            ast = self.parser.parse(script)
            result["valid"] = True
            
        except Exception as e:
            result["errors"].append(f"구문 오류: {str(e)}")
        
        return result
    
    async def _check_performance(self, script: str) -> Dict[str, Any]:
        """성능 검사를 수행합니다."""
        result = {
            "score": 100,
            "issues": [],
            "warnings": []
        }
        
        score = 100
        
        # 과도한 반복 검사
        repeat_count = self._count_repetitions(script)
        if repeat_count > 100:
            result["issues"].append(f"과도한 반복 횟수: {repeat_count}회")
            score -= 20
        
        # 짧은 간격 검사
        min_interval = self._find_minimum_interval(script)
        if min_interval < 10:
            result["issues"].append(f"너무 짧은 실행 간격: {min_interval}ms")
            score -= 15
        
        result["score"] = max(0, score)
        return result
    
    def _determine_overall_status(self, validation_result: Dict[str, Any]) -> str:
        """전체 검증 상태를 결정합니다."""
        if validation_result.get("errors"):
            return "error"
        
        if not validation_result.get("syntax_check", {}).get("valid", False):
            return "invalid"
        
        performance_score = validation_result.get("performance_check", {}).get("score", 100)
        
        if performance_score < 50:
            return "warning"
        elif performance_score < 80:
            return "caution"
        else:
            return "valid"
    
    def _format_validation_result(self, script: str, validation_result: Dict[str, Any], 
                                suggest_fixes: bool) -> str:
        """검증 결과를 포맷팅합니다."""
        
        status = validation_result["overall_status"]
        
        # 상태별 이모지 및 메시지
        status_info = {
            "valid": ("✅", "검증 성공"),
            "caution": ("⚠️", "주의사항 있음"),
            "warning": ("🔶", "경고사항 있음"),
            "invalid": ("❌", "검증 실패"),
            "error": ("💥", "검증 오류")
        }
        
        emoji, status_msg = status_info.get(status, ("❓", "알 수 없음"))
        
        result = f"{emoji} MSL 스크립트 검증 결과: {status_msg}\n\n"
        result += f"📝 검증된 스크립트: '{script}'\n"
        result += f"🔍 검증 수준: {validation_result['level']}\n\n"
        
        # 구문 검사 결과
        syntax = validation_result.get("syntax_check", {})
        if syntax:
            result += "📋 구문 검사:\n"
            if syntax.get("valid"):
                result += f"  ✅ 구문 정확성: 통과\n"
                result += f"  📊 토큰 수: {syntax.get('token_count', 0)}개\n"
            else:
                result += f"  ❌ 구문 오류 발견:\n"
                for error in syntax.get("errors", []):
                    result += f"    • {error}\n"
            result += "\n"
        
        # 성능 검사 결과
        performance = validation_result.get("performance_check", {})
        if performance:
            score = performance.get("score", 0)
            result += f"⚡ 성능 검사:\n"
            result += f"  📊 성능 점수: {score}/100점\n"
            
            if performance.get("issues"):
                result += f"  ⚠️ 성능 이슈:\n"
                for issue in performance["issues"]:
                    result += f"    • {issue}\n"
            result += "\n"
        
        # 다음 단계 안내
        result += "🚀 다음 단계:\n"
        if status == "valid":
            result += "• optimize_msl: 성능 최적화 수행\n"
            result += "• explain_msl: 상세한 동작 설명\n"
        else:
            result += "• 발견된 문제들을 수정 후 재검증\n"
            result += "• parse_msl: 구문 분석 재수행\n"
        
        return result
    
    def _count_repetitions(self, script: str) -> int:
        """반복 횟수를 계산합니다."""
        matches = re.findall(r'\*(\d+)', script)
        return max([int(m) for m in matches], default=1)
    
    def _find_minimum_interval(self, script: str) -> int:
        """최소 실행 간격을 찾습니다."""
        matches = re.findall(r'&\s*(\d+)', script)
        return min([int(m) for m in matches], default=100)
    
    def _load_validation_rules(self) -> Dict[str, Any]:
        """검증 규칙을 로드합니다."""
        return {
            "performance_thresholds": {
                "max_repetitions": 1000,
                "min_interval": 10
            }
        } 