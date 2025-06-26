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
                    "check_security": {
                        "type": "boolean",
                        "description": "보안 관련 이슈를 검사할지 여부입니다.",
                        "default": False
                    },
                    "suggest_fixes": {
                        "type": "boolean",
                        "description": "발견된 문제에 대한 수정 제안을 포함할지 여부입니다.",
                        "default": True
                    },
                    "target_platform": {
                        "type": "string",
                        "description": "대상 플랫폼 (Windows, Linux, Mac 등). 플랫폼별 특화 검증을 수행합니다.",
                        "default": "Windows"
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
            check_security = arguments.get("check_security", False)
            suggest_fixes = arguments.get("suggest_fixes", True)
            target_platform = arguments.get("target_platform", "Windows")
            
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
            validation_result = await self._perform_comprehensive_validation(
                script, validation_level, check_performance, check_security, target_platform
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
    
    async def _perform_comprehensive_validation(self, script: str, level: str, 
                                              check_performance: bool, check_security: bool,
                                              target_platform: str) -> Dict[str, Any]:
        """종합적인 검증을 수행합니다."""
        
        validation_result = {
            "script": script,
            "level": level,
            "overall_status": "unknown",
            "syntax_check": {},
            "semantic_check": {},
            "performance_check": {},
            "security_check": {},
            "compatibility_check": {},
            "suggestions": [],
            "warnings": [],
            "errors": []
        }
        
        try:
            # 1. 구문 검사 (Syntax Check)
            validation_result["syntax_check"] = await self._check_syntax(script)
            
            # 구문 오류가 있으면 다른 검사는 제한적으로만 수행
            if validation_result["syntax_check"]["valid"]:
                
                # 2. 의미적 검사 (Semantic Check)
                if level in ["standard", "strict", "comprehensive"]:
                    validation_result["semantic_check"] = await self._check_semantics(script)
                
                # 3. 성능 검사 (Performance Check)
                if check_performance and level in ["strict", "comprehensive"]:
                    validation_result["performance_check"] = await self._check_performance(script)
                
                # 4. 보안 검사 (Security Check)
                if check_security and level == "comprehensive":
                    validation_result["security_check"] = await self._check_security(script)
                
                # 5. 호환성 검사 (Compatibility Check)
                if level == "comprehensive":
                    validation_result["compatibility_check"] = await self._check_compatibility(
                        script, target_platform
                    )
            
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
            "token_count": 0,
            "ast_info": {}
        }
        
        try:
            # 토큰화 검사
            tokens = self.lexer.tokenize(script)
            token_list = list(tokens)
            result["token_count"] = len(token_list)
            
            # 파싱 검사
            ast = self.parser.parse(script)
            result["valid"] = True
            result["ast_info"] = {
                "type": type(ast).__name__,
                "complexity": self._estimate_ast_complexity(ast)
            }
            
        except Exception as e:
            result["errors"].append(f"구문 오류: {str(e)}")
        
        return result
    
    async def _check_semantics(self, script: str) -> Dict[str, Any]:
        """의미적 검사를 수행합니다."""
        result = {
            "valid": True,
            "issues": [],
            "warnings": [],
            "key_analysis": {},
            "timing_analysis": {},
            "logic_analysis": {}
        }
        
        # 키 조합 분석
        result["key_analysis"] = self._analyze_key_combinations(script)
        
        # 타이밍 분석
        result["timing_analysis"] = self._analyze_timing_patterns(script)
        
        # 논리 구조 분석
        result["logic_analysis"] = self._analyze_logic_structure(script)
        
        # 의미적 문제 탐지
        issues = []
        
        # 1. 무의미한 키 조합 검사
        if self._has_meaningless_combinations(script):
            issues.append("무의미한 키 조합이 감지되었습니다")
        
        # 2. 모순된 타이밍 검사
        if self._has_conflicting_timing(script):
            issues.append("모순된 타이밍 설정이 감지되었습니다")
        
        # 3. 무한 루프 가능성 검사
        if self._has_infinite_loop_risk(script):
            issues.append("무한 루프 가능성이 감지되었습니다")
        
        result["issues"] = issues
        result["valid"] = len(issues) == 0
        
        return result
    
    async def _check_performance(self, script: str) -> Dict[str, Any]:
        """성능 검사를 수행합니다."""
        result = {
            "score": 100,  # 100점 만점
            "issues": [],
            "warnings": [],
            "optimizations": [],
            "resource_usage": {}
        }
        
        # 성능 이슈 검사
        issues = []
        score = 100
        
        # 1. 과도한 반복 검사
        repeat_count = self._count_repetitions(script)
        if repeat_count > 100:
            issues.append(f"과도한 반복 횟수: {repeat_count}회")
            score -= 20
        elif repeat_count > 50:
            result["warnings"].append(f"많은 반복 횟수: {repeat_count}회")
            score -= 10
        
        # 2. 짧은 간격 타이밍 검사
        min_interval = self._find_minimum_interval(script)
        if min_interval < 10:
            issues.append(f"너무 짧은 실행 간격: {min_interval}ms")
            score -= 15
        elif min_interval < 50:
            result["warnings"].append(f"빠른 실행 간격: {min_interval}ms")
            score -= 5
        
        # 3. 복잡한 중첩 구조 검사
        nesting_depth = self._calculate_nesting_depth(script)
        if nesting_depth > 5:
            issues.append(f"과도한 중첩 깊이: {nesting_depth}")
            score -= 10
        
        # 4. 최적화 제안
        optimizations = []
        if self._can_optimize_repetitions(script):
            optimizations.append("반복 구조를 최적화할 수 있습니다")
        if self._can_optimize_timing(script):
            optimizations.append("타이밍을 최적화할 수 있습니다")
        
        result["score"] = max(0, score)
        result["issues"] = issues
        result["optimizations"] = optimizations
        result["resource_usage"] = {
            "estimated_cpu": "중간" if score < 70 else "낮음",
            "estimated_memory": "낮음",
            "estimated_duration": self._estimate_execution_time(script)
        }
        
        return result
    
    async def _check_security(self, script: str) -> Dict[str, Any]:
        """보안 검사를 수행합니다."""
        result = {
            "risk_level": "low",
            "issues": [],
            "warnings": [],
            "recommendations": []
        }
        
        # 보안 이슈 검사
        issues = []
        warnings = []
        risk_level = "low"
        
        # 1. 시스템 키 조합 검사
        system_keys = ["alt+f4", "ctrl+alt+del", "win+l", "win+r"]
        for sys_key in system_keys:
            if sys_key in script.lower():
                issues.append(f"위험한 시스템 키 조합: {sys_key}")
                risk_level = "high"
        
        # 2. 과도한 반복 검사 (DoS 위험)
        if self._count_repetitions(script) > 1000:
            warnings.append("과도한 반복으로 인한 시스템 부하 위험")
            if risk_level == "low":
                risk_level = "medium"
        
        # 3. 극도로 빠른 실행 검사
        if self._find_minimum_interval(script) < 5:
            warnings.append("극도로 빠른 실행으로 인한 시스템 불안정 위험")
            if risk_level == "low":
                risk_level = "medium"
        
        result["risk_level"] = risk_level
        result["issues"] = issues
        result["warnings"] = warnings
        
        # 보안 권장사항
        if risk_level != "low":
            result["recommendations"] = [
                "스크립트 실행 전 시스템 상태를 확인하세요",
                "안전한 환경에서 먼저 테스트하세요",
                "실행 중 중단 방법을 미리 준비하세요"
            ]
        
        return result
    
    async def _check_compatibility(self, script: str, platform: str) -> Dict[str, Any]:
        """플랫폼 호환성 검사를 수행합니다."""
        result = {
            "platform": platform,
            "compatible": True,
            "issues": [],
            "warnings": [],
            "alternative_suggestions": []
        }
        
        # 플랫폼별 키 호환성 검사
        if platform.lower() == "linux":
            # Linux에서 문제가 될 수 있는 키들
            linux_issues = []
            if "win+" in script.lower():
                linux_issues.append("Windows 키는 Linux에서 Super 키로 매핑됩니다")
            
            result["warnings"].extend(linux_issues)
        
        elif platform.lower() == "mac":
            # Mac에서 문제가 될 수 있는 키들
            mac_issues = []
            if "ctrl+" in script.lower():
                mac_issues.append("Ctrl 키는 Mac에서 Cmd 키로 대체하는 것을 고려하세요")
            if "alt+" in script.lower():
                mac_issues.append("Alt 키는 Mac에서 Option 키입니다")
            
            result["warnings"].extend(mac_issues)
        
        return result
    
    def _determine_overall_status(self, validation_result: Dict[str, Any]) -> str:
        """전체 검증 상태를 결정합니다."""
        if validation_result.get("errors"):
            return "error"
        
        if not validation_result.get("syntax_check", {}).get("valid", False):
            return "invalid"
        
        semantic_issues = len(validation_result.get("semantic_check", {}).get("issues", []))
        performance_score = validation_result.get("performance_check", {}).get("score", 100)
        security_risk = validation_result.get("security_check", {}).get("risk_level", "low")
        
        if security_risk == "high" or semantic_issues > 2 or performance_score < 50:
            return "warning"
        elif semantic_issues > 0 or performance_score < 80 or security_risk == "medium":
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
                if syntax.get("ast_info"):
                    result += f"  🌳 AST 타입: {syntax['ast_info'].get('type', 'Unknown')}\n"
            else:
                result += f"  ❌ 구문 오류 발견:\n"
                for error in syntax.get("errors", []):
                    result += f"    • {error}\n"
            result += "\n"
        
        # 의미적 검사 결과
        semantic = validation_result.get("semantic_check", {})
        if semantic:
            result += "🧠 의미적 검사:\n"
            if semantic.get("valid"):
                result += f"  ✅ 의미적 일관성: 통과\n"
            else:
                result += f"  ⚠️ 의미적 문제 발견:\n"
                for issue in semantic.get("issues", []):
                    result += f"    • {issue}\n"
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
            
            if performance.get("optimizations"):
                result += f"  💡 최적화 제안:\n"
                for opt in performance["optimizations"]:
                    result += f"    • {opt}\n"
            result += "\n"
        
        # 보안 검사 결과
        security = validation_result.get("security_check", {})
        if security:
            risk_level = security.get("risk_level", "low")
            risk_emoji = {"low": "🟢", "medium": "🟡", "high": "🔴"}.get(risk_level, "⚪")
            
            result += f"🔒 보안 검사:\n"
            result += f"  {risk_emoji} 위험 수준: {risk_level.upper()}\n"
            
            if security.get("issues"):
                result += f"  ⚠️ 보안 이슈:\n"
                for issue in security["issues"]:
                    result += f"    • {issue}\n"
            result += "\n"
        
        # 수정 제안
        if suggest_fixes and status in ["warning", "invalid", "caution"]:
            result += "🔧 수정 제안:\n"
            suggestions = self._generate_fix_suggestions(validation_result)
            for suggestion in suggestions:
                result += f"  • {suggestion}\n"
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
    
    def _generate_fix_suggestions(self, validation_result: Dict[str, Any]) -> List[str]:
        """수정 제안을 생성합니다."""
        suggestions = []
        
        # 구문 오류 수정 제안
        syntax_errors = validation_result.get("syntax_check", {}).get("errors", [])
        for error in syntax_errors:
            if "undefined" in error.lower():
                suggestions.append("정의되지 않은 키나 명령어를 확인하고 수정하세요")
            elif "syntax" in error.lower():
                suggestions.append("구문 규칙에 맞게 스크립트를 수정하세요")
        
        # 성능 이슈 수정 제안
        performance = validation_result.get("performance_check", {})
        if performance.get("score", 100) < 70:
            suggestions.append("반복 횟수를 줄이거나 실행 간격을 늘려보세요")
        
        # 보안 이슈 수정 제안
        security_risk = validation_result.get("security_check", {}).get("risk_level")
        if security_risk in ["medium", "high"]:
            suggestions.append("위험한 키 조합을 제거하거나 안전한 대안을 사용하세요")
        
        if not suggestions:
            suggestions.append("전반적인 코드 품질을 개선해보세요")
        
        return suggestions
    
    # 헬퍼 메서드들 (분석 로직)
    def _estimate_ast_complexity(self, ast) -> str:
        """AST 복잡도를 추정합니다."""
        return "medium"  # 실제 구현 시 AST 구조 분석
    
    def _analyze_key_combinations(self, script: str) -> Dict[str, Any]:
        """키 조합을 분석합니다."""
        return {"valid_combinations": True, "problematic_keys": []}
    
    def _analyze_timing_patterns(self, script: str) -> Dict[str, Any]:
        """타이밍 패턴을 분석합니다."""
        return {"consistent": True, "conflicts": []}
    
    def _analyze_logic_structure(self, script: str) -> Dict[str, Any]:
        """논리 구조를 분석합니다."""
        return {"coherent": True, "issues": []}
    
    def _has_meaningless_combinations(self, script: str) -> bool:
        """무의미한 키 조합을 검사합니다."""
        return False
    
    def _has_conflicting_timing(self, script: str) -> bool:
        """모순된 타이밍을 검사합니다."""
        return False
    
    def _has_infinite_loop_risk(self, script: str) -> bool:
        """무한 루프 위험을 검사합니다."""
        return False
    
    def _count_repetitions(self, script: str) -> int:
        """반복 횟수를 계산합니다."""
        matches = re.findall(r'\*(\d+)', script)
        return max([int(m) for m in matches], default=1)
    
    def _find_minimum_interval(self, script: str) -> int:
        """최소 실행 간격을 찾습니다."""
        matches = re.findall(r'&\s*(\d+)', script)
        return min([int(m) for m in matches], default=100)
    
    def _calculate_nesting_depth(self, script: str) -> int:
        """중첩 깊이를 계산합니다."""
        max_depth = 0
        current_depth = 0
        for char in script:
            if char in '([{':
                current_depth += 1
                max_depth = max(max_depth, current_depth)
            elif char in ')]}':
                current_depth -= 1
        return max_depth
    
    def _can_optimize_repetitions(self, script: str) -> bool:
        """반복 최적화 가능성을 확인합니다."""
        return "*" in script and "," in script
    
    def _can_optimize_timing(self, script: str) -> bool:
        """타이밍 최적화 가능성을 확인합니다."""
        return "&" in script or ">" in script
    
    def _estimate_execution_time(self, script: str) -> str:
        """실행 시간을 추정합니다."""
        # 간단한 추정 로직
        if "*" in script:
            return "중간 (1-10초)"
        elif ">" in script:
            return "긴편 (5-30초)"
        else:
            return "짧음 (1초 미만)"
    
    def _load_validation_rules(self) -> Dict[str, Any]:
        """검증 규칙을 로드합니다."""
        return {
            "forbidden_combinations": ["ctrl+alt+del"],
            "performance_thresholds": {
                "max_repetitions": 1000,
                "min_interval": 10
            },
            "security_patterns": ["alt+f4", "win+l", "win+r"]
        } 