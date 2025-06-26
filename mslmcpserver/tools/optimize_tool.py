"""
MSL 최적화 도구

MSL 스크립트의 성능을 최적화하고 효율성을 개선하는 도구입니다.
중복 제거, 타이밍 최적화, 구조 개선 등을 통해 더 나은 스크립트를 생성합니다.
"""

import asyncio
import json
import traceback
import re
from typing import Dict, Any, List, Optional, Tuple
from mcp.types import TextContent, Tool

from ..msl.msl_lexer import MSLLexer
from ..msl.msl_parser import MSLParser


class OptimizeTool:
    """MSL 스크립트 최적화 도구"""
    
    def __init__(self):
        self.lexer = MSLLexer()
        self.parser = MSLParser()
        self.optimization_rules = self._load_optimization_rules()
    
    @property
    def tool_definition(self) -> Tool:
        """도구 정의를 반환합니다."""
        return Tool(
            name="optimize_msl",
            description="MSL(Macro Scripting Language) 스크립트를 최적화하여 성능과 효율성을 개선합니다. "
                       "중복 제거, 타이밍 최적화, 구조 개선 등을 수행하여 더 빠르고 안정적인 스크립트를 생성합니다.",
            inputSchema={
                "type": "object",
                "properties": {
                    "script": {
                        "type": "string",
                        "description": "최적화할 MSL 스크립트 텍스트입니다."
                    },
                    "optimization_level": {
                        "type": "string",
                        "enum": ["basic", "standard", "aggressive"],
                        "description": "최적화 수준입니다. "
                                     "basic: 기본 최적화, standard: 표준 최적화, aggressive: 적극적 최적화",
                        "default": "standard"
                    },
                    "preserve_timing": {
                        "type": "boolean",
                        "description": "기존 타이밍을 보존할지 여부입니다. true로 설정하면 타이밍 관련 최적화를 제한합니다.",
                        "default": False
                    },
                    "target_performance": {
                        "type": "string",
                        "enum": ["speed", "stability", "balanced"],
                        "description": "최적화 목표입니다. speed: 실행 속도 우선, stability: 안정성 우선, balanced: 균형",
                        "default": "balanced"
                    },
                    "show_diff": {
                        "type": "boolean",
                        "description": "원본과 최적화된 스크립트의 차이점을 보여줄지 여부입니다.",
                        "default": True
                    }
                },
                "required": ["script"]
            }
        )
    
    async def execute(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """최적화 도구를 실행합니다."""
        try:
            script = arguments.get("script", "").strip()
            optimization_level = arguments.get("optimization_level", "standard")
            preserve_timing = arguments.get("preserve_timing", False)
            target_performance = arguments.get("target_performance", "balanced")
            show_diff = arguments.get("show_diff", True)
            
            if not script:
                return [TextContent(
                    type="text",
                    text="❌ 오류: 최적화할 스크립트가 제공되지 않았습니다.\n\n"
                         "사용법: optimize_msl(script='your_msl_script')\n\n"
                         "예시:\n"
                         "• optimize_msl(script='a,a,a,b,b,c')\n"
                         "• optimize_msl(script='ctrl+c, ctrl+v', optimization_level='aggressive')"
                )]
            
            # 원본 스크립트 검증
            original_valid = await self._validate_script(script)
            if not original_valid:
                return [TextContent(
                    type="text",
                    text="❌ 원본 스크립트에 구문 오류가 있습니다. 먼저 오류를 수정해주세요.\n\n"
                         "parse_msl 또는 validate_msl 도구를 사용하여 오류를 확인할 수 있습니다."
                )]
            
            # 최적화 수행
            optimization_result = await self._perform_optimization(
                script, optimization_level, preserve_timing, target_performance
            )
            
            # 결과 포맷팅
            result = self._format_optimization_result(
                script, optimization_result, show_diff
            )
            
            return [TextContent(type="text", text=result)]
            
        except Exception as e:
            error_msg = f"❌ MSL 최적화 도구 실행 중 오류가 발생했습니다:\n{str(e)}\n\n"
            error_msg += f"스택 트레이스:\n{traceback.format_exc()}"
            return [TextContent(type="text", text=error_msg)]
    
    async def _perform_optimization(self, script: str, level: str, preserve_timing: bool, 
                                  target: str) -> Dict[str, Any]:
        """최적화를 수행합니다."""
        
        optimization_result = {
            "original_script": script,
            "optimized_script": script,
            "level": level,
            "target": target,
            "optimizations_applied": [],
            "performance_improvement": {},
            "warnings": [],
            "errors": []
        }
        
        try:
            optimized = script
            applied_optimizations = []
            
            # 1. 기본 최적화 (모든 수준에서 적용)
            optimized, basic_opts = await self._apply_basic_optimizations(optimized)
            applied_optimizations.extend(basic_opts)
            
            # 2. 표준 최적화 (standard, aggressive)
            if level in ["standard", "aggressive"]:
                optimized, standard_opts = await self._apply_standard_optimizations(
                    optimized, preserve_timing
                )
                applied_optimizations.extend(standard_opts)
            
            # 3. 적극적 최적화 (aggressive만)
            if level == "aggressive":
                optimized, aggressive_opts = await self._apply_aggressive_optimizations(
                    optimized, target
                )
                applied_optimizations.extend(aggressive_opts)
            
            # 4. 타겟별 특화 최적화
            optimized, target_opts = await self._apply_target_specific_optimizations(
                optimized, target
            )
            applied_optimizations.extend(target_opts)
            
            # 5. 최적화 결과 검증
            optimized_valid = await self._validate_script(optimized)
            if not optimized_valid:
                optimization_result["warnings"].append("최적화된 스크립트에 오류가 발생했습니다. 원본을 반환합니다.")
                optimized = script
                applied_optimizations = ["최적화 실패로 인한 원본 유지"]
            
            # 성능 개선 분석
            performance_improvement = await self._analyze_performance_improvement(
                script, optimized
            )
            
            optimization_result.update({
                "optimized_script": optimized,
                "optimizations_applied": applied_optimizations,
                "performance_improvement": performance_improvement
            })
            
        except Exception as e:
            optimization_result["errors"].append(f"최적화 중 오류 발생: {str(e)}")
            optimization_result["optimized_script"] = script
        
        return optimization_result
    
    async def _apply_basic_optimizations(self, script: str) -> Tuple[str, List[str]]:
        """기본 최적화를 적용합니다."""
        optimized = script
        applied = []
        
        # 1. 공백 정리
        original_optimized = optimized
        optimized = re.sub(r'\s+', ' ', optimized.strip())
        if optimized != original_optimized:
            applied.append("불필요한 공백 제거")
        
        # 2. 중복 쉼표 제거
        original_optimized = optimized
        optimized = re.sub(r',+', ',', optimized)
        if optimized != original_optimized:
            applied.append("중복 쉼표 제거")
        
        # 3. 연속된 동일한 키 통합
        original_optimized = optimized
        optimized = self._merge_consecutive_identical_keys(optimized)
        if optimized != original_optimized:
            applied.append("연속된 동일 키 통합")
        
        return optimized, applied
    
    async def _apply_standard_optimizations(self, script: str, preserve_timing: bool) -> Tuple[str, List[str]]:
        """표준 최적화를 적용합니다."""
        optimized = script
        applied = []
        
        # 1. 중복 패턴 제거
        original_optimized = optimized
        optimized = self._remove_duplicate_patterns(optimized)
        if optimized != original_optimized:
            applied.append("중복 패턴 제거")
        
        # 2. 타이밍 최적화 (preserve_timing=False인 경우)
        if not preserve_timing:
            original_optimized = optimized
            optimized = self._optimize_timing(optimized)
            if optimized != original_optimized:
                applied.append("타이밍 최적화")
        
        # 3. 괄호 그룹화 최적화
        original_optimized = optimized
        optimized = self._optimize_grouping(optimized)
        if optimized != original_optimized:
            applied.append("그룹화 최적화")
        
        return optimized, applied
    
    async def _apply_aggressive_optimizations(self, script: str, target: str) -> Tuple[str, List[str]]:
        """적극적 최적화를 적용합니다."""
        optimized = script
        applied = []
        
        # 1. 복잡한 패턴 재구성
        original_optimized = optimized
        optimized = self._restructure_complex_patterns(optimized)
        if optimized != original_optimized:
            applied.append("복잡한 패턴 재구성")
        
        # 2. 반복 구조 최적화
        original_optimized = optimized
        optimized = self._optimize_repetitions(optimized)
        if optimized != original_optimized:
            applied.append("반복 구조 최적화")
        
        # 3. 병렬 실행 최적화
        if target in ["speed", "balanced"]:
            original_optimized = optimized
            optimized = self._optimize_parallel_execution(optimized)
            if optimized != original_optimized:
                applied.append("병렬 실행 최적화")
        
        return optimized, applied
    
    async def _apply_target_specific_optimizations(self, script: str, target: str) -> Tuple[str, List[str]]:
        """타겟별 특화 최적화를 적용합니다."""
        optimized = script
        applied = []
        
        if target == "speed":
            # 속도 우선 최적화
            original_optimized = optimized
            optimized = self._optimize_for_speed(optimized)
            if optimized != original_optimized:
                applied.append("속도 최적화")
                
        elif target == "stability":
            # 안정성 우선 최적화
            original_optimized = optimized
            optimized = self._optimize_for_stability(optimized)
            if optimized != original_optimized:
                applied.append("안정성 최적화")
        
        # balanced는 이미 적용된 최적화들의 균형으로 처리
        
        return optimized, applied
    
    async def _analyze_performance_improvement(self, original: str, optimized: str) -> Dict[str, Any]:
        """성능 개선을 분석합니다."""
        
        # 기본 메트릭 계산
        original_length = len(original)
        optimized_length = len(optimized)
        length_reduction = original_length - optimized_length
        
        # 토큰 수 비교
        original_tokens = len(list(self.lexer.tokenize(original)))
        optimized_tokens = len(list(self.lexer.tokenize(optimized)))
        token_reduction = original_tokens - optimized_tokens
        
        # 복잡도 점수 계산 (간단한 휴리스틱)
        original_complexity = self._calculate_complexity_score(original)
        optimized_complexity = self._calculate_complexity_score(optimized)
        complexity_improvement = original_complexity - optimized_complexity
        
        # 예상 실행 시간 개선
        original_exec_time = self._estimate_execution_time(original)
        optimized_exec_time = self._estimate_execution_time(optimized)
        time_improvement = original_exec_time - optimized_exec_time
        
        return {
            "length_reduction": {
                "absolute": length_reduction,
                "percentage": round((length_reduction / original_length) * 100, 1) if original_length > 0 else 0
            },
            "token_reduction": {
                "absolute": token_reduction,
                "percentage": round((token_reduction / original_tokens) * 100, 1) if original_tokens > 0 else 0
            },
            "complexity_improvement": {
                "original_score": original_complexity,
                "optimized_score": optimized_complexity,
                "improvement": complexity_improvement
            },
            "execution_time_improvement": {
                "original_ms": original_exec_time,
                "optimized_ms": optimized_exec_time,
                "improvement_ms": time_improvement,
                "improvement_percentage": round((time_improvement / original_exec_time) * 100, 1) if original_exec_time > 0 else 0
            }
        }
    
    async def _validate_script(self, script: str) -> bool:
        """스크립트가 유효한지 검증합니다."""
        try:
            ast = self.parser.parse(script)
            return True
        except:
            return False
    
    def _merge_consecutive_identical_keys(self, script: str) -> str:
        """연속된 동일한 키를 통합합니다."""
        # 예: "a,a,a" -> "(a)*3"
        parts = script.split(',')
        if len(parts) <= 1:
            return script
        
        optimized_parts = []
        current_key = parts[0].strip()
        count = 1
        
        for i in range(1, len(parts)):
            key = parts[i].strip()
            if key == current_key and not self._is_complex_expression(key):
                count += 1
            else:
                if count > 2:
                    optimized_parts.append(f"({current_key})*{count}")
                elif count == 2:
                    optimized_parts.extend([current_key, current_key])
                else:
                    optimized_parts.append(current_key)
                current_key = key
                count = 1
        
        # 마지막 키 처리
        if count > 2:
            optimized_parts.append(f"({current_key})*{count}")
        elif count == 2:
            optimized_parts.extend([current_key, current_key])
        else:
            optimized_parts.append(current_key)
        
        return ','.join(optimized_parts)
    
    def _remove_duplicate_patterns(self, script: str) -> str:
        """중복 패턴을 제거합니다."""
        # 간단한 중복 패턴 검출 및 제거
        return script  # 실제 구현에서는 더 복잡한 로직 필요
    
    def _optimize_timing(self, script: str) -> str:
        """타이밍을 최적화합니다."""
        # 불필요하게 짧은 간격을 적절한 수준으로 조정
        optimized = re.sub(r'&\s*([1-9])\b', r'& 10', script)  # 10ms 미만을 10ms로
        return optimized
    
    def _optimize_grouping(self, script: str) -> str:
        """그룹화를 최적화합니다."""
        # 불필요한 괄호 제거 등
        return script  # 실제 구현에서는 더 복잡한 로직 필요
    
    def _restructure_complex_patterns(self, script: str) -> str:
        """복잡한 패턴을 재구성합니다."""
        return script  # 실제 구현에서는 더 복잡한 로직 필요
    
    def _optimize_repetitions(self, script: str) -> str:
        """반복 구조를 최적화합니다."""
        return script  # 실제 구현에서는 더 복잡한 로직 필요
    
    def _optimize_parallel_execution(self, script: str) -> str:
        """병렬 실행을 최적화합니다."""
        return script  # 실제 구현에서는 더 복잡한 로직 필요
    
    def _optimize_for_speed(self, script: str) -> str:
        """속도를 위해 최적화합니다."""
        # 간격을 줄이고 병렬 처리를 증가
        optimized = re.sub(r'&\s*(\d+)', lambda m: f"& {max(10, int(m.group(1)) // 2)}", script)
        return optimized
    
    def _optimize_for_stability(self, script: str) -> str:
        """안정성을 위해 최적화합니다."""
        # 간격을 늘리고 안전한 구조 사용
        optimized = re.sub(r'&\s*(\d+)', lambda m: f"& {max(50, int(m.group(1)) * 2)}", script)
        return optimized
    
    def _calculate_complexity_score(self, script: str) -> int:
        """복잡도 점수를 계산합니다."""
        score = 0
        score += len(script) // 10  # 길이 기반
        score += script.count('(') * 2  # 괄호 중첩
        score += script.count('*') * 3  # 반복 구조
        score += script.count('&') * 2  # 타이밍 제어
        return score
    
    def _estimate_execution_time(self, script: str) -> int:
        """예상 실행 시간을 밀리초로 추정합니다."""
        base_time = 100  # 기본 100ms
        
        # 키 수에 따른 시간 증가
        key_count = script.count(',') + 1
        base_time += key_count * 10
        
        # 반복에 따른 시간 증가
        for match in re.finditer(r'\*(\d+)', script):
            repeat_count = int(match.group(1))
            base_time += repeat_count * 20
        
        # 타이밍 제어에 따른 시간 증가
        for match in re.finditer(r'&\s*(\d+)', script):
            interval = int(match.group(1))
            base_time += interval
        
        # 홀드 시간 추가
        for match in re.finditer(r'>\s*(\d+)', script):
            hold_time = int(match.group(1))
            base_time += hold_time
        
        return base_time
    
    def _is_complex_expression(self, expr: str) -> bool:
        """표현식이 복잡한지 확인합니다."""
        return any(char in expr for char in ['(', ')', '+', '>', '&', '*'])
    
    def _format_optimization_result(self, original: str, optimization_result: Dict[str, Any], 
                                  show_diff: bool) -> str:
        """최적화 결과를 포맷팅합니다."""
        
        optimized = optimization_result["optimized_script"]
        applied = optimization_result["optimizations_applied"]
        performance = optimization_result["performance_improvement"]
        
        result = "🚀 MSL 스크립트 최적화 완료!\n\n"
        
        # 원본과 최적화된 스크립트
        result += f"📝 원본 스크립트: '{original}'\n"
        result += f"✨ 최적화 스크립트: '{optimized}'\n\n"
        
        # 적용된 최적화
        if applied:
            result += "🔧 적용된 최적화:\n"
            for opt in applied:
                result += f"  • {opt}\n"
        else:
            result += "🔧 적용된 최적화: 없음 (이미 최적화됨)\n"
        result += "\n"
        
        # 성능 개선 정보
        if performance:
            result += "📊 성능 개선 분석:\n"
            
            # 길이 개선
            length_improve = performance["length_reduction"]
            if length_improve["absolute"] > 0:
                result += f"  📏 길이 감소: {length_improve['absolute']}자 ({length_improve['percentage']}%)\n"
            
            # 토큰 개선
            token_improve = performance["token_reduction"]
            if token_improve["absolute"] > 0:
                result += f"  🎯 토큰 감소: {token_improve['absolute']}개 ({token_improve['percentage']}%)\n"
            
            # 복잡도 개선
            complexity = performance["complexity_improvement"]
            if complexity["improvement"] > 0:
                result += f"  🧠 복잡도 개선: {complexity['original_score']} → {complexity['optimized_score']}\n"
            
            # 실행 시간 개선
            exec_time = performance["execution_time_improvement"]
            if exec_time["improvement_ms"] > 0:
                result += f"  ⚡ 실행 시간 개선: {exec_time['improvement_ms']}ms ({exec_time['improvement_percentage']}%)\n"
            
            if all(perf["absolute"] == 0 or perf.get("improvement", 0) == 0 for perf in [length_improve, token_improve]):
                result += "  ℹ️ 이미 잘 최적화된 스크립트입니다.\n"
            result += "\n"
        
        # 차이점 표시
        if show_diff and original != optimized:
            result += "🔍 주요 변경사항:\n"
            if len(original) > len(optimized):
                result += f"  • 스크립트 길이가 {len(original) - len(optimized)}자 단축되었습니다\n"
            
            # 구체적인 변경사항 분석
            if "*" in optimized and "*" not in original:
                result += f"  • 반복 패턴이 최적화되었습니다\n"
            if "(" in optimized and "(" not in original:
                result += f"  • 그룹화가 추가되었습니다\n"
            
            result += "\n"
        
        # 다음 단계 안내
        result += "🚀 다음 단계:\n"
        result += "• validate_msl: 최적화된 스크립트 검증\n"
        result += "• explain_msl: 최적화된 스크립트 설명\n"
        result += "• parse_msl: 상세한 구조 분석"
        
        return result
    
    def _load_optimization_rules(self) -> Dict[str, Any]:
        """최적화 규칙을 로드합니다."""
        return {
            "merge_threshold": 3,  # 3개 이상 연속시 통합
            "min_interval": 10,    # 최소 간격 10ms
            "stability_interval": 50,  # 안정성 모드 최소 간격
            "speed_reduction_factor": 0.5  # 속도 모드 간격 감소율
        } 