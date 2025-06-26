"""
MSL (Macro Scripting Language) AST (Abstract Syntax Tree) 정의
파서가 생성하는 구문 트리의 노드들을 정의합니다.

이 파일은 게임 매크로 스크립팅을 위한 MSL 언어의 AST 노드들을 정의합니다.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Any, Dict
from dataclasses import dataclass
from enum import Enum


class NodeType(Enum):
    """AST 노드 타입 열거형"""
    # 표현식 노드 타입들
    KEY = "KEY"                    # 키 입력 노드 (W, A, Space 등)
    NUMBER = "NUMBER"              # 숫자 노드 (시간, 횟수 등)
    VARIABLE = "VARIABLE"          # 변수 노드 ($combo1 등)
    MOUSE_COORD = "MOUSE_COORD"    # 마우스 좌표 노드 (@(100,200))
    WHEEL = "WHEEL"                # 휠 제어 노드 (wheel+/wheel-)
    
    # 연산자 노드 타입들
    SEQUENTIAL = "SEQUENTIAL"      # 순차 실행 (,)
    SIMULTANEOUS = "SIMULTANEOUS"  # 동시 실행 (+)
    HOLD_CHAIN = "HOLD_CHAIN"     # 홀드 연결 (>)
    PARALLEL = "PARALLEL"         # 병렬 실행 (|)
    TOGGLE = "TOGGLE"             # 토글 (~)
    REPEAT = "REPEAT"             # 반복 (*)
    CONTINUOUS = "CONTINUOUS"     # 연속 입력 (&)
    
    # 타이밍 노드 타입들
    DELAY = "DELAY"               # 지연 ((숫자))
    HOLD = "HOLD"                 # 홀드 ([숫자])
    INTERVAL = "INTERVAL"         # 간격 ({숫자})
    FADE = "FADE"                 # 페이드 (<숫자>)
    
    # 그룹 노드 타입
    GROUP = "GROUP"               # 그룹화


@dataclass
class Position:
    """AST 노드의 소스 코드 위치 정보를 저장하는 클래스"""
    line: int         # 줄 번호
    column: int       # 열 번호
    position: int     # 전체 위치


class MSLNode(ABC):
    """
    MSL AST 노드의 추상 기본 클래스
    모든 AST 노드는 이 클래스를 상속받아 구현됩니다.
    """
    
    def __init__(self, node_type: NodeType, position: Optional[Position] = None):
        """
        MSL 노드 초기화
        
        Args:
            node_type (NodeType): 노드 타입
            position (Position, optional): 소스 코드에서의 위치 정보
        """
        self.node_type = node_type
        self.position = position
        self.parent: Optional['MSLNode'] = None
        self.children: List['MSLNode'] = []
    
    def add_child(self, child: 'MSLNode'):
        """자식 노드를 추가하는 메서드"""
        child.parent = self
        self.children.append(child)
    
    def remove_child(self, child: 'MSLNode'):
        """자식 노드를 제거하는 메서드"""
        if child in self.children:
            child.parent = None
            self.children.remove(child)
    
    @abstractmethod
    def accept(self, visitor):
        """Visitor 패턴을 위한 추상 메서드"""
        pass
    
    def __str__(self) -> str:
        """노드의 문자열 표현을 반환"""
        return f"{self.node_type.value}"
    
    def tree_string(self, indent: int = 0) -> str:
        """트리 구조를 문자열로 표현하는 메서드"""
        result = "  " * indent + str(self) + "\n"
        for child in self.children:
            result += child.tree_string(indent + 1)
        return result


class ExpressionNode(MSLNode):
    """
    표현식 노드 (값을 가지는 노드)
    키, 숫자, 변수 등 실제 값을 가지는 노드들의 기본 클래스
    """
    
    def __init__(self, node_type: NodeType, value: Any, position: Optional[Position] = None):
        """
        표현식 노드 초기화
        
        Args:
            node_type (NodeType): 노드 타입
            value (Any): 노드가 가지는 값
            position (Position, optional): 소스 코드 위치
        """
        super().__init__(node_type, position)
        self.value = value
    
    def __str__(self) -> str:
        return f"{self.node_type.value}({self.value})"


class KeyNode(ExpressionNode):
    """키 입력 노드 (W, A, Space, Ctrl 등)"""
    
    def __init__(self, key_name: str, position: Optional[Position] = None):
        """
        키 노드 초기화
        
        Args:
            key_name (str): 키 이름 (예: "W", "Space", "Ctrl")
            position (Position, optional): 소스 코드 위치
        """
        super().__init__(NodeType.KEY, key_name, position)
        self.key_name = key_name
    
    def accept(self, visitor):
        """키 노드 방문자 처리"""
        return visitor.visit_key_node(self)


class NumberNode(ExpressionNode):
    """숫자 노드 (시간, 횟수 등)"""
    
    def __init__(self, number: float, position: Optional[Position] = None):
        """
        숫자 노드 초기화
        
        Args:
            number (float): 숫자 값
            position (Position, optional): 소스 코드 위치
        """
        super().__init__(NodeType.NUMBER, number, position)
        self.number = number
    
    def accept(self, visitor):
        """숫자 노드 방문자 처리"""
        return visitor.visit_number_node(self)


class VariableNode(ExpressionNode):
    """변수 노드 ($combo1 등)"""
    
    def __init__(self, variable_name: str, position: Optional[Position] = None):
        """
        변수 노드 초기화
        
        Args:
            variable_name (str): 변수 이름 ($ 제외)
            position (Position, optional): 소스 코드 위치
        """
        super().__init__(NodeType.VARIABLE, variable_name, position)
        self.variable_name = variable_name
    
    def accept(self, visitor):
        """변수 노드 방문자 처리"""
        return visitor.visit_variable_node(self)


class MouseCoordNode(ExpressionNode):
    """마우스 좌표 노드 (@(100,200))"""
    
    def __init__(self, x: int, y: int, position: Optional[Position] = None):
        """
        마우스 좌표 노드 초기화
        
        Args:
            x (int): X 좌표
            y (int): Y 좌표
            position (Position, optional): 소스 코드 위치
        """
        super().__init__(NodeType.MOUSE_COORD, (x, y), position)
        self.x = x
        self.y = y
    
    def accept(self, visitor):
        """마우스 좌표 노드 방문자 처리"""
        return visitor.visit_mouse_coord_node(self)
    
    def __str__(self) -> str:
        return f"{self.node_type.value}({self.x},{self.y})"


class WheelNode(ExpressionNode):
    """휠 제어 노드 (wheel+/wheel-)"""
    
    def __init__(self, direction: str, amount: int = 1, position: Optional[Position] = None):
        """
        휠 노드 초기화
        
        Args:
            direction (str): 휠 방향 ("+" 또는 "-")
            amount (int): 휠 이동량 (기본값: 1)
            position (Position, optional): 소스 코드 위치
        """
        super().__init__(NodeType.WHEEL, f"wheel{direction}{amount}", position)
        self.direction = direction
        self.amount = amount
    
    def accept(self, visitor):
        """휠 노드 방문자 처리"""
        return visitor.visit_wheel_node(self)
    
    def __str__(self) -> str:
        return f"{self.node_type.value}({self.direction}{self.amount})"


class OperatorNode(MSLNode):
    """
    연산자 노드 (여러 자식 노드를 가지는 노드)
    순차실행, 동시실행, 병렬실행 등의 연산을 나타냅니다.
    """
    
    def __init__(self, node_type: NodeType, position: Optional[Position] = None):
        """
        연산자 노드 초기화
        
        Args:
            node_type (NodeType): 연산자 노드 타입
            position (Position, optional): 소스 코드 위치
        """
        super().__init__(node_type, position)


class SequentialNode(OperatorNode):
    """순차 실행 노드 (,)"""
    
    def __init__(self, position: Optional[Position] = None):
        super().__init__(NodeType.SEQUENTIAL, position)
    
    def accept(self, visitor):
        return visitor.visit_sequential_node(self)


class SimultaneousNode(OperatorNode):
    """동시 실행 노드 (+)"""
    
    def __init__(self, position: Optional[Position] = None):
        super().__init__(NodeType.SIMULTANEOUS, position)
    
    def accept(self, visitor):
        return visitor.visit_simultaneous_node(self)


class HoldChainNode(OperatorNode):
    """홀드 연결 노드 (>)"""
    
    def __init__(self, position: Optional[Position] = None):
        super().__init__(NodeType.HOLD_CHAIN, position)
    
    def accept(self, visitor):
        return visitor.visit_hold_chain_node(self)


class ParallelNode(OperatorNode):
    """병렬 실행 노드 (|)"""
    
    def __init__(self, position: Optional[Position] = None):
        super().__init__(NodeType.PARALLEL, position)
    
    def accept(self, visitor):
        return visitor.visit_parallel_node(self)


class ToggleNode(OperatorNode):
    """토글 노드 (~)"""
    
    def __init__(self, position: Optional[Position] = None):
        super().__init__(NodeType.TOGGLE, position)
    
    def accept(self, visitor):
        return visitor.visit_toggle_node(self)


class RepeatNode(OperatorNode):
    """반복 노드 (*)"""
    
    def __init__(self, count: int, position: Optional[Position] = None):
        """
        반복 노드 초기화
        
        Args:
            count (int): 반복 횟수
            position (Position, optional): 소스 코드 위치
        """
        super().__init__(NodeType.REPEAT, position)
        self.count = count
    
    def accept(self, visitor):
        return visitor.visit_repeat_node(self)
    
    def __str__(self) -> str:
        return f"{self.node_type.value}({self.count})"


class ContinuousNode(OperatorNode):
    """연속 입력 노드 (&)"""
    
    def __init__(self, interval: int, position: Optional[Position] = None):
        """
        연속 입력 노드 초기화
        
        Args:
            interval (int): 입력 간격 (밀리초)
            position (Position, optional): 소스 코드 위치
        """
        super().__init__(NodeType.CONTINUOUS, position)
        self.interval = interval
    
    def accept(self, visitor):
        return visitor.visit_continuous_node(self)
    
    def __str__(self) -> str:
        return f"{self.node_type.value}({self.interval})"


class TimingNode(MSLNode):
    """
    타이밍 제어 노드 (시간 관련 노드)
    지연, 홀드, 간격, 페이드 등을 나타냅니다.
    """
    
    def __init__(self, node_type: NodeType, duration: int, position: Optional[Position] = None):
        """
        타이밍 노드 초기화
        
        Args:
            node_type (NodeType): 타이밍 노드 타입
            duration (int): 지속 시간 (밀리초)
            position (Position, optional): 소스 코드 위치
        """
        super().__init__(node_type, position)
        self.duration = duration
    
    def __str__(self) -> str:
        return f"{self.node_type.value}({self.duration})"


class DelayNode(TimingNode):
    """지연 노드 ((숫자))"""
    
    def __init__(self, delay_time: int, position: Optional[Position] = None):
        """
        지연 노드 초기화
        
        Args:
            delay_time (int): 지연 시간 (밀리초)
            position (Position, optional): 소스 코드 위치
        """
        super().__init__(NodeType.DELAY, delay_time, position)
        self.delay_time = delay_time
    
    def accept(self, visitor):
        return visitor.visit_delay_node(self)


class HoldNode(TimingNode):
    """홀드 노드 ([숫자])"""
    
    def __init__(self, hold_time: int, position: Optional[Position] = None):
        """
        홀드 노드 초기화
        
        Args:
            hold_time (int): 홀드 시간 (밀리초)
            position (Position, optional): 소스 코드 위치
        """
        super().__init__(NodeType.HOLD, hold_time, position)
        self.hold_time = hold_time
    
    def accept(self, visitor):
        return visitor.visit_hold_node(self)


class IntervalNode(TimingNode):
    """간격 노드 ({숫자})"""
    
    def __init__(self, interval_time: int, position: Optional[Position] = None):
        """
        간격 노드 초기화
        
        Args:
            interval_time (int): 간격 시간 (밀리초)
            position (Position, optional): 소스 코드 위치
        """
        super().__init__(NodeType.INTERVAL, interval_time, position)
        self.interval_time = interval_time
    
    def accept(self, visitor):
        return visitor.visit_interval_node(self)


class FadeNode(TimingNode):
    """페이드 노드 (<숫자>)"""
    
    def __init__(self, fade_time: int, position: Optional[Position] = None):
        """
        페이드 노드 초기화
        
        Args:
            fade_time (int): 페이드 시간 (밀리초)
            position (Position, optional): 소스 코드 위치
        """
        super().__init__(NodeType.FADE, fade_time, position)
        self.fade_time = fade_time
    
    def accept(self, visitor):
        return visitor.visit_fade_node(self)


class GroupNode(MSLNode):
    """그룹화 노드 (괄호로 묶인 표현식)"""
    
    def __init__(self, position: Optional[Position] = None):
        """
        그룹 노드 초기화
        
        Args:
            position (Position, optional): 소스 코드 위치
        """
        super().__init__(NodeType.GROUP, position)
    
    def accept(self, visitor):
        return visitor.visit_group_node(self)


class MSLVisitor(ABC):
    """
    MSL AST 방문자 추상 클래스
    Visitor 패턴을 구현하여 AST 노드들을 처리합니다.
    """
    
    @abstractmethod
    def visit_key_node(self, node: KeyNode):
        """키 노드 방문 처리"""
        pass
    
    @abstractmethod
    def visit_number_node(self, node: NumberNode):
        """숫자 노드 방문 처리"""
        pass
    
    @abstractmethod
    def visit_variable_node(self, node: VariableNode):
        """변수 노드 방문 처리"""
        pass
    
    @abstractmethod
    def visit_mouse_coord_node(self, node: MouseCoordNode):
        """마우스 좌표 노드 방문 처리"""
        pass
    
    @abstractmethod
    def visit_wheel_node(self, node: WheelNode):
        """휠 노드 방문 처리"""
        pass
    
    @abstractmethod
    def visit_sequential_node(self, node: SequentialNode):
        """순차 실행 노드 방문 처리"""
        pass
    
    @abstractmethod
    def visit_simultaneous_node(self, node: SimultaneousNode):
        """동시 실행 노드 방문 처리"""
        pass
    
    @abstractmethod
    def visit_hold_chain_node(self, node: HoldChainNode):
        """홀드 연결 노드 방문 처리"""
        pass
    
    @abstractmethod
    def visit_parallel_node(self, node: ParallelNode):
        """병렬 실행 노드 방문 처리"""
        pass
    
    @abstractmethod
    def visit_toggle_node(self, node: ToggleNode):
        """토글 노드 방문 처리"""
        pass
    
    @abstractmethod
    def visit_repeat_node(self, node: RepeatNode):
        """반복 노드 방문 처리"""
        pass
    
    @abstractmethod
    def visit_continuous_node(self, node: ContinuousNode):
        """연속 입력 노드 방문 처리"""
        pass
    
    @abstractmethod
    def visit_delay_node(self, node: DelayNode):
        """지연 노드 방문 처리"""
        pass
    
    @abstractmethod
    def visit_hold_node(self, node: HoldNode):
        """홀드 노드 방문 처리"""
        pass
    
    @abstractmethod
    def visit_interval_node(self, node: IntervalNode):
        """간격 노드 방문 처리"""
        pass
    
    @abstractmethod
    def visit_fade_node(self, node: FadeNode):
        """페이드 노드 방문 처리"""
        pass
    
    @abstractmethod
    def visit_group_node(self, node: GroupNode):
        """그룹 노드 방문 처리"""
        pass


class ASTPrinter(MSLVisitor):
    """
    AST를 문자열로 출력하는 방문자 클래스
    디버깅과 시각화를 위해 사용됩니다.
    """
    
    def __init__(self):
        """AST 프린터 초기화"""
        self.indent_level = 0
        self.output = []
    
    def _print_with_indent(self, text: str):
        """들여쓰기를 적용하여 텍스트 출력"""
        self.output.append("  " * self.indent_level + text)
    
    def _visit_children(self, node: MSLNode):
        """자식 노드들을 방문하는 공통 메서드"""
        self.indent_level += 1
        for child in node.children:
            child.accept(self)
        self.indent_level -= 1
    
    def visit_key_node(self, node: KeyNode):
        self._print_with_indent(f"Key: {node.key_name}")
    
    def visit_number_node(self, node: NumberNode):
        self._print_with_indent(f"Number: {node.number}")
    
    def visit_variable_node(self, node: VariableNode):
        self._print_with_indent(f"Variable: {node.variable_name}")
    
    def visit_mouse_coord_node(self, node: MouseCoordNode):
        self._print_with_indent(f"MouseCoord: ({node.x}, {node.y})")
    
    def visit_wheel_node(self, node: WheelNode):
        self._print_with_indent(f"Wheel: {node.direction}{node.amount}")
    
    def visit_sequential_node(self, node: SequentialNode):
        self._print_with_indent("Sequential:")
        self._visit_children(node)
    
    def visit_simultaneous_node(self, node: SimultaneousNode):
        self._print_with_indent("Simultaneous:")
        self._visit_children(node)
    
    def visit_hold_chain_node(self, node: HoldChainNode):
        self._print_with_indent("HoldChain:")
        self._visit_children(node)
    
    def visit_parallel_node(self, node: ParallelNode):
        self._print_with_indent("Parallel:")
        self._visit_children(node)
    
    def visit_toggle_node(self, node: ToggleNode):
        self._print_with_indent("Toggle:")
        self._visit_children(node)
    
    def visit_repeat_node(self, node: RepeatNode):
        self._print_with_indent(f"Repeat({node.count}):")
        self._visit_children(node)
    
    def visit_continuous_node(self, node: ContinuousNode):
        self._print_with_indent(f"Continuous({node.interval}):")
        self._visit_children(node)
    
    def visit_delay_node(self, node: DelayNode):
        self._print_with_indent(f"Delay: {node.delay_time}ms")
    
    def visit_hold_node(self, node: HoldNode):
        self._print_with_indent(f"Hold: {node.hold_time}ms")
    
    def visit_interval_node(self, node: IntervalNode):
        self._print_with_indent(f"Interval: {node.interval_time}ms")
    
    def visit_fade_node(self, node: FadeNode):
        self._print_with_indent(f"Fade: {node.fade_time}ms")
    
    def visit_group_node(self, node: GroupNode):
        self._print_with_indent("Group:")
        self._visit_children(node)
    
    def get_output(self) -> str:
        """출력 결과를 문자열로 반환"""
        return "\n".join(self.output) 