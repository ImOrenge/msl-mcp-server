import pytest
import asyncio
from src.server.state_tracker import StateTracker, SessionState, CommandState
from datetime import datetime, timedelta
import json
from pathlib import Path
import shutil

@pytest.fixture
def temp_storage_dir(tmp_path):
    storage_dir = tmp_path / "test_state"
    storage_dir.mkdir()
    yield storage_dir
    shutil.rmtree(storage_dir)

@pytest.fixture
def state_tracker(temp_storage_dir):
    return StateTracker(str(temp_storage_dir))

@pytest.mark.asyncio
async def test_create_session(state_tracker):
    session = await state_tracker.create_session("test-session", "test-user")
    
    assert session.session_id == "test-session"
    assert session.user_id == "test-user"
    assert isinstance(session.start_time, datetime)
    assert isinstance(session.last_activity, datetime)
    assert session.commands == {}

@pytest.mark.asyncio
async def test_get_session(state_tracker):
    await state_tracker.create_session("test-session")
    session = await state_tracker.get_session("test-session")
    
    assert session is not None
    assert session.session_id == "test-session"
    
    non_existent = await state_tracker.get_session("non-existent")
    assert non_existent is None

@pytest.mark.asyncio
async def test_update_session(state_tracker):
    await state_tracker.create_session("test-session")
    metadata = {"test_key": "test_value"}
    
    session = await state_tracker.update_session("test-session", metadata)
    
    assert session is not None
    assert session.metadata["test_key"] == "test_value"
    assert (datetime.now() - session.last_activity).total_seconds() < 1

@pytest.mark.asyncio
async def test_start_command(state_tracker):
    await state_tracker.create_session("test-session")
    command_state = await state_tracker.start_command("test-session", "cmd-1")
    
    assert command_state is not None
    assert command_state.command_id == "cmd-1"
    assert command_state.status == "pending"
    assert isinstance(command_state.start_time, datetime)
    assert command_state.end_time is None

@pytest.mark.asyncio
async def test_update_command_status(state_tracker):
    await state_tracker.create_session("test-session")
    await state_tracker.start_command("test-session", "cmd-1")
    
    result = {"output": "test result"}
    command_state = await state_tracker.update_command_status(
        "test-session",
        "cmd-1",
        "completed",
        result=result
    )
    
    assert command_state is not None
    assert command_state.status == "completed"
    assert command_state.result == result
    assert command_state.end_time is not None

@pytest.mark.asyncio
async def test_get_command_history(state_tracker):
    await state_tracker.create_session("test-session")
    
    # 여러 명령 생성
    for i in range(5):
        await state_tracker.start_command("test-session", f"cmd-{i}")
        await state_tracker.update_command_status(
            "test-session",
            f"cmd-{i}",
            "completed" if i % 2 == 0 else "failed"
        )
    
    # 전체 이력 조회
    all_commands = await state_tracker.get_command_history("test-session")
    assert len(all_commands) == 5
    
    # 상태별 이력 조회
    completed = await state_tracker.get_command_history("test-session", status="completed")
    assert len(completed) == 3
    
    failed = await state_tracker.get_command_history("test-session", status="failed")
    assert len(failed) == 2
    
    # 제한된 이력 조회
    limited = await state_tracker.get_command_history("test-session", limit=2)
    assert len(limited) == 2

@pytest.mark.asyncio
async def test_cleanup_old_sessions(state_tracker):
    # 현재 세션 생성
    await state_tracker.create_session("current-session")
    
    # 오래된 세션 생성
    old_session = await state_tracker.create_session("old-session")
    old_session.last_activity = datetime.now() - timedelta(hours=25)
    await state_tracker.save_state()
    
    # 정리 실행
    await state_tracker.cleanup_old_sessions(max_age_hours=24)
    
    # 확인
    current = await state_tracker.get_session("current-session")
    old = await state_tracker.get_session("old-session")
    
    assert current is not None
    assert old is None

@pytest.mark.asyncio
async def test_state_persistence(temp_storage_dir):
    # 첫 번째 인스턴스로 상태 생성
    tracker1 = StateTracker(str(temp_storage_dir))
    await tracker1.create_session("test-session")
    await tracker1.start_command("test-session", "cmd-1")
    await tracker1.update_command_status("test-session", "cmd-1", "completed")
    
    # 두 번째 인스턴스로 상태 로드
    tracker2 = StateTracker(str(temp_storage_dir))
    session = await tracker2.get_session("test-session")
    
    assert session is not None
    assert "cmd-1" in session.commands
    assert session.commands["cmd-1"].status == "completed"

@pytest.mark.asyncio
async def test_invalid_session_operations(state_tracker):
    # 존재하지 않는 세션에 대한 작업
    result = await state_tracker.update_session("non-existent", {})
    assert result is None
    
    command = await state_tracker.start_command("non-existent", "cmd-1")
    assert command is None
    
    status = await state_tracker.update_command_status(
        "non-existent",
        "cmd-1",
        "completed"
    )
    assert status is None
    
    history = await state_tracker.get_command_history("non-existent")
    assert history == []

@pytest.mark.asyncio
async def test_concurrent_session_operations(state_tracker):
    await state_tracker.create_session("test-session")
    
    # 동시에 여러 명령 시작
    tasks = []
    for i in range(10):
        tasks.append(
            state_tracker.start_command("test-session", f"cmd-{i}")
        )
    
    results = await asyncio.gather(*tasks)
    
    # 모든 명령이 생성되었는지 확인
    assert all(r is not None for r in results)
    session = await state_tracker.get_session("test-session")
    assert len(session.commands) == 10 