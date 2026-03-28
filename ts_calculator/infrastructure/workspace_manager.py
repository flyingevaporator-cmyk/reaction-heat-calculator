"""Manages per-session and per-step working directories."""
from __future__ import annotations
import shutil
import time
from pathlib import Path
from typing import Optional


class WorkspaceManager:
    def __init__(self, base_dir: Optional[Path] = None) -> None:
        if base_dir is None:
            base_dir = Path.home() / ".ts_calculator" / "workspaces"
        self.base_dir = base_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def create_session_dir(self, session_id: str) -> Path:
        path = self.base_dir / session_id
        path.mkdir(parents=True, exist_ok=True)
        return path

    def create_step_dir(self, session_dir: Path, step_name: str) -> Path:
        path = session_dir / step_name
        path.mkdir(parents=True, exist_ok=True)
        return path

    def cleanup_session(self, session_dir: Path) -> None:
        if session_dir.exists():
            shutil.rmtree(session_dir)

    @staticmethod
    def new_session_id() -> str:
        return f"session_{int(time.time() * 1000)}"
