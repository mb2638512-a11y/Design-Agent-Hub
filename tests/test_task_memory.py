"""Tests for privacy-first opt-in manager memory."""

import json

from design_agent_hub import task_memory


def test_memory_is_disabled_by_default(monkeypatch, tmp_path):
    monkeypatch.delenv("MANAGER_MEMORY_ENABLED", raising=False)
    monkeypatch.setenv("MANAGER_MEMORY_PATH", str(tmp_path / "memory.sqlite3"))
    result = task_memory.remember_task("Create a design", {"status": "delegated"})
    assert result["stored"] is False
    assert not (tmp_path / "memory.sqlite3").exists()


def test_memory_stores_only_compact_summary_and_can_clear(monkeypatch, tmp_path):
    db_path = tmp_path / "memory.sqlite3"
    monkeypatch.setenv("MANAGER_MEMORY_ENABLED", "true")
    monkeypatch.setenv("MANAGER_MEMORY_PATH", str(db_path))
    stored = task_memory.remember_task(
        "Create a design",
        {"status": "delegated", "selected_agent": {"id": "design"}, "result": {"private_detail": "not stored"}},
    )
    assert stored["stored"] is True
    result = task_memory.recent_tasks(5)
    assert result["tasks"][0]["task"] == "Create a design"
    assert result["tasks"][0]["result"]["status"] == "delegated"
    assert "private_detail" not in json.dumps(result)
    assert task_memory.clear_memory()["cleared"] is True
    assert task_memory.recent_tasks()["tasks"] == []
