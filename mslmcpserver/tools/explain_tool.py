"""
MSL 스크립트 설명 및 교육 도구
MSL 구문을 분석하고 초보자가 이해하기 쉽게 설명해주는 도구
"""

import asyncio
from typing import Dict, Any, List, Optional
from ..msl.msl_parser import MSLParser
from ..msl.msl_lexer import MSLLexer
from ..msl.msl_ast import *

class ExplainTool:
    """
    MSL 스크립트 설명 도구
    
    주요 기능:
    - MSL 스크립트의 각 구문 분석 및 설명
    - 초보자 친화적인 교육 자료 제공
    - 단계별 실행 흐름 설명
    - 키 입력 시퀀스 시각화
    """
    
    def __init__(self):
        """도구 초기화 - 파서와 어휘분석기 준비"""
        self.parser = MSLParser()
        self.lexer = MSLLexer()
        
        # MSL 연산자별 설명 사전
        self.operator_descriptions = {
            ',': "순차 실행: 왼쪽 동작 완료 후 오른쪽 동작 실행",
            '+': "동시 실행: 여러 동작을 같은 시간에 실행",
            '>': "홀드: 키를 누른 상태로 유지하면서 다음 동작 실행",
            '|': "병렬 실행: 독립적인 두 동작을 동시에 실행",
            '~': "토글: 키 상태를 반전 (눌려있으면 떼고, 떼져있으면 누름)",
            '*': "반복: 지정된 횟수만큼 동작 반복",
            '&': "연속: 키를 계속 누른 상태로 유지"
        }
        
        # 특수 키 설명 사전
        self.special_keys = {
            'space': '스페이스바',
            'enter': '엔터키',
            'escape': 'ESC키',
            'tab': '탭키',
            'shift': '시프트키',
            'ctrl': '컨트롤키',
            'alt': '알트키',
            'win': '윈도우키',
            'f1': 'F1 기능키',
            'f2': 'F2 기능키',
            'f3': 'F3 기능키',
            'f4': 'F4 기능키',
            'f5': 'F5 기능키',
            'f6': 'F6 기능키',
            'f7': 'F7 기능키',
            'f8': 'F8 기능키',
            'f9': 'F9 기능키',
            'f10': 'F10 기능키',
            'f11': 'F11 기능키',
            'f12': 'F12 기능키',
            'up': '위쪽 화살표키',
            'down': '아래쪽 화살표키',
            'left': '왼쪽 화살표키',
            'right': '오른쪽 화살표키',
            'home': 'Home키',
            'end': 'End키',
            'pageup': 'Page Up키',
            'pagedown': 'Page Down키',
            'insert': 'Insert키',
            'delete': 'Delete키',
            'backspace': 'Backspace키'
        }
    
    async def explain_script(self, script: str, detail_level: str = "standard") -> Dict[str, Any]:
        """
        MSL 스크립트를 분석하고 설명을 생성합니다
        
        Args:
            script: 분석할 MSL 스크립트
            detail_level: 설명 상세도 ("basic", "standard", "detailed")
        
        Returns:
            분석 결과와 설명이 담긴 딕셔너리
        """
        try:
            # 1단계: 토큰 분석
            tokens = self.lexer.tokenize(script)
            
            # 2단계: 구문 분석 및 AST 생성
            ast = self.parser.parse(tokens)
            
            # 3단계: 설명 생성
            explanation = self._generate_explanation(ast, script, detail_level)
            
            return {
                "success": True,
                "script": script,
                "detail_level": detail_level,
                "explanation": explanation,
                "execution_flow": self._generate_execution_flow(ast),
                "key_sequence": self._generate_key_sequence(ast),
                "timing_info": self._analyze_timing(ast),
                "educational_tips": self._generate_tips(ast)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "script": script,
                "suggestion": "스크립트 구문을 확인해주세요. MSL 문법에 맞지 않는 부분이 있을 수 있습니다."
            }
    
    def _generate_explanation(self, ast: ASTNode, script: str, detail_level: str) -> Dict[str, Any]:
        """
        AST를 기반으로 상세한 설명을 생성합니다
        
        Args:
            ast: 파싱된 AST
            script: 원본 스크립트
            detail_level: 설명 상세도
        
        Returns:
            설명 딕셔너리
        """
        explanation = {
            "overview": self._get_script_overview(ast),
            "structure_analysis": self._analyze_structure(ast),
            "component_breakdown": self._break_down_components(ast, detail_level),
            "complexity_level": self._assess_complexity(ast)
        }
        
        if detail_level in ["standard", "detailed"]:
            explanation["operator_usage"] = self._analyze_operators(ast)
            explanation["timing_analysis"] = self._analyze_timing_detailed(ast)
        
        if detail_level == "detailed":
            explanation["optimization_suggestions"] = self._suggest_optimizations(ast)
            explanation["alternative_approaches"] = self._suggest_alternatives(ast)
        
        return explanation
    
    def _get_script_overview(self, ast: ASTNode) -> str:
        """스크립트의 전반적인 개요를 생성합니다"""
        node_count = self._count_nodes(ast)
        operators = self._find_operators(ast)
        
        overview = f"이 MSL 스크립트는 총 {node_count}개의 동작으로 구성되어 있습니다."
        
        if operators:
            operator_names = [self.operator_descriptions.get(op, op) for op in operators]
            overview += f" 사용된 연산자: {', '.join(set(operator_names))}"
        
        return overview
    
    def _analyze_structure(self, ast: ASTNode) -> Dict[str, Any]:
        """스크립트의 구조를 분석합니다"""
        structure = {
            "type": type(ast).__name__,
            "description": self._get_node_description(ast),
            "children": []
        }
        
        # 자식 노드들 재귀적으로 분석
        if hasattr(ast, 'left') and ast.left:
            structure["children"].append(self._analyze_structure(ast.left))
        if hasattr(ast, 'right') and ast.right:
            structure["children"].append(self._analyze_structure(ast.right))
        if hasattr(ast, 'children') and ast.children:
            for child in ast.children:
                structure["children"].append(self._analyze_structure(child))
        
        return structure
    
    def _break_down_components(self, ast: ASTNode, detail_level: str) -> List[Dict[str, Any]]:
        """스크립트의 각 구성요소를 분해하여 설명합니다"""
        components = []
        self._collect_components(ast, components, detail_level)
        return components
    
    def _collect_components(self, node: ASTNode, components: List[Dict[str, Any]], detail_level: str, level: int = 0):
        """재귀적으로 컴포넌트를 수집합니다"""
        component = {
            "level": level,
            "type": type(node).__name__,
            "description": self._get_node_description(node),
            "explanation": self._get_detailed_explanation(node, detail_level)
        }
        
        # 특수 속성들 추가
        if isinstance(node, KeyNode):
            component["key_info"] = {
                "key": node.key,
                "korean_name": self.special_keys.get(node.key.lower(), f"'{node.key}' 키"),
                "category": self._categorize_key(node.key)
            }
        elif isinstance(node, DelayNode):
            component["timing_info"] = {
                "delay_ms": node.delay,
                "description": f"{node.delay}밀리초 대기"
            }
        elif isinstance(node, RepeatNode):
            component["repeat_info"] = {
                "count": node.count,
                "description": f"{node.count}번 반복 실행"
            }
        
        components.append(component)
        
        # 자식 노드들 처리
        if hasattr(node, 'left') and node.left:
            self._collect_components(node.left, components, detail_level, level + 1)
        if hasattr(node, 'right') and node.right:
            self._collect_components(node.right, components, detail_level, level + 1)
        if hasattr(node, 'children') and node.children:
            for child in node.children:
                self._collect_components(child, components, detail_level, level + 1)
    
    def _get_node_description(self, node: ASTNode) -> str:
        """노드 타입별 설명을 생성합니다"""
        if isinstance(node, KeyNode):
            key_name = self.special_keys.get(node.key.lower(), f"'{node.key}' 키")
            return f"{key_name} 입력"
        elif isinstance(node, SequenceNode):
            return "순차 실행 (왼쪽 동작 완료 후 오른쪽 동작)"
        elif isinstance(node, ConcurrentNode):
            return "동시 실행 (여러 동작을 같은 시간에)"
        elif isinstance(node, HoldNode):
            return "홀드 실행 (키를 누른 상태로 유지)"
        elif isinstance(node, ParallelNode):
            return "병렬 실행 (독립적인 동작들을 동시에)"
        elif isinstance(node, ToggleNode):
            return "토글 실행 (키 상태 반전)"
        elif isinstance(node, RepeatNode):
            return f"반복 실행 ({node.count}번)"
        elif isinstance(node, ContinuousNode):
            return "연속 실행 (키를 계속 누른 상태)"
        elif isinstance(node, DelayNode):
            return f"대기 ({node.delay}ms)"
        elif isinstance(node, GroupNode):
            return "그룹 실행 (묶음 동작)"
        else:
            return f"{type(node).__name__} 동작"
    
    def _get_detailed_explanation(self, node: ASTNode, detail_level: str) -> str:
        """노드의 상세한 설명을 생성합니다"""
        if detail_level == "basic":
            return self._get_node_description(node)
        
        explanations = {
            KeyNode: "키보드의 특정 키를 한 번 누르고 떼는 동작입니다.",
            SequenceNode: "왼쪽 동작이 완전히 끝난 후에 오른쪽 동작을 시작합니다. 순서가 중요한 매크로에 사용됩니다.",
            ConcurrentNode: "여러 동작을 정확히 같은 시간에 시작합니다. 키 조합(Ctrl+C 등)에 주로 사용됩니다.",
            HoldNode: "키를 누른 상태를 유지하면서 다른 동작을 실행합니다. 이동키를 누른 상태에서 스킬을 사용할 때 유용합니다.",
            ParallelNode: "두 동작을 독립적으로 동시에 실행합니다. 하나가 끝나도 다른 것은 계속 실행됩니다.",
            ToggleNode: "키의 현재 상태를 반전시킵니다. 눌려있으면 떼고, 떼져있으면 누릅니다.",
            RepeatNode: "지정된 횟수만큼 동작을 반복합니다. 연사나 반복 동작에 사용됩니다.",
            ContinuousNode: "키를 계속 누른 상태로 유지합니다. 이동이나 연속 동작에 사용됩니다.",
            DelayNode: "지정된 시간만큼 대기합니다. 동작 사이의 타이밍을 조절할 때 사용됩니다.",
            GroupNode: "여러 동작을 하나의 그룹으로 묶어서 처리합니다."
        }
        
        base_explanation = explanations.get(type(node), "특수한 동작을 수행합니다.")
        
        if detail_level == "detailed":
            # 추가 세부 정보 제공
            if isinstance(node, KeyNode):
                base_explanation += f" 게임에서 '{node.key}' 키의 기능을 실행합니다."
            elif isinstance(node, DelayNode):
                base_explanation += f" {node.delay}밀리초는 약 {node.delay/1000:.2f}초입니다."
            elif isinstance(node, RepeatNode):
                base_explanation += f" 총 실행 시간은 반복 내용에 따라 달라집니다."
        
        return base_explanation
    
    def _generate_execution_flow(self, ast: ASTNode) -> List[Dict[str, Any]]:
        """실행 흐름을 단계별로 생성합니다"""
        flow = []
        self._collect_execution_steps(ast, flow, 0)
        return flow
    
    def _collect_execution_steps(self, node: ASTNode, flow: List[Dict[str, Any]], step: int, timing: float = 0.0):
        """실행 단계를 재귀적으로 수집합니다"""
        if isinstance(node, SequenceNode):
            # 순차 실행: 왼쪽 먼저, 그 다음 오른쪽
            step = self._collect_execution_steps(node.left, flow, step, timing)
            step = self._collect_execution_steps(node.right, flow, step, timing)
        elif isinstance(node, ConcurrentNode):
            # 동시 실행: 같은 타이밍에 모든 동작
            self._collect_execution_steps(node.left, flow, step, timing)
            self._collect_execution_steps(node.right, flow, step, timing)
            step += 1
        elif isinstance(node, DelayNode):
            # 대기 시간 추가
            flow.append({
                "step": step,
                "timing": timing,
                "action": "대기",
                "description": f"{node.delay}ms 대기",
                "type": "delay"
            })
            timing += node.delay
            step += 1
        else:
            # 기본 동작
            flow.append({
                "step": step,
                "timing": timing,
                "action": self._get_node_description(node),
                "description": self._get_detailed_explanation(node, "standard"),
                "type": "action"
            })
            step += 1
        
        return step
    
    def _generate_key_sequence(self, ast: ASTNode) -> List[str]:
        """키 입력 시퀀스를 생성합니다"""
        sequence = []
        self._collect_key_sequence(ast, sequence)
        return sequence
    
    def _collect_key_sequence(self, node: ASTNode, sequence: List[str]):
        """키 시퀀스를 재귀적으로 수집합니다"""
        if isinstance(node, KeyNode):
            key_name = self.special_keys.get(node.key.lower(), node.key)
            sequence.append(key_name)
        elif hasattr(node, 'left') and node.left:
            self._collect_key_sequence(node.left, sequence)
        elif hasattr(node, 'right') and node.right:
            self._collect_key_sequence(node.right, sequence)
        elif hasattr(node, 'children') and node.children:
            for child in node.children:
                self._collect_key_sequence(child, sequence)
    
    def _analyze_timing(self, ast: ASTNode) -> Dict[str, Any]:
        """타이밍 정보를 분석합니다"""
        timing_info = {
            "total_estimated_time": self._calculate_total_time(ast),
            "delay_points": self._find_delays(ast),
            "concurrent_actions": self._find_concurrent_actions(ast),
            "timing_critical": self._assess_timing_criticality(ast)
        }
        return timing_info
    
    def _generate_tips(self, ast: ASTNode) -> List[str]:
        """교육적 팁을 생성합니다"""
        tips = []
        
        # 복잡도에 따른 팁
        complexity = self._assess_complexity(ast)
        if complexity == "초급":
            tips.append("💡 기본적인 키 입력 매크로입니다. 게임에서 간단한 동작 자동화에 적합합니다.")
        elif complexity == "중급":
            tips.append("💡 여러 동작이 조합된 매크로입니다. 타이밍이 중요한 콤보나 스킬 연계에 사용됩니다.")
        else:
            tips.append("💡 복잡한 매크로입니다. 게임의 복잡한 전략이나 연속 동작에 활용됩니다.")
        
        # 구조별 팁
        if self._has_delays(ast):
            tips.append("⏱️ 대기 시간이 포함되어 있어 정확한 타이밍 제어가 가능합니다.")
        
        if self._has_concurrent_actions(ast):
            tips.append("🔄 동시 실행 동작이 있어 여러 키를 함께 누르는 조합이 가능합니다.")
        
        if self._has_repeats(ast):
            tips.append("🔁 반복 동작이 있어 연사나 지속적인 동작이 가능합니다.")
        
        # 최적화 팁
        optimization_suggestions = self._suggest_optimizations(ast)
        if optimization_suggestions:
            tips.append("⚡ 성능 최적화 여지가 있습니다. optimize_msl 도구를 사용해보세요.")
        
        return tips
    
    # 헬퍼 메서드들
    def _count_nodes(self, node: ASTNode) -> int:
        """AST 노드 개수를 계산합니다"""
        count = 1
        if hasattr(node, 'left') and node.left:
            count += self._count_nodes(node.left)
        if hasattr(node, 'right') and node.right:
            count += self._count_nodes(node.right)
        if hasattr(node, 'children') and node.children:
            for child in node.children:
                count += self._count_nodes(child)
        return count
    
    def _find_operators(self, node: ASTNode) -> List[str]:
        """사용된 연산자들을 찾습니다"""
        operators = []
        
        if isinstance(node, SequenceNode):
            operators.append(',')
        elif isinstance(node, ConcurrentNode):
            operators.append('+')
        elif isinstance(node, HoldNode):
            operators.append('>')
        elif isinstance(node, ParallelNode):
            operators.append('|')
        elif isinstance(node, ToggleNode):
            operators.append('~')
        elif isinstance(node, RepeatNode):
            operators.append('*')
        elif isinstance(node, ContinuousNode):
            operators.append('&')
        
        # 자식 노드들에서 재귀적으로 찾기
        if hasattr(node, 'left') and node.left:
            operators.extend(self._find_operators(node.left))
        if hasattr(node, 'right') and node.right:
            operators.extend(self._find_operators(node.right))
        if hasattr(node, 'children') and node.children:
            for child in node.children:
                operators.extend(self._find_operators(child))
        
        return operators
    
    def _categorize_key(self, key: str) -> str:
        """키를 카테고리별로 분류합니다"""
        if key.lower() in ['ctrl', 'shift', 'alt', 'win']:
            return "수식키"
        elif key.lower() in ['f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'f10', 'f11', 'f12']:
            return "기능키"
        elif key.lower() in ['up', 'down', 'left', 'right']:
            return "화살표키"
        elif key.lower() in ['space', 'enter', 'escape', 'tab', 'backspace', 'delete']:
            return "특수키"
        elif key.isalpha():
            return "문자키"
        elif key.isdigit():
            return "숫자키"
        else:
            return "기타키"
    
    def _assess_complexity(self, ast: ASTNode) -> str:
        """스크립트의 복잡도를 평가합니다"""
        node_count = self._count_nodes(ast)
        operators = set(self._find_operators(ast))
        
        if node_count <= 3 and len(operators) <= 1:
            return "초급"
        elif node_count <= 10 and len(operators) <= 3:
            return "중급"
        else:
            return "고급"
    
    def _analyze_operators(self, ast: ASTNode) -> Dict[str, Any]:
        """연산자 사용 패턴을 분석합니다"""
        operators = self._find_operators(ast)
        operator_count = {}
        
        for op in operators:
            operator_count[op] = operator_count.get(op, 0) + 1
        
        return {
            "used_operators": list(set(operators)),
            "operator_frequency": operator_count,
            "operator_descriptions": {op: self.operator_descriptions.get(op, op) for op in set(operators)}
        }
    
    def _analyze_timing_detailed(self, ast: ASTNode) -> Dict[str, Any]:
        """상세한 타이밍 분석을 수행합니다"""
        return {
            "has_delays": self._has_delays(ast),
            "has_concurrent": self._has_concurrent_actions(ast),
            "has_holds": self._has_holds(ast),
            "estimated_duration": self._calculate_total_time(ast),
            "timing_complexity": self._assess_timing_complexity(ast)
        }
    
    def _suggest_optimizations(self, ast: ASTNode) -> List[str]:
        """최적화 제안을 생성합니다"""
        suggestions = []
        
        # 불필요한 대기 시간 검사
        if self._has_excessive_delays(ast):
            suggestions.append("일부 대기 시간이 너무 길 수 있습니다. 최적화를 고려해보세요.")
        
        # 중복 동작 검사
        if self._has_redundant_actions(ast):
            suggestions.append("중복된 동작이 있습니다. 구조를 단순화할 수 있습니다.")
        
        return suggestions
    
    def _suggest_alternatives(self, ast: ASTNode) -> List[str]:
        """대안적 접근법을 제안합니다"""
        alternatives = []
        
        # 복잡한 시퀀스에 대한 대안 제안
        if self._is_complex_sequence(ast):
            alternatives.append("복잡한 순차 실행을 더 간단한 동시 실행으로 변경할 수 있는지 검토해보세요.")
        
        return alternatives
    
    # 유틸리티 메서드들
    def _calculate_total_time(self, node: ASTNode) -> float:
        """총 예상 실행 시간을 계산합니다 (밀리초)"""
        if isinstance(node, DelayNode):
            return float(node.delay)
        elif isinstance(node, SequenceNode):
            # 순차 실행은 시간을 더함
            left_time = self._calculate_total_time(node.left) if node.left else 0
            right_time = self._calculate_total_time(node.right) if node.right else 0
            return left_time + right_time
        elif isinstance(node, ConcurrentNode):
            # 동시 실행은 더 긴 시간을 선택
            left_time = self._calculate_total_time(node.left) if node.left else 0
            right_time = self._calculate_total_time(node.right) if node.right else 0
            return max(left_time, right_time)
        elif isinstance(node, RepeatNode):
            # 반복은 내용 시간 × 반복 횟수
            child_time = 0
            if hasattr(node, 'children') and node.children:
                child_time = sum(self._calculate_total_time(child) for child in node.children)
            return child_time * node.count
        else:
            # 기본 키 입력은 50ms로 가정
            return 50.0
    
    def _find_delays(self, node: ASTNode) -> List[Dict[str, Any]]:
        """딜레이 노드들을 찾습니다"""
        delays = []
        
        if isinstance(node, DelayNode):
            delays.append({
                "delay": node.delay,
                "description": f"{node.delay}ms 대기"
            })
        
        # 자식 노드들에서 재귀적으로 찾기
        if hasattr(node, 'left') and node.left:
            delays.extend(self._find_delays(node.left))
        if hasattr(node, 'right') and node.right:
            delays.extend(self._find_delays(node.right))
        if hasattr(node, 'children') and node.children:
            for child in node.children:
                delays.extend(self._find_delays(child))
        
        return delays
    
    def _find_concurrent_actions(self, node: ASTNode) -> List[str]:
        """동시 실행 동작들을 찾습니다"""
        concurrent = []
        
        if isinstance(node, ConcurrentNode):
            concurrent.append("동시 실행 발견")
        
        # 자식 노드들에서 재귀적으로 찾기
        if hasattr(node, 'left') and node.left:
            concurrent.extend(self._find_concurrent_actions(node.left))
        if hasattr(node, 'right') and node.right:
            concurrent.extend(self._find_concurrent_actions(node.right))
        
        return concurrent
    
    def _assess_timing_criticality(self, node: ASTNode) -> str:
        """타이밍 중요도를 평가합니다"""
        has_delays = self._has_delays(node)
        has_concurrent = self._has_concurrent_actions(node)
        has_holds = self._has_holds(node)
        
        if has_delays and has_concurrent and has_holds:
            return "매우 높음"
        elif (has_delays and has_concurrent) or (has_delays and has_holds):
            return "높음"
        elif has_delays or has_concurrent or has_holds:
            return "보통"
        else:
            return "낮음"
    
    def _has_delays(self, node: ASTNode) -> bool:
        """딜레이가 있는지 확인합니다"""
        if isinstance(node, DelayNode):
            return True
        
        if hasattr(node, 'left') and node.left and self._has_delays(node.left):
            return True
        if hasattr(node, 'right') and node.right and self._has_delays(node.right):
            return True
        if hasattr(node, 'children') and node.children:
            for child in node.children:
                if self._has_delays(child):
                    return True
        
        return False
    
    def _has_concurrent_actions(self, node: ASTNode) -> bool:
        """동시 실행이 있는지 확인합니다"""
        if isinstance(node, ConcurrentNode):
            return True
        
        if hasattr(node, 'left') and node.left and self._has_concurrent_actions(node.left):
            return True
        if hasattr(node, 'right') and node.right and self._has_concurrent_actions(node.right):
            return True
        
        return False
    
    def _has_repeats(self, node: ASTNode) -> bool:
        """반복이 있는지 확인합니다"""
        if isinstance(node, RepeatNode):
            return True
        
        if hasattr(node, 'left') and node.left and self._has_repeats(node.left):
            return True
        if hasattr(node, 'right') and node.right and self._has_repeats(node.right):
            return True
        
        return False
    
    def _has_holds(self, node: ASTNode) -> bool:
        """홀드가 있는지 확인합니다"""
        if isinstance(node, HoldNode):
            return True
        
        if hasattr(node, 'left') and node.left and self._has_holds(node.left):
            return True
        if hasattr(node, 'right') and node.right and self._has_holds(node.right):
            return True
        
        return False
    
    def _has_excessive_delays(self, node: ASTNode) -> bool:
        """과도한 딜레이가 있는지 확인합니다 (1초 이상)"""
        if isinstance(node, DelayNode) and node.delay > 1000:
            return True
        
        if hasattr(node, 'left') and node.left and self._has_excessive_delays(node.left):
            return True
        if hasattr(node, 'right') and node.right and self._has_excessive_delays(node.right):
            return True
        
        return False
    
    def _has_redundant_actions(self, node: ASTNode) -> bool:
        """중복 동작이 있는지 확인합니다 (간단한 휴리스틱)"""
        # 동일한 키가 연속으로 나오는지 확인
        keys = []
        self._collect_key_sequence(node, keys)
        
        for i in range(len(keys) - 1):
            if keys[i] == keys[i + 1]:
                return True
        
        return False
    
    def _is_complex_sequence(self, node: ASTNode) -> bool:
        """복잡한 시퀀스인지 확인합니다"""
        return self._count_nodes(node) > 10
    
    def _assess_timing_complexity(self, node: ASTNode) -> str:
        """타이밍 복잡도를 평가합니다"""
        delay_count = len(self._find_delays(node))
        concurrent_count = len(self._find_concurrent_actions(node))
        
        total_complexity = delay_count + concurrent_count
        
        if total_complexity == 0:
            return "단순"
        elif total_complexity <= 2:
            return "보통"
        elif total_complexity <= 5:
            return "복잡"
        else:
            return "매우 복잡" 