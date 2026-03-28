"""Save and restore WorkflowSession as JSON."""
from __future__ import annotations
import json
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.workflow_session import WorkflowSession


class SessionSerializer:
    @staticmethod
    def save(session: "WorkflowSession", path: Path) -> None:
        path.write_text(json.dumps(session.to_dict(), indent=2, ensure_ascii=False),
                        encoding="utf-8")

    @staticmethod
    def load(path: Path) -> "WorkflowSession":
        from app.workflow_session import WorkflowSession
        data = json.loads(path.read_text(encoding="utf-8"))
        return WorkflowSession.from_dict(data)
