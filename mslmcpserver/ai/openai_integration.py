"""
OpenAI GPT API를 이용한 MSL 스크립트 생성 및 분석 모듈

이 모듈은 OpenAI GPT API를 사용하여:
1. 자연어 프롬프트를 MSL 스크립트로 변환
2. MSL 스크립트 최적화 제안
3. MSL 스크립트 교육적 설명 생성
4. MSL 관련 질문에 대한 답변 제공
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from openai import AsyncOpenAI
import os
from datetime import datetime

logger = logging.getLogger(__name__)

class OpenAIIntegration:
    """OpenAI GPT API를 이용한 MSL 지원 클래스"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        OpenAI 클라이언트 초기화
        
        Args:
            api_key: OpenAI API 키 (없으면 환경변수에서 가져옴)
        """
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API 키가 필요합니다. 환경변수 OPENAI_API_KEY를 설정하거나 직접 제공하세요.")
        
        self.client = AsyncOpenAI(api_key=self.api_key)
        self.model = "gpt-4o"  # 최신 모델 사용
        
        # MSL 언어 기본 정보
        self.msl_system_prompt = self._build_msl_system_prompt()
        
    def _build_msl_system_prompt(self) -> str:
        """MSL 언어 시스템 프롬프트 구성"""
        return """
당신은 MSL(Macro Scripting Language) 전문가입니다. MSL은 게이머를 위한 직관적인 매크로 스크립팅 언어입니다.

== MSL 언어 특징 ==

1. 기본 연산자:
   - , (쉼표): 순차 실행 (A,B = A 후 B 실행)
   - + (플러스): 동시 실행 (A+B = A와 B 동시 실행)
   - > (홀드): 키 홀드 (A>B = A 누른 상태에서 B 실행)
   - | (파이프): 병렬 실행 (A|B = A와 B 병렬 실행)
   - ~ (틸드): 토글 (A~B = A 토글 후 B)
   - * (별표): 반복 (A*3 = A를 3번 반복)
   - & (앰퍼샌드): 연속 실행 (A&B = A 연속 실행 후 B)

2. 타이밍 제어:
   - (delay): 지연 시간 (100) = 100ms 지연
   - [hold]: 홀드 시간 [500] = 500ms 홀드
   - {interval}: 간격 시간 {200} = 200ms 간격
   - <fade>: 페이드 시간 <300> = 300ms 페이드

3. 특수 기능:
   - $variable: 변수 정의 및 사용
   - @(x,y): 마우스 좌표 이동
   - wheel+/wheel-: 마우스 휠 제어
   - LMB/RMB/MMB: 마우스 버튼
   - 키보드 키: A-Z, 0-9, Space, Enter, Escape 등

4. 예제:
   - Q,W,E: Q키 누르고, W키 누르고, E키 누름
   - A+B: A키와 B키 동시에 누름
   - Shift>Q: Shift 누른 상태에서 Q키 누름
   - Q*3: Q키를 3번 반복
   - @(100,200),LMB: 좌표 (100,200)으로 이동 후 좌클릭
   - Q,(200),W: Q키 누름, 200ms 지연, W키 누름

== 응답 지침 ==
1. 항상 MSL 구문을 정확히 사용하세요
2. 게이밍 상황에 맞는 실용적인 스크립트를 생성하세요
3. 초보자도 이해할 수 있도록 설명하세요
4. 성능과 안전성을 고려하세요
5. 한국어로 응답하세요
"""

    async def generate_msl_from_prompt(self, prompt: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        자연어 프롬프트로부터 MSL 스크립트 생성
        
        Args:
            prompt: 자연어 요청
            context: 추가 컨텍스트 정보
            
        Returns:
            생성된 MSL 스크립트와 메타데이터
        """
        try:
            user_prompt = f"""
다음 요청을 MSL 스크립트로 변환해주세요:

요청: {prompt}

응답 형식:
{{
    "msl_script": "생성된 MSL 스크립트",
    "description": "스크립트 설명",
    "complexity": "간단/보통/복잡",
    "estimated_duration": "예상 실행 시간 (ms)",
    "optimization_suggestions": ["최적화 제안 목록"],
    "safety_notes": ["안전성 주의사항"],
    "game_context": "적용 가능한 게임 상황"
}}
"""
            
            if context:
                user_prompt += f"\n\n추가 컨텍스트: {json.dumps(context, ensure_ascii=False, indent=2)}"
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.msl_system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            content = response.choices[0].message.content
            
            # JSON 파싱 시도
            try:
                result = json.loads(content)
            except json.JSONDecodeError:
                # JSON 파싱 실패시 텍스트에서 추출
                result = self._extract_msl_from_text(content)
            
            # 생성 시간 추가
            result["generated_at"] = datetime.now().isoformat()
            result["model_used"] = self.model
            
            return result
            
        except Exception as e:
            logger.error(f"MSL 생성 중 오류: {e}")
            return {
                "error": str(e),
                "msl_script": "",
                "description": "스크립트 생성에 실패했습니다.",
                "generated_at": datetime.now().isoformat()
            }

    async def optimize_msl_script(self, msl_script: str, optimization_level: str = "standard") -> Dict[str, Any]:
        """
        MSL 스크립트 최적화 제안 생성
        
        Args:
            msl_script: 최적화할 MSL 스크립트
            optimization_level: 최적화 수준 (basic/standard/aggressive)
            
        Returns:
            최적화된 스크립트와 제안사항
        """
        try:
            optimization_prompts = {
                "basic": "기본적인 성능 개선만 제안하세요",
                "standard": "표준적인 최적화를 수행하세요", 
                "aggressive": "공격적인 최적화를 수행하되 안전성을 유지하세요"
            }
            
            user_prompt = f"""
다음 MSL 스크립트를 {optimization_level} 수준으로 최적화해주세요:

원본 스크립트: {msl_script}

최적화 지침: {optimization_prompts.get(optimization_level, optimization_prompts["standard"])}

응답 형식:
{{
    "optimized_script": "최적화된 MSL 스크립트",
    "improvements": [
        {{
            "type": "성능/가독성/안전성",
            "description": "개선 사항 설명",
            "before": "변경 전 코드",
            "after": "변경 후 코드"
        }}
    ],
    "performance_gain": "예상 성능 향상 (%)",
    "safety_level": "안전성 등급 (높음/보통/낮음)",
    "complexity_change": "복잡도 변화 설명"
}}
"""
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.msl_system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,  # 최적화는 더 결정적으로
                max_tokens=1200
            )
            
            content = response.choices[0].message.content
            
            try:
                result = json.loads(content)
            except json.JSONDecodeError:
                result = self._extract_optimization_from_text(content, msl_script)
            
            result["optimization_level"] = optimization_level
            result["generated_at"] = datetime.now().isoformat()
            
            return result
            
        except Exception as e:
            logger.error(f"MSL 최적화 중 오류: {e}")
            return {
                "error": str(e),
                "optimized_script": msl_script,
                "improvements": [],
                "generated_at": datetime.now().isoformat()
            }

    async def explain_msl_script(self, msl_script: str, detail_level: str = "beginner") -> Dict[str, Any]:
        """
        MSL 스크립트에 대한 교육적 설명 생성
        
        Args:
            msl_script: 설명할 MSL 스크립트
            detail_level: 설명 수준 (beginner/intermediate/advanced)
            
        Returns:
            스크립트 설명과 교육 자료
        """
        try:
            detail_prompts = {
                "beginner": "초보자가 이해할 수 있도록 기초부터 자세히 설명하세요",
                "intermediate": "중급자 수준으로 핵심 개념과 응용을 설명하세요",
                "advanced": "고급 사용자를 위해 최적화와 고급 기법을 포함하여 설명하세요"
            }
            
            user_prompt = f"""
다음 MSL 스크립트를 {detail_level} 수준으로 설명해주세요:

스크립트: {msl_script}

설명 지침: {detail_prompts.get(detail_level, detail_prompts["beginner"])}

응답 형식:
{{
    "overview": "스크립트 전체 개요",
    "step_by_step": [
        {{
            "step": 1,
            "code": "해당 부분 코드",
            "explanation": "단계별 설명",
            "key_concepts": ["핵심 개념들"]
        }}
    ],
    "execution_flow": "실행 흐름 설명",
    "learning_points": ["학습 포인트들"],
    "related_concepts": ["관련 개념들"],
    "practice_suggestions": ["연습 제안들"],
    "difficulty_level": "난이도 (1-10)",
    "estimated_learning_time": "예상 학습 시간"
}}
"""
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.msl_system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.5,
                max_tokens=1500
            )
            
            content = response.choices[0].message.content
            
            try:
                result = json.loads(content)
            except json.JSONDecodeError:
                result = self._extract_explanation_from_text(content, msl_script)
            
            result["detail_level"] = detail_level
            result["generated_at"] = datetime.now().isoformat()
            
            return result
            
        except Exception as e:
            logger.error(f"MSL 설명 생성 중 오류: {e}")
            return {
                "error": str(e),
                "overview": "스크립트 설명 생성에 실패했습니다.",
                "generated_at": datetime.now().isoformat()
            }

    async def validate_msl_script(self, msl_script: str) -> Dict[str, Any]:
        """
        MSL 스크립트 유효성 검증 및 개선 제안
        
        Args:
            msl_script: 검증할 MSL 스크립트
            
        Returns:
            검증 결과와 개선 제안
        """
        try:
            user_prompt = f"""
다음 MSL 스크립트의 유효성을 검증하고 개선점을 제안해주세요:

스크립트: {msl_script}

검증 항목:
1. 문법 정확성
2. 성능 효율성
3. 안전성
4. 가독성
5. 게임 적용 가능성

응답 형식:
{{
    "is_valid": true/false,
    "syntax_errors": ["문법 오류들"],
    "warnings": ["경고 사항들"],
    "suggestions": [
        {{
            "type": "문법/성능/안전성/가독성",
            "severity": "높음/보통/낮음",
            "description": "제안 설명",
            "fix": "수정 방법"
        }}
    ],
    "performance_score": "성능 점수 (1-10)",
    "safety_score": "안전성 점수 (1-10)",
    "overall_quality": "전체 품질 평가"
}}
"""
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.msl_system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2,  # 검증은 엄격하게
                max_tokens=1000
            )
            
            content = response.choices[0].message.content
            
            try:
                result = json.loads(content)
            except json.JSONDecodeError:
                result = self._extract_validation_from_text(content, msl_script)
            
            result["generated_at"] = datetime.now().isoformat()
            
            return result
            
        except Exception as e:
            logger.error(f"MSL 검증 중 오류: {e}")
            return {
                "error": str(e),
                "is_valid": False,
                "generated_at": datetime.now().isoformat()
            }

    async def get_msl_examples(self, category: str = "basic", game_context: str = None) -> Dict[str, Any]:
        """
        카테고리별 MSL 예제 생성
        
        Args:
            category: 예제 카테고리 (basic/combat/movement/complex 등)
            game_context: 게임 컨텍스트 (fps/moba/rpg 등)
            
        Returns:
            카테고리별 MSL 예제들
        """
        try:
            context_info = f" ({game_context} 게임 상황)" if game_context else ""
            
            user_prompt = f"""
{category} 카테고리의 MSL 예제들을 생성해주세요{context_info}:

응답 형식:
{{
    "category": "{category}",
    "game_context": "{game_context or 'general'}",
    "examples": [
        {{
            "title": "예제 제목",
            "description": "예제 설명",
            "msl_script": "MSL 스크립트",
            "use_case": "사용 상황",
            "difficulty": "난이도 (1-5)",
            "tags": ["태그들"]
        }}
    ],
    "learning_progression": ["학습 순서 추천"],
    "related_categories": ["관련 카테고리들"]
}}
"""
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.msl_system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.8,  # 예제는 다양하게
                max_tokens=1500
            )
            
            content = response.choices[0].message.content
            
            try:
                result = json.loads(content)
            except json.JSONDecodeError:
                result = self._extract_examples_from_text(content, category)
            
            result["generated_at"] = datetime.now().isoformat()
            
            return result
            
        except Exception as e:
            logger.error(f"MSL 예제 생성 중 오류: {e}")
            return {
                "error": str(e),
                "category": category,
                "examples": [],
                "generated_at": datetime.now().isoformat()
            }

    def _extract_msl_from_text(self, text: str) -> Dict[str, Any]:
        """텍스트에서 MSL 정보 추출 (JSON 파싱 실패시 대안)"""
        # 기본 구조 반환
        return {
            "msl_script": "",
            "description": text,
            "complexity": "unknown",
            "estimated_duration": "0",
            "optimization_suggestions": [],
            "safety_notes": [],
            "game_context": "general"
        }

    def _extract_optimization_from_text(self, text: str, original_script: str) -> Dict[str, Any]:
        """텍스트에서 최적화 정보 추출"""
        return {
            "optimized_script": original_script,
            "improvements": [],
            "performance_gain": "0%",
            "safety_level": "unknown",
            "complexity_change": text
        }

    def _extract_explanation_from_text(self, text: str, msl_script: str) -> Dict[str, Any]:
        """텍스트에서 설명 정보 추출"""
        return {
            "overview": text,
            "step_by_step": [],
            "execution_flow": text,
            "learning_points": [],
            "related_concepts": [],
            "practice_suggestions": [],
            "difficulty_level": "5",
            "estimated_learning_time": "unknown"
        }

    def _extract_validation_from_text(self, text: str, msl_script: str) -> Dict[str, Any]:
        """텍스트에서 검증 정보 추출"""
        return {
            "is_valid": True,
            "syntax_errors": [],
            "warnings": [],
            "suggestions": [],
            "performance_score": "5",
            "safety_score": "5",
            "overall_quality": text
        }

    def _extract_examples_from_text(self, text: str, category: str) -> Dict[str, Any]:
        """텍스트에서 예제 정보 추출"""
        return {
            "category": category,
            "game_context": "general",
            "examples": [],
            "learning_progression": [],
            "related_categories": []
        }

    async def close(self):
        """리소스 정리"""
        await self.client.close()

# 전역 인스턴스 (싱글톤 패턴)
_openai_instance = None

async def get_openai_integration() -> OpenAIIntegration:
    """OpenAI 통합 인스턴스 가져오기"""
    global _openai_instance
    if _openai_instance is None:
        _openai_instance = OpenAIIntegration()
    return _openai_instance

async def cleanup_openai_integration():
    """OpenAI 통합 인스턴스 정리"""
    global _openai_instance
    if _openai_instance:
        await _openai_instance.close()
        _openai_instance = None 