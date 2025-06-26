import pytest
import asyncio
from src.server.windows_automation import WindowsAction, WindowsAutomation
from unittest.mock import patch, MagicMock

@pytest.fixture
def windows_automation():
    return WindowsAutomation()

@pytest.mark.asyncio
async def test_click_action_with_coordinates():
    with patch("pyautogui.click") as mock_click:
        automation = WindowsAutomation()
        action = WindowsAction(
            action_type="click",
            parameters={"x": 100, "y": 200}
        )
        
        result = await automation.execute_action(action)
        
        assert result.success
        assert result.result == {"clicked": True}
        mock_click.assert_called_once_with(x=100, y=200, button="left", clicks=1)

@pytest.mark.asyncio
async def test_click_action_with_image():
    with patch("pyautogui.locateOnScreen") as mock_locate, \
         patch("pyautogui.click") as mock_click:
        mock_locate.return_value = (100, 200, 50, 50)
        automation = WindowsAutomation()
        action = WindowsAction(
            action_type="click",
            parameters={"image": "test.png"}
        )
        
        result = await automation.execute_action(action)
        
        assert result.success
        assert result.result == {"clicked": True}
        mock_locate.assert_called_once_with("test.png", confidence=0.9)
        mock_click.assert_called_once()

@pytest.mark.asyncio
async def test_type_action():
    with patch("pyautogui.write") as mock_write:
        automation = WindowsAutomation()
        action = WindowsAction(
            action_type="type",
            parameters={"text": "Hello, World!"}
        )
        
        result = await automation.execute_action(action)
        
        assert result.success
        assert result.result == {"typed": "Hello, World!"}
        mock_write.assert_called_once_with("Hello, World!", interval=0.1)

@pytest.mark.asyncio
async def test_hotkey_action():
    with patch("pyautogui.hotkey") as mock_hotkey:
        automation = WindowsAutomation()
        action = WindowsAction(
            action_type="hotkey",
            parameters={"keys": ["ctrl", "c"]}
        )
        
        result = await automation.execute_action(action)
        
        assert result.success
        assert result.result == {"hotkey": "ctrl+c"}
        mock_hotkey.assert_called_once_with("ctrl", "c")

@pytest.mark.asyncio
async def test_window_action():
    with patch("win32gui.FindWindow") as mock_find, \
         patch("win32gui.ShowWindow") as mock_show, \
         patch("win32gui.SetForegroundWindow") as mock_set:
        mock_find.return_value = 12345
        automation = WindowsAutomation()
        action = WindowsAction(
            action_type="window",
            parameters={
                "title": "Notepad",
                "operation": "activate"
            }
        )
        
        result = await automation.execute_action(action)
        
        assert result.success
        assert result.result == {"window": "Notepad", "operation": "activate"}

@pytest.mark.asyncio
async def test_wait_action():
    with patch("time.sleep") as mock_sleep:
        automation = WindowsAutomation()
        action = WindowsAction(
            action_type="wait",
            parameters={"seconds": 2}
        )
        
        result = await automation.execute_action(action)
        
        assert result.success
        assert result.result == {"waited": 2}
        mock_sleep.assert_called_once_with(2)

@pytest.mark.asyncio
async def test_execute_actions_sequence():
    with patch("pyautogui.click") as mock_click, \
         patch("pyautogui.write") as mock_write:
        automation = WindowsAutomation()
        actions = [
            WindowsAction(
                action_type="click",
                parameters={"x": 100, "y": 200}
            ),
            WindowsAction(
                action_type="type",
                parameters={"text": "Test"}
            )
        ]
        
        results = await automation.execute_actions(actions)
        
        assert len(results) == 2
        assert all(r.success for r in results)
        mock_click.assert_called_once()
        mock_write.assert_called_once()

@pytest.mark.asyncio
async def test_invalid_action_type():
    automation = WindowsAutomation()
    action = WindowsAction(
        action_type="invalid",
        parameters={}
    )
    
    result = await automation.execute_action(action)
    
    assert not result.success
    assert "Unknown action type" in result.error

@pytest.mark.asyncio
async def test_missing_required_parameters():
    automation = WindowsAutomation()
    action = WindowsAction(
        action_type="type",
        parameters={}
    )
    
    result = await automation.execute_action(action)
    
    assert not result.success
    assert "Text parameter is required" in result.error 