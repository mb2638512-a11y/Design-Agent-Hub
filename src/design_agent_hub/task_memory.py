"""Small opt-in SQLite memory for manager task continuity.

Only task metadata and bounded text summaries are stored. Disabled unless
MANAGER_MEMORY_ENABLED=true; keep the database on a private local disk.
"""
from __future__ import annotations

import json
import os
import sqlite3
import time
from pathlib import Path
from typing import Any


def _enabled() -> bool:
    return os.getenv("MANAGER_MEMORY_ENABLED", "false").strip().casefold() in {"1", "true", "yes", "on"}


def _db_path() -> Path:
    return Path(os.getenv("MANAGER_MEMORY_PATH", ".design_agent_hub_memory.sqlite3")).expanduser()


def remember_task(task: str, result: dict[str, Any]) -> dict[str, Any]:
    """Persist a bounded task/result summary when memory is explicitly enabled."""
    if not _enabled():
        return {"enabled": False, "stored": False, "reason": "opt_in_disabled"}
    path = _db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    compact_result = {
        "status": result.get("status"),
        "workflow_mode": result.get("workflow_mode"),
        "selected_agent": result.get("selected_agent"),
        "successful_agents": result.get("successful_agents"),
        "failed_agents": result.get("failed_agents"),
    }
    with sqlite3.connect(path, timeout=3.0) as connection:
        connection.execute(
            "CREATE TABLE IF NOT EXISTS task_memory (id INTEGER PRIMARY KEY AUTOINCREMENT, created_at INTEGER NOT NULL, task TEXT NOT NULL, result_summary TEXT NOT NULL)"
        )
        connection.execute(
            "INSERT INTO task_memory (created_at, task, result_summary) VALUES (?, ?, ?)",
            (int(time.time()), task[:2000], json.dumps(compact_result, ensure_ascii=False)),
        )
        connection.execute(
            "DELETE FROM task_memory WHERE id NOT IN (SELECT id FROM task_memory ORDER BY id DESC LIMIT 100)"
        )
    return {"enabled": True, "stored": True, "retained_limit": 100, "database_path": str(path)}


def recent_tasks(limit: int = 10) -> dict[str, Any]:
    """Return recent task summaries; never return full specialist outputs."""
    if not _enabled():
        return {"enabled": False, "tasks": [], "reason": "opt_in_disabled"}
    safe_limit = max(1, min(int(limit), 50))
    path = _db_path()
    if not path.exists():
        return {"enabled": True, "tasks": []}
    with sqlite3.connect(path, timeout=3.0) as connection:
        connection.row_factory = sqlite3.Row
        exists = connection.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name='task_memory'"
        ).fetchone()
        if not exists:
            return {"enabled": True, "tasks": []}
        rows = connection.execute(
            "SELECT id, created_at, task, result_summary FROM task_memory ORDER BY id DESC LIMIT ?",
            (safe_limit,),
        ).fetchall()
    return {
        "enabled": True,
        "tasks": [
            {"id": row["id"], "created_at": row["created_at"], "task": row["task"], "result": json.loads(row["result_summary"])}
            for row in rows
        ],
    }


def clear_memory() -> dict[str, Any]:
    """Delete the locally stored task history when memory is enabled."""
    if not _enabled():
        return {"enabled": False, "cleared": False, "reason": "opt_in_disabled"}
    path = _db_path()
    if path.exists():
        with sqlite3.connect(path, timeout=3.0) as connection:
            connection.execute("DROP TABLE IF EXISTS task_memory")
    return {"enabled": True, "cleared": True}
