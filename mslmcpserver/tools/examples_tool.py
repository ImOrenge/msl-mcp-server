"""
MSL 스크립트 예제 제공 도구
다양한 MSL 예제를 카테고리별, 난이도별로 제공하는 교육용 도구
"""

import asyncio
from typing import Dict, Any, List, Optional
from ..msl.msl_parser import MSLParser
from ..msl.msl_lexer import MSLLexer

class ExamplesTool:
    """
    MSL 스크립트 예제 제공 도구
    
    주요 기능:
    - 카테고리별 MSL 예제 제공
    - 난이도별 학습 경로 제공
    - 게임 장르별 특화 예제 제공
    - 대화형 예제 검색 및 필터링
    """
    
    def __init__(self):
        """도구 초기화"""
        self.parser = MSLParser()
        self.lexer = MSLLexer()
        
        # 예제 데이터베이스 초기화
        self._init_examples_database()
    
    def _init_examples_database(self):
        """예제 데이터베이스를 초기화합니다"""
        self.examples = {
            # 기본 키 입력 예제 (초급)
            "basic_keys": {
                "category": "기본 키 입력",
                "difficulty": "초급",
                "description": "단순한 키 입력 매크로",
                "examples": [
                    {
                        "name": "단일 키 입력",
                        "script": "a",
                        "description": "'A' 키를 한 번 누릅니다",
                        "use_case": "기본적인 키 입력, 문자 입력 테스트"
                    },
                    {
                        "name": "특수 키 입력",
                        "script": "space",
                        "description": "스페이스바를 한 번 누릅니다",
                        "use_case": "점프, 확인 버튼"
                    },
                    {
                        "name": "기능키 입력",
                        "script": "f1",
                        "description": "F1 키를 누릅니다",
                        "use_case": "도움말, 인벤토리 열기"
                    },
                    {
                        "name": "화살표 키",
                        "script": "up",
                        "description": "위쪽 화살표 키를 누릅니다",
                        "use_case": "캐릭터 이동, 메뉴 탐색"
                    }
                ]
            },
            
            # 순차 실행 예제 (초급-중급)
            "sequences": {
                "category": "순차 실행",
                "difficulty": "초급-중급",
                "description": "여러 동작을 순서대로 실행하는 매크로",
                "examples": [
                    {
                        "name": "간단한 순차 실행",
                        "script": "q,w,e",
                        "description": "Q → W → E 순서로 키를 누릅니다",
                        "use_case": "스킬 콤보, 순서가 중요한 동작"
                    },
                    {
                        "name": "이동 + 동작",
                        "script": "w,space",
                        "description": "앞으로 이동 후 점프합니다",
                        "use_case": "달리기 점프, 플랫폼 이동"
                    },
                    {
                        "name": "복잡한 스킬 콤보",
                        "script": "q,w,e,r",
                        "description": "Q → W → E → R 순서로 스킬을 시전합니다",
                        "use_case": "MOBA/RPG 게임의 스킬 콤보"
                    },
                    {
                        "name": "아이템 사용 순서",
                        "script": "1,2,3",
                        "description": "1번 → 2번 → 3번 아이템을 순서대로 사용합니다",
                        "use_case": "포션 연속 사용, 버프 중첩"
                    }
                ]
            },
            
            # 동시 실행 예제 (중급)
            "concurrent": {
                "category": "동시 실행",
                "difficulty": "중급",
                "description": "여러 동작을 동시에 실행하는 매크로",
                "examples": [
                    {
                        "name": "기본 조합키",
                        "script": "ctrl+c",
                        "description": "Ctrl과 C를 동시에 누릅니다 (복사)",
                        "use_case": "복사, 붙여넣기, 시스템 단축키"
                    },
                    {
                        "name": "이동 + 스킬",
                        "script": "w+q",
                        "description": "앞으로 이동하면서 동시에 Q 스킬을 사용합니다",
                        "use_case": "이동하면서 공격, 캐스팅 중 이동"
                    },
                    {
                        "name": "다중 스킬 시전",
                        "script": "q+e",
                        "description": "Q와 E 스킬을 동시에 시전합니다",
                        "use_case": "버프/디버프 동시 적용, 즉석 콤보"
                    },
                    {
                        "name": "3개 동시 입력",
                        "script": "shift+ctrl+alt",
                        "description": "Shift, Ctrl, Alt를 모두 동시에 누릅니다",
                        "use_case": "복잡한 단축키, 특수 기능"
                    }
                ]
            },
            
            # 타이밍 제어 예제 (중급-고급)
            "timing": {
                "category": "타이밍 제어",
                "difficulty": "중급-고급",
                "description": "정확한 타이밍으로 동작을 제어하는 매크로",
                "examples": [
                    {
                        "name": "기본 딜레이",
                        "script": "q,(500),w",
                        "description": "Q를 누르고 0.5초 후 W를 누릅니다",
                        "use_case": "스킬 쿨다운 대기, 캐스팅 시간 고려"
                    },
                    {
                        "name": "연속 스킬 with 딜레이",
                        "script": "q,(200),w,(200),e",
                        "description": "Q → 0.2초 대기 → W → 0.2초 대기 → E",
                        "use_case": "정확한 타이밍의 스킬 로테이션"
                    },
                    {
                        "name": "짧은 간격 연타",
                        "script": "space,(100),space,(100),space",
                        "description": "0.1초 간격으로 스페이스를 3번 누릅니다",
                        "use_case": "더블점프, 연속 점프"
                    },
                    {
                        "name": "긴 대기시간",
                        "script": "1,(2000),2",
                        "description": "1번 키를 누르고 2초 후 2번 키를 누릅니다",
                        "use_case": "긴 쿨다운 스킬, 채널링 스킬"
                    }
                ]
            },
            
            # 홀드 및 연속 입력 예제 (중급-고급)
            "holds": {
                "category": "홀드 및 연속",
                "difficulty": "중급-고급",
                "description": "키를 누른 상태를 유지하거나 연속으로 입력하는 매크로",
                "examples": [
                    {
                        "name": "이동 중 공격",
                        "script": "w>q",
                        "description": "W키를 누른 상태에서 Q를 실행합니다",
                        "use_case": "이동하면서 공격, 차지 스킬"
                    },
                    {
                        "name": "연속 입력",
                        "script": "q&",
                        "description": "Q키를 계속 누른 상태로 유지합니다",
                        "use_case": "오토파이어, 연속 스킬"
                    },
                    {
                        "name": "복합 홀드",
                        "script": "shift>w>space",
                        "description": "Shift를 누른 상태에서 W를 누르고, 이어서 Space를 누릅니다",
                        "use_case": "달리기 점프, 차지 공격"
                    },
                    {
                        "name": "토글 동작",
                        "script": "caps~",
                        "description": "Caps Lock 상태를 토글합니다",
                        "use_case": "상태 전환, 모드 변경"
                    }
                ]
            },
            
            # 반복 실행 예제 (중급-고급)
            "repeats": {
                "category": "반복 실행",
                "difficulty": "중급-고급",
                "description": "동작을 여러 번 반복하는 매크로",
                "examples": [
                    {
                        "name": "기본 반복",
                        "script": "q*3",
                        "description": "Q키를 3번 연속으로 누릅니다",
                        "use_case": "연타, 다중 스킬 시전"
                    },
                    {
                        "name": "반복 with 딜레이",
                        "script": "(q,(100))*5",
                        "description": "Q키를 누르고 0.1초 대기하는 동작을 5번 반복합니다",
                        "use_case": "정확한 간격의 연타, 리듬 게임"
                    },
                    {
                        "name": "복합 동작 반복",
                        "script": "(q,w)*3",
                        "description": "Q → W 동작을 3번 반복합니다",
                        "use_case": "콤보 반복, 패턴 공격"
                    },
                    {
                        "name": "많은 반복",
                        "script": "space*10",
                        "description": "스페이스바를 10번 연속으로 누릅니다",
                        "use_case": "빠른 연타, 스킵 기능"
                    }
                ]
            },
            
            # 병렬 실행 예제 (고급)
            "parallel": {
                "category": "병렬 실행",
                "difficulty": "고급",
                "description": "독립적인 동작을 동시에 실행하는 고급 매크로",
                "examples": [
                    {
                        "name": "기본 병렬",
                        "script": "q|w",
                        "description": "Q와 W를 독립적으로 동시에 실행합니다",
                        "use_case": "독립적인 다중 작업"
                    },
                    {
                        "name": "이동과 스킬 병렬",
                        "script": "w&|(q,(500),e)*3",
                        "description": "W키를 계속 누르면서 동시에 Q→E 콤보를 3번 반복합니다",
                        "use_case": "이동하면서 스킬 로테이션"
                    },
                    {
                        "name": "복잡한 병렬",
                        "script": "(q*5)|((200),w*3)",
                        "description": "Q를 5번 누르면서 동시에 0.2초 후 W를 3번 누릅니다",
                        "use_case": "복잡한 다중 스킬 조합"
                    }
                ]
            },
            
            # 게임별 특화 예제
            "fps_games": {
                "category": "FPS 게임",
                "difficulty": "중급",
                "description": "FPS 게임에 특화된 매크로",
                "examples": [
                    {
                        "name": "빠른 무기 전환",
                        "script": "1,2,1",
                        "description": "주무기 → 보조무기 → 주무기로 빠르게 전환",
                        "use_case": "빠른 재장전 효과, 무기 전환"
                    },
                    {
                        "name": "스트레이프 점프",
                        "script": "a+space,(50),d+space",
                        "description": "왼쪽 이동+점프 후 오른쪽 이동+점프",
                        "use_case": "스트레이프 점프, 고급 이동"
                    },
                    {
                        "name": "카운터 스트레이프",
                        "script": "w&,(100),s,(50),w&",
                        "description": "앞으로 이동 → 급정거 → 다시 앞으로 이동",
                        "use_case": "정확한 에이밍을 위한 스트레이프"
                    }
                ]
            },
            
            "moba_games": {
                "category": "MOBA 게임",
                "difficulty": "중급-고급",
                "description": "MOBA 게임에 특화된 매크로",
                "examples": [
                    {
                        "name": "빠른 콤보",
                        "script": "q,w,e,r",
                        "description": "모든 스킬을 순서대로 빠르게 시전",
                        "use_case": "원콤 킬, 즉시 폭딜"
                    },
                    {
                        "name": "스마트 캐스트 콤보",
                        "script": "q+click,w+click,e+click",
                        "description": "스킬과 클릭을 동시에 실행하는 스마트 캐스트",
                        "use_case": "빠른 타겟팅, 연속 스킬샷"
                    },
                    {
                        "name": "아이템 + 스킬 콤보",
                        "script": "1,q,w,2,e,r",
                        "description": "아이템 사용과 스킬을 조합한 콤보",
                        "use_case": "완벽한 타이밍의 아이템 콤보"
                    }
                ]
            },
            
            "mmo_games": {
                "category": "MMO 게임",
                "difficulty": "중급",
                "description": "MMO 게임에 특화된 매크로",
                "examples": [
                    {
                        "name": "버프 로테이션",
                        "script": "f1,(1000),f2,(1000),f3",
                        "description": "버프 스킬을 1초 간격으로 순서대로 사용",
                        "use_case": "버프 유지, 파티 지원"
                    },
                    {
                        "name": "생산 자동화",
                        "script": "(space,(2000))*10",
                        "description": "2초 간격으로 스페이스를 10번 누름 (제작 반복)",
                        "use_case": "제작 자동화, 반복 작업"
                    },
                    {
                        "name": "퀵슬롯 관리",
                        "script": "1,2,3,4,5",
                        "description": "퀵슬롯 1~5번을 순서대로 사용",
                        "use_case": "포션 연속 사용, 스킬 로테이션"
                    }
                ]
            }
        }
    
    async def get_examples(self, 
                          category: str = None, 
                          difficulty: str = None, 
                          search_term: str = None) -> Dict[str, Any]:
        """
        조건에 맞는 예제들을 검색합니다
        
        Args:
            category: 카테고리 필터 (예: "기본 키 입력", "순차 실행")
            difficulty: 난이도 필터 (예: "초급", "중급", "고급")
            search_term: 검색어 (이름, 설명, 사용 사례에서 검색)
        
        Returns:
            필터링된 예제들
        """
        try:
            filtered_examples = {}
            
            for key, example_group in self.examples.items():
                # 카테고리 필터
                if category and category not in example_group["category"]:
                    continue
                
                # 난이도 필터
                if difficulty and difficulty not in example_group["difficulty"]:
                    continue
                
                # 검색어 필터
                if search_term:
                    search_term_lower = search_term.lower()
                    found_in_group = False
                    
                    # 그룹 정보에서 검색
                    if (search_term_lower in example_group["category"].lower() or
                        search_term_lower in example_group["description"].lower()):
                        found_in_group = True
                    
                    # 개별 예제에서 검색
                    if not found_in_group:
                        for example in example_group["examples"]:
                            if (search_term_lower in example["name"].lower() or
                                search_term_lower in example["description"].lower() or
                                search_term_lower in example["use_case"].lower() or
                                search_term_lower in example["script"].lower()):
                                found_in_group = True
                                break
                    
                    if not found_in_group:
                        continue
                
                filtered_examples[key] = example_group
            
            return {
                "success": True,
                "total_categories": len(filtered_examples),
                "total_examples": sum(len(group["examples"]) for group in filtered_examples.values()),
                "filters_applied": {
                    "category": category,
                    "difficulty": difficulty,
                    "search_term": search_term
                },
                "examples": filtered_examples
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "예제 검색 중 오류가 발생했습니다."
            }
    
    async def get_example_by_name(self, name: str) -> Dict[str, Any]:
        """
        이름으로 특정 예제를 검색합니다
        
        Args:
            name: 예제 이름
        
        Returns:
            찾은 예제의 상세 정보
        """
        try:
            for group_key, group in self.examples.items():
                for example in group["examples"]:
                    if example["name"].lower() == name.lower():
                        # 예제 검증
                        validation_result = await self._validate_example(example["script"])
                        
                        return {
                            "success": True,
                            "example": example,
                            "category": group["category"],
                            "difficulty": group["difficulty"],
                            "validation": validation_result,
                            "related_examples": self._find_related_examples(group_key, example)
                        }
            
            return {
                "success": False,
                "error": f"'{name}' 이름의 예제를 찾을 수 없습니다.",
                "suggestions": self._suggest_similar_examples(name)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "예제 검색 중 오류가 발생했습니다."
            }
    
    async def get_learning_path(self, target_difficulty: str = "고급") -> Dict[str, Any]:
        """
        학습 경로를 제안합니다
        
        Args:
            target_difficulty: 목표 난이도
        
        Returns:
            단계별 학습 경로
        """
        try:
            difficulty_order = ["초급", "초급-중급", "중급", "중급-고급", "고급"]
            target_index = difficulty_order.index(target_difficulty) if target_difficulty in difficulty_order else len(difficulty_order) - 1
            
            learning_path = []
            
            for i in range(target_index + 1):
                current_difficulty = difficulty_order[i]
                step_examples = []
                
                for group_key, group in self.examples.items():
                    if current_difficulty in group["difficulty"]:
                        step_examples.append({
                            "category": group["category"],
                            "group_key": group_key,
                            "example_count": len(group["examples"]),
                            "recommended_examples": group["examples"][:2]  # 처음 2개만 추천
                        })
                
                if step_examples:
                    learning_path.append({
                        "step": i + 1,
                        "difficulty": current_difficulty,
                        "description": self._get_difficulty_description(current_difficulty),
                        "categories": step_examples
                    })
            
            return {
                "success": True,
                "target_difficulty": target_difficulty,
                "total_steps": len(learning_path),
                "learning_path": learning_path,
                "estimated_time": self._estimate_learning_time(learning_path),
                "tips": self._get_learning_tips()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "학습 경로 생성 중 오류가 발생했습니다."
            }
    
    async def get_categories(self) -> Dict[str, Any]:
        """
        사용 가능한 모든 카테고리를 반환합니다
        
        Returns:
            카테고리 목록과 정보
        """
        try:
            categories = {}
            
            for group_key, group in self.examples.items():
                category_name = group["category"]
                if category_name not in categories:
                    categories[category_name] = {
                        "difficulty": group["difficulty"],
                        "description": group["description"],
                        "example_count": 0,
                        "groups": []
                    }
                
                categories[category_name]["example_count"] += len(group["examples"])
                categories[category_name]["groups"].append(group_key)
            
            return {
                "success": True,
                "total_categories": len(categories),
                "categories": categories,
                "difficulty_levels": ["초급", "초급-중급", "중급", "중급-고급", "고급"]
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "카테고리 정보 조회 중 오류가 발생했습니다."
            }
    
    async def create_custom_example(self, 
                                   name: str, 
                                   script: str, 
                                   description: str, 
                                   use_case: str) -> Dict[str, Any]:
        """
        사용자 정의 예제를 생성하고 검증합니다
        
        Args:
            name: 예제 이름
            script: MSL 스크립트
            description: 설명
            use_case: 사용 사례
        
        Returns:
            생성된 예제 정보와 검증 결과
        """
        try:
            # 스크립트 검증
            validation_result = await self._validate_example(script)
            
            if not validation_result["is_valid"]:
                return {
                    "success": False,
                    "error": "유효하지 않은 MSL 스크립트입니다.",
                    "validation_errors": validation_result["errors"]
                }
            
            # 복잡도 분석
            complexity = self._analyze_example_complexity(script)
            
            # 비슷한 예제 찾기
            similar_examples = self._find_similar_examples(script)
            
            custom_example = {
                "name": name,
                "script": script,
                "description": description,
                "use_case": use_case,
                "created_by": "user",
                "complexity": complexity,
                "validation": validation_result
            }
            
            return {
                "success": True,
                "custom_example": custom_example,
                "similar_examples": similar_examples,
                "suggestions": self._suggest_improvements(script)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "사용자 정의 예제 생성 중 오류가 발생했습니다."
            }
    
    # 헬퍼 메서드들
    async def _validate_example(self, script: str) -> Dict[str, Any]:
        """예제 스크립트를 검증합니다"""
        try:
            tokens = self.lexer.tokenize(script)
            ast = self.parser.parse(tokens)
            
            return {
                "is_valid": True,
                "ast_nodes": self._count_ast_nodes(ast),
                "estimated_time": self._estimate_execution_time(ast)
            }
            
        except Exception as e:
            return {
                "is_valid": False,
                "errors": [str(e)]
            }
    
    def _find_related_examples(self, group_key: str, current_example: Dict[str, Any]) -> List[Dict[str, Any]]:
        """관련 예제들을 찾습니다"""
        related = []
        group = self.examples[group_key]
        
        for example in group["examples"]:
            if example["name"] != current_example["name"]:
                related.append({
                    "name": example["name"],
                    "script": example["script"],
                    "description": example["description"]
                })
        
        return related[:3]  # 최대 3개만 반환
    
    def _suggest_similar_examples(self, name: str) -> List[str]:
        """비슷한 이름의 예제들을 제안합니다"""
        suggestions = []
        name_lower = name.lower()
        
        for group in self.examples.values():
            for example in group["examples"]:
                example_name_lower = example["name"].lower()
                # 간단한 유사성 검사 (부분 문자열 포함)
                if (name_lower in example_name_lower or 
                    example_name_lower in name_lower or
                    any(word in example_name_lower for word in name_lower.split())):
                    suggestions.append(example["name"])
        
        return suggestions[:5]  # 최대 5개만 반환
    
    def _get_difficulty_description(self, difficulty: str) -> str:
        """난이도별 설명을 반환합니다"""
        descriptions = {
            "초급": "MSL의 기본 개념을 학습합니다. 단순한 키 입력과 순차 실행을 다룹니다.",
            "초급-중급": "기본 개념을 확장하여 약간 복잡한 패턴을 학습합니다.",
            "중급": "동시 실행, 타이밍 제어 등 중간 수준의 기능을 학습합니다.",
            "중급-고급": "홀드, 반복 등 고급 기능을 조합하여 사용합니다.",
            "고급": "병렬 실행 등 복잡한 고급 기능을 마스터합니다."
        }
        return descriptions.get(difficulty, "MSL 스크립팅을 학습합니다.")
    
    def _estimate_learning_time(self, learning_path: List[Dict[str, Any]]) -> str:
        """학습 시간을 추정합니다"""
        total_examples = sum(
            sum(len(self.examples[cat["group_key"]]["examples"]) for cat in step["categories"])
            for step in learning_path
        )
        
        # 예제당 평균 10분으로 가정
        estimated_minutes = total_examples * 10
        hours = estimated_minutes // 60
        minutes = estimated_minutes % 60
        
        if hours > 0:
            return f"약 {hours}시간 {minutes}분"
        else:
            return f"약 {minutes}분"
    
    def _get_learning_tips(self) -> List[str]:
        """학습 팁을 반환합니다"""
        return [
            "💡 각 예제를 직접 타이핑해보면서 연습하세요",
            "🎯 예제의 사용 사례를 이해하고 자신의 게임에 적용해보세요",
            "⚡ 간단한 예제부터 시작하여 점진적으로 복잡한 것으로 넘어가세요",
            "🔄 예제를 변형해보면서 창의적으로 활용하는 방법을 찾아보세요",
            "🧪 validate_msl 도구를 사용하여 작성한 스크립트가 올바른지 확인하세요"
        ]
    
    def _analyze_example_complexity(self, script: str) -> str:
        """예제의 복잡도를 분석합니다"""
        try:
            tokens = self.lexer.tokenize(script)
            ast = self.parser.parse(tokens)
            node_count = self._count_ast_nodes(ast)
            
            if node_count <= 3:
                return "초급"
            elif node_count <= 8:
                return "중급"
            else:
                return "고급"
                
        except:
            return "알 수 없음"
    
    def _find_similar_examples(self, script: str) -> List[Dict[str, Any]]:
        """비슷한 스크립트의 예제들을 찾습니다"""
        similar = []
        script_length = len(script)
        
        for group in self.examples.values():
            for example in group["examples"]:
                example_length = len(example["script"])
                # 길이가 비슷하거나 공통 패턴이 있는 예제 찾기
                if (abs(script_length - example_length) <= 5 or
                    any(char in example["script"] for char in ['+', '>', '|', '*', '&'] if char in script)):
                    similar.append({
                        "name": example["name"],
                        "script": example["script"],
                        "category": group["category"]
                    })
        
        return similar[:3]  # 최대 3개만 반환
    
    def _suggest_improvements(self, script: str) -> List[str]:
        """스크립트 개선 제안을 생성합니다"""
        suggestions = []
        
        # 간단한 개선 제안 로직
        if '(' in script and ')' in script:
            suggestions.append("타이밍 제어를 사용하고 있네요! optimize_msl 도구로 최적화를 확인해보세요.")
        
        if '+' in script:
            suggestions.append("동시 실행을 사용하고 있습니다. 키 조합이 정확한지 확인해보세요.")
        
        if script.count(',') > 5:
            suggestions.append("긴 순차 실행입니다. 일부를 그룹화하면 더 읽기 쉬울 수 있습니다.")
        
        if '*' in script:
            suggestions.append("반복 실행을 사용하고 있습니다. 반복 횟수가 적절한지 확인해보세요.")
        
        return suggestions
    
    def _count_ast_nodes(self, node) -> int:
        """AST 노드 개수를 계산합니다"""
        if not node:
            return 0
        
        count = 1
        if hasattr(node, 'left') and node.left:
            count += self._count_ast_nodes(node.left)
        if hasattr(node, 'right') and node.right:
            count += self._count_ast_nodes(node.right)
        if hasattr(node, 'children') and node.children:
            for child in node.children:
                count += self._count_ast_nodes(child)
        
        return count
    
    def _estimate_execution_time(self, node) -> float:
        """실행 시간을 추정합니다 (밀리초)"""
        if not node:
            return 0.0
        
        # 기본 키 입력은 50ms로 가정
        base_time = 50.0
        
        # 노드 타입에 따른 시간 계산 (간단한 추정)
        if hasattr(node, 'left') and hasattr(node, 'right'):
            left_time = self._estimate_execution_time(node.left)
            right_time = self._estimate_execution_time(node.right)
            
            # 순차 실행인 경우 시간을 더하고, 동시 실행인 경우 최대값 선택
            if 'Sequence' in type(node).__name__:
                return left_time + right_time
            else:
                return max(left_time, right_time)
        
        return base_time 