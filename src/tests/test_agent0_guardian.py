"""
Unit tests for LlamaCppSupervisor and GuardianAgent.
Tests basic initialization, task toggles, and self-healing capabilities.
"""

import os
import shutil
import pytest
from pathlib import Path

from agent0core.core.llama_cpp_supervisor import LlamaCppSupervisor, LlamaModelSlot
from agent0core.core.guardian_agent import GuardianAgent, GuardianTask

def test_supervisor_initialization():
    # Arrange
    base_port = 9000
    max_slots = 3
    
    # Act
    supervisor = LlamaCppSupervisor(base_port=base_port, max_slots=max_slots)
    
    # Assert
    assert supervisor.base_port == base_port
    assert supervisor.max_slots == max_slots
    assert len(supervisor.slots) == max_slots
    assert supervisor.slots[0].port == base_port
    assert supervisor.slots[2].port == base_port + 2
    assert supervisor.slots[0].status == "empty"

def test_guardian_agent_task_loading():
    # Arrange
    supervisor = LlamaCppSupervisor()
    agent = GuardianAgent(supervisor)
    
    # Act
    task_count = len(agent.tasks)
    
    # Assert
    assert task_count == 22
    task_ids = [t.id for t in agent.tasks]
    assert "disk_space_check" in task_ids
    assert "temp_cleanup" in task_ids
    assert "memory_audit" in task_ids
    assert "directive_integrity" in task_ids

def test_guardian_task_toggles():
    # Arrange
    supervisor = LlamaCppSupervisor()
    agent = GuardianAgent(supervisor)
    task_id = "disk_space_check"
    
    # Act & Assert
    task = next(t for t in agent.tasks if t.id == task_id)
    assert task.enabled is True
    
    agent.toggle_task(task_id)
    assert task.enabled is False
    
    agent.toggle_task(task_id)
    assert task.enabled is True

@pytest.mark.asyncio
async def test_guardian_task_disk_check():
    # Arrange
    supervisor = LlamaCppSupervisor()
    agent = GuardianAgent(supervisor)
    
    # Act
    res = await agent.run_task("disk_space_check")
    
    # Assert
    assert res is not None
    assert res["id"] == "disk_space_check"
    assert res["lastResult"] in ("success", "warning")
    assert "Models directory" in res["lastDetail"]

@pytest.mark.asyncio
async def test_guardian_self_healing_directives(tmp_path):
    # Arrange: Setup mock files in temporary path
    orig_file = tmp_path / "Permanent_Active_Directives.txt"
    bak_dir = tmp_path / "state"
    bak_dir.mkdir()
    bak_file = bak_dir / "Permanent_Active_Directives.txt.bak"
    
    directive_content = b"Mock Directive Content: Law 1, Law 2..."
    orig_file.write_bytes(directive_content)
    bak_file.write_bytes(directive_content)
    
    # Instantiate supervisor and agent
    supervisor = LlamaCppSupervisor()
    agent = GuardianAgent(supervisor)
    
    # Mock OS paths internally to use tmp_path
    import unittest.mock as mock
    with mock.patch("agent0core.core.guardian_agent.Path") as mock_path:
        # Configure Path mock to return paths relative to tmp_path when requested
        def path_side_effect(*args):
            p_str = str(args[0]) if args else ""
            if "Permanent_Active_Directives.txt" in p_str:
                if "bak" in p_str:
                    return bak_file
                return orig_file
            return Path(*args)
            
        mock_path.side_effect = path_side_effect
        
        # Act 1: Verify intact
        res = await agent._task_directive_integrity()
        assert res["status"] == "success"
        assert "verified intact" in res["detail"]
        
        # Tamper with file
        orig_file.write_bytes(b"Corrupted Content!")
        
        # Act 2: Verify it self-heals
        res_heal = await agent._task_directive_integrity()
        assert res_heal["status"] == "success"
        assert "self-healed from backup" in res_heal["detail"]
        
        # Assert file content is restored
        assert orig_file.read_bytes() == directive_content
