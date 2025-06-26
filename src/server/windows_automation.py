from typing import Dict, List, Optional, Any, Tuple
import pyautogui
import keyboard
import win32gui
import win32con
import win32api
import logging
from pydantic import BaseModel
import time
import re

class WindowsAction(BaseModel):
    """Windows 자동화 동작 모델"""
    action_type: str  # click, type, hotkey, window, wait
    parameters: Dict[str, Any] = {}
    description: Optional[str] = None

class WindowsAutomationResult(BaseModel):
    """Windows 자동화 실행 결과 모델"""
    success: bool
    action: WindowsAction
    result: Optional[Any] = None
    error: Optional[str] = None

class WindowsAutomation:
    """Windows 자동화 구현"""
    def __init__(self):
        self.logger = logging.getLogger("WindowsAutomation")
        pyautogui.FAILSAFE = True
        
    async def execute_actions(self, actions: List[WindowsAction]) -> List[WindowsAutomationResult]:
        """여러 동작 실행"""
        results = []
        for action in actions:
            result = await self.execute_action(action)
            results.append(result)
            if not result.success:
                break
        return results
        
    async def execute_action(self, action: WindowsAction) -> WindowsAutomationResult:
        """단일 동작 실행"""
        try:
            if action.action_type == "click":
                result = await self._handle_click(action)
            elif action.action_type == "type":
                result = await self._handle_type(action)
            elif action.action_type == "hotkey":
                result = await self._handle_hotkey(action)
            elif action.action_type == "window":
                result = await self._handle_window(action)
            elif action.action_type == "wait":
                result = await self._handle_wait(action)
            else:
                raise ValueError(f"Unknown action type: {action.action_type}")
                
            return WindowsAutomationResult(
                success=True,
                action=action,
                result=result
            )
            
        except Exception as e:
            self.logger.error(f"Error executing action {action.action_type}: {str(e)}")
            return WindowsAutomationResult(
                success=False,
                action=action,
                error=str(e)
            )
            
    async def _handle_click(self, action: WindowsAction) -> Dict[str, Any]:
        """클릭 동작 처리"""
        x = action.parameters.get("x")
        y = action.parameters.get("y")
        button = action.parameters.get("button", "left")
        clicks = action.parameters.get("clicks", 1)
        
        if x is not None and y is not None:
            pyautogui.click(x=x, y=y, button=button, clicks=clicks)
        else:
            image = action.parameters.get("image")
            if image:
                location = pyautogui.locateOnScreen(image, confidence=0.9)
                if location:
                    pyautogui.click(location, button=button, clicks=clicks)
                else:
                    raise Exception(f"Image {image} not found on screen")
                    
        return {"clicked": True}
        
    async def _handle_type(self, action: WindowsAction) -> Dict[str, Any]:
        """타이핑 동작 처리"""
        text = action.parameters.get("text")
        interval = action.parameters.get("interval", 0.1)
        
        if not text:
            raise ValueError("Text parameter is required for type action")
            
        pyautogui.write(text, interval=interval)
        return {"typed": text}
        
    async def _handle_hotkey(self, action: WindowsAction) -> Dict[str, Any]:
        """단축키 동작 처리"""
        keys = action.parameters.get("keys", [])
        if not keys:
            raise ValueError("Keys parameter is required for hotkey action")
            
        pyautogui.hotkey(*keys)
        return {"hotkey": "+".join(keys)}
        
    async def _handle_window(self, action: WindowsAction) -> Dict[str, Any]:
        """창 관련 동작 처리"""
        window_title = action.parameters.get("title")
        operation = action.parameters.get("operation", "activate")
        
        if not window_title:
            raise ValueError("Window title is required for window action")
            
        def find_window(title: str) -> Optional[int]:
            def callback(hwnd, windows):
                if win32gui.IsWindowVisible(hwnd):
                    window_text = win32gui.GetWindowText(hwnd)
                    if re.search(title, window_text, re.IGNORECASE):
                        windows.append(hwnd)
                return True
                
            windows = []
            win32gui.EnumWindows(callback, windows)
            return windows[0] if windows else None
            
        hwnd = find_window(window_title)
        if not hwnd:
            raise Exception(f"Window with title '{window_title}' not found")
            
        if operation == "activate":
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(hwnd)
        elif operation == "minimize":
            win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
        elif operation == "maximize":
            win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
        elif operation == "close":
            win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
            
        return {"window": window_title, "operation": operation}
        
    async def _handle_wait(self, action: WindowsAction) -> Dict[str, Any]:
        """대기 동작 처리"""
        seconds = action.parameters.get("seconds", 1)
        time.sleep(seconds)
        return {"waited": seconds}
        
    def parse_command(self, command_text: str) -> List[WindowsAction]:
        """명령 텍스트를 Windows 동작으로 파싱"""
        # 이 메서드는 나중에 자연어 처리를 통해 구현
        # 현재는 예시로 간단한 동작만 반환
        return [
            WindowsAction(
                action_type="type",
                parameters={"text": command_text},
                description="입력된 텍스트 타이핑"
            )
        ] 