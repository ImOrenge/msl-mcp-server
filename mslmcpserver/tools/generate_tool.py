"""
MSL 생성 도구

자연어 프롬프트를 받아 MSL 스크립트를 자동 생성하는 도구입니다.
OpenAI GPT API를 활용하여 정확하고 효율적인 MSL 스크립트를 생성합니다.
"""

import asyncio
import json
import traceback
from typing import Dict, Any, List, Optional
from mcp.types import TextContent, Tool

from ..msl.msl_lexer import MSLLexer
from ..msl.msl_parser import MSLParser
from ..ai.openai_integration import get_openai_integration


class GenerateTool:
    """MSL 스크립트 자동 생성 도구"""
    
    def __init__(self):
        self.lexer = MSLLexer()
        self.parser = MSLParser()
        self.msl_patterns = self._load_msl_patterns()
    
    @property
    def tool_definition(self) -> Tool:
        """도구 정의를 반환합니다."""
        return Tool(
            name="generate_msl",
            description="자연어 프롬프트를 기반으로 MSL(Macro Scripting Language) 스크립트를 자동 생성합니다. "
                       "Context7과 AI를 활용하여 사용자의 의도에 맞는 정확한 MSL 스크립트를 생성합니다.",
            inputSchema={
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "생성할 매크로의 동작을 설명하는 자연어 프롬프트입니다. "
                                     "예: '컨트롤C 누르고 컨트롤V를 누르는 매크로' 또는 '공격키를 연속으로 5번 누르기'"
                    },
                    "game_context": {
                        "type": "string",
                        "description": "게임 컨텍스트 정보 (선택사항). 특정 게임에 최적화된 스크립트를 생성합니다. "
                                     "예: 'FPS게임', 'MMORPG', 'RTS게임' 등",
                        "default": ""
                    },
                    "complexity": {
                        "type": "string",
                        "enum": ["simple", "medium", "complex"],
                        "description": "생성할 스크립트의 복잡도 수준입니다. "
                                     "simple: 기본적인 키 조합, medium: 타이밍 제어 포함, complex: 고급 기능 활용",
                        "default": "medium"
                    },
                    "optimize": {
                        "type": "boolean",
                        "description": "생성된 스크립트를 자동으로 최적화할지 여부입니다.",
                        "default": True
                    },
                    "include_explanation": {
                        "type": "boolean", 
                        "description": "생성된 스크립트에 대한 상세 설명을 포함할지 여부입니다.",
                        "default": True
                    }
                },
                "required": ["prompt"]
            }
        )
    
    async def execute(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """MSL 생성 도구를 실행합니다."""
        try:
            prompt = arguments.get("prompt", "").strip()
            game_context = arguments.get("game_context", "")
            complexity = arguments.get("complexity", "medium")
            optimize = arguments.get("optimize", True)
            include_explanation = arguments.get("include_explanation", True)
            
            if not prompt:
                return [TextContent(
                    type="text",
                    text="❌ 오류: 생성할 매크로에 대한 설명이 제공되지 않았습니다.\n\n"
                         "사용법: generate_msl(prompt='원하는 매크로 동작 설명')\n\n"
                         "예시:\n"
                         "• generate_msl(prompt='컨트롤C 누르고 컨트롤V 누르기')\n"
                         "• generate_msl(prompt='공격키를 연속으로 5번 누르기')\n"
                         "• generate_msl(prompt='마우스 좌클릭 후 우클릭하기')"
                )]
            
            # 1. 프롬프트 분석 및 MSL 패턴 매칭
            analysis_result = await self._analyze_prompt(prompt, game_context, complexity)
            analysis_result["original_prompt"] = prompt
            
            # 2. MSL 스크립트 생성
            msl_script = await self._generate_msl_script(analysis_result)
            
            # 3. 생성된 스크립트 검증
            validation_result = await self._validate_generated_script(msl_script)
            
            if not validation_result["valid"]:
                # 검증 실패 시 재생성 시도
                msl_script = await self._fix_script_errors(msl_script, validation_result["errors"])
                validation_result = await self._validate_generated_script(msl_script)
            
            # 4. 최적화 (요청된 경우)
            if optimize and validation_result["valid"]:
                msl_script = await self._optimize_script(msl_script)
            
            # 5. 결과 포맷팅
            result = self._format_generation_result(
                prompt, msl_script, analysis_result, 
                validation_result, include_explanation
            )
            
            return [TextContent(type="text", text=result)]
            
        except Exception as e:
            error_msg = f"❌ MSL 생성 도구 실행 중 오류가 발생했습니다:\n{str(e)}\n\n"
            error_msg += f"스택 트레이스:\n{traceback.format_exc()}"
            return [TextContent(type="text", text=error_msg)]
    
    async def _analyze_prompt(self, prompt: str, game_context: str, complexity: str) -> Dict[str, Any]:
        """프롬프트를 분석하여 MSL 생성에 필요한 정보를 추출합니다."""
        
        # 키워드 기반 패턴 매칭
        analysis = {
            "action_type": "sequential",  # sequential, simultaneous, hold, repeat
            "keys": [],
            "timing": [],
            "modifiers": [],
            "mouse_actions": [],
            "special_features": [],
            "estimated_complexity": complexity
        }
        
        # 일반적인 키 패턴 인식
        key_patterns = {
            "컨트롤c": "ctrl+c",
            "컨트롤v": "ctrl+v", 
            "컨트롤a": "ctrl+a",
            "컨트롤z": "ctrl+z",
            "컨트롤s": "ctrl+s",
            "엔터": "enter",
            "스페이스": "space",
            "백스페이스": "backspace",
            "탭": "tab",
            "시프트": "shift",
            "알트": "alt",
            "공격": "q",
            "스킬": "w",
            "이동": "wasd",
            "점프": "space"
        }
        
        # 동작 타입 인식
        if "동시에" in prompt or "함께" in prompt or "같이" in prompt:
            analysis["action_type"] = "simultaneous"
        elif "연속" in prompt or "계속" in prompt or "반복" in prompt:
            analysis["action_type"] = "repeat"
        elif "누르고 있" in prompt or "홀드" in prompt:
            analysis["action_type"] = "hold"
        
        # 키 추출
        for korean, msl_key in key_patterns.items():
            if korean in prompt.lower():
                analysis["keys"].append(msl_key)
        
        # 숫자 추출 (반복 횟수 등)
        import re
        numbers = re.findall(r'\d+', prompt)
        if numbers:
            analysis["repeat_count"] = int(numbers[0])
        
        # 마우스 동작 인식
        if "클릭" in prompt:
            if "좌클릭" in prompt or "왼쪽클릭" in prompt:
                analysis["mouse_actions"].append("lclick")
            if "우클릭" in prompt or "오른쪽클릭" in prompt:
                analysis["mouse_actions"].append("rclick")
            if "클릭" in prompt and "좌" not in prompt and "우" not in prompt:
                analysis["mouse_actions"].append("lclick")
        
        # 타이밍 정보
        if "빠르게" in prompt:
            analysis["timing"].append("fast")
        elif "천천히" in prompt:
            analysis["timing"].append("slow")
        elif "지연" in prompt or "대기" in prompt:
            analysis["timing"].append("delay")
        
        return analysis
    
    async def _generate_msl_script(self, analysis: Dict[str, Any]) -> str:
        """분석 결과를 바탕으로 MSL 스크립트를 생성합니다."""
        
        # OpenAI 통합을 시도하되, 실패시 기본 패턴 매칭 사용
        try:
            openai_integration = await get_openai_integration()
            prompt = analysis.get("original_prompt", "")
            
            if prompt:
                # OpenAI로 MSL 생성 시도
                result = await openai_integration.generate_msl_from_prompt(
                    prompt=prompt,
                    context={
                        "complexity": analysis.get("estimated_complexity", "medium"),
                        "game_context": analysis.get("game_context", ""),
                        "action_type": analysis.get("action_type", "sequential")
                    }
                )
                
                if result.get("msl_script") and not result.get("error"):
                    return result["msl_script"]
        except Exception as e:
            # OpenAI 실패시 기본 방식으로 폴백
            print(f"OpenAI 생성 실패, 기본 방식 사용: {e}")
        
        # 기본 패턴 매칭 방식으로 폴백
        action_type = analysis["action_type"]
        keys = analysis["keys"]
        mouse_actions = analysis["mouse_actions"]
        repeat_count = analysis.get("repeat_count", 1)
        timing = analysis["timing"]
        
        # 기본 키/마우스 액션 결합
        actions = keys + mouse_actions
        
        if not actions:
            return "# 인식된 키/마우스 액션이 없습니다"
        
        # 액션 타입에 따른 MSL 스크립트 생성
        if action_type == "simultaneous":
            # 동시 실행: +로 연결
            script = "+".join(actions)
            
        elif action_type == "repeat":
            # 반복 실행: *로 반복
            base_script = ",".join(actions) if len(actions) > 1 else actions[0]
            script = f"({base_script})*{repeat_count}"
            
        elif action_type == "hold":
            # 홀드 실행: >로 홀드
            base_script = ",".join(actions) if len(actions) > 1 else actions[0]
            hold_time = 1000  # 기본 1초
            script = f"{base_script} > {hold_time}"
            
        else:  # sequential
            # 순차 실행: ,로 연결
            script = ",".join(actions)
        
        # 타이밍 조정
        if "fast" in timing:
            script = f"{script} & 50"  # 50ms 간격
        elif "slow" in timing:
            script = f"{script} & 500"  # 500ms 간격
        elif "delay" in timing:
            script = f"(200), {script}"  # 200ms 지연
        
        return script
    
    async def _validate_generated_script(self, script: str) -> Dict[str, Any]:
        """생성된 MSL 스크립트를 검증합니다."""
        try:
            # 파싱 시도
            ast = self.parser.parse(script)
            return {
                "valid": True,
                "errors": [],
                "warnings": []
            }
        except Exception as e:
            return {
                "valid": False,
                "errors": [str(e)],
                "warnings": []
            }
    
    async def _fix_script_errors(self, script: str, errors: List[str]) -> str:
        """스크립트 오류를 수정합니다."""
        # 간단한 오류 수정 로직
        fixed_script = script
        
        # 일반적인 오류 패턴 수정
        if "undefined" in str(errors):
            # 정의되지 않은 키 수정
            fixed_script = fixed_script.replace("wasd", "w,a,s,d")
        
        # 구문 오류 수정
        if "syntax" in str(errors).lower():
            # 공백 제거 및 기본 포맷팅
            fixed_script = fixed_script.strip().replace("  ", " ")
        
        return fixed_script
    
    async def _optimize_script(self, script: str) -> str:
        """MSL 스크립트를 최적화합니다."""
        # 기본적인 최적화 로직
        optimized = script
        
        # 중복 제거
        if ",," in optimized:
            optimized = optimized.replace(",,", ",")
        
        # 불필요한 공백 제거
        optimized = optimized.strip()
        
        return optimized
    
    def _format_generation_result(self, prompt: str, script: str, analysis: Dict, 
                                validation: Dict, include_explanation: bool) -> str:
        """생성 결과를 포맷팅합니다."""
        
        result = "🎯 MSL 스크립트 생성 완료!\n\n"
        result += f"📝 입력 프롬프트: '{prompt}'\n\n"
        
        # 생성된 스크립트
        result += "🔧 생성된 MSL 스크립트:\n"
        result += f"```msl\n{script}\n```\n\n"
        
        # 검증 결과
        if validation["valid"]:
            result += "✅ 스크립트 검증: 성공\n"
        else:
            result += "⚠️ 스크립트 검증: 일부 오류 있음\n"
            for error in validation["errors"]:
                result += f"  • {error}\n"
        result += "\n"
        
        if include_explanation:
            # 분석 정보
            result += "📊 분석 정보:\n"
            result += f"• 동작 타입: {analysis['action_type']}\n"
            result += f"• 인식된 키: {', '.join(analysis['keys']) if analysis['keys'] else '없음'}\n"
            result += f"• 마우스 동작: {', '.join(analysis['mouse_actions']) if analysis['mouse_actions'] else '없음'}\n"
            if analysis.get('repeat_count'):
                result += f"• 반복 횟수: {analysis['repeat_count']}회\n"
            result += "\n"
            
            # 스크립트 설명
            result += "💡 스크립트 설명:\n"
            result += self._explain_script(script)
            result += "\n"
        
        # 다음 단계 안내
        result += "🚀 다음 단계:\n"
        result += "• parse_msl: 생성된 스크립트 상세 분석\n"
        result += "• validate_msl: 추가 검증 수행\n"
        result += "• optimize_msl: 성능 최적화\n"
        result += "• explain_msl: 상세한 동작 설명"
        
        return result
    
    def _explain_script(self, script: str) -> str:
        """스크립트의 동작을 설명합니다."""
        explanation = ""
        
        if "+" in script:
            explanation += "• 키들을 동시에 누릅니다\n"
        if "," in script:
            explanation += "• 키들을 순차적으로 누릅니다\n"
        if "*" in script:
            explanation += "• 지정된 횟수만큼 반복 실행됩니다\n"
        if ">" in script:
            explanation += "• 키를 일정 시간 동안 누르고 있습니다\n"
        if "&" in script:
            explanation += "• 키 입력 간격이 조정됩니다\n"
        
        if not explanation:
            explanation = "• 기본적인 키 입력을 수행합니다\n"
        
        return explanation
    
    def _load_msl_patterns(self) -> Dict[str, Any]:
        """MSL 패턴 데이터베이스를 로드합니다."""
        return {
            "common_combos": {
                "copy_paste": "ctrl+c, ctrl+v",
                "select_all": "ctrl+a",
                "save": "ctrl+s",
                "undo": "ctrl+z"
            },
            "gaming_patterns": {
                "attack_combo": "q, w, e",
                "movement": "w, a, s, d",
                "quick_skill": "q+shift"
            }
        } 