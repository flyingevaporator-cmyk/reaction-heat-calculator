"""JobManager: manages calculation jobs on QThreadPool."""
from __future__ import annotations
from typing import Callable, Dict, Optional

from PyQt6.QtCore import QObject, QThreadPool, pyqtSignal

from .calculation_worker import CalculationWorker
from .workflow_session import WorkflowSession, WorkflowStep


class JobManager(QObject):
    # Signals forwarded from workers
    step_started = pyqtSignal(str, str)       # session_id, step_name
    step_finished = pyqtSignal(str, str, bool) # session_id, step_name, success
    log_line = pyqtSignal(str, str, str)       # session_id, step_name, line
    session_completed = pyqtSignal(str)        # session_id
    session_failed = pyqtSignal(str, str)      # session_id, error_message
    session_cancelled = pyqtSignal(str)        # session_id

    def __init__(self, parent: Optional[QObject] = None) -> None:
        super().__init__(parent)
        self._pool = QThreadPool.globalInstance()
        self._workers: Dict[str, CalculationWorker] = {}

    def submit(self, session: WorkflowSession) -> None:
        sid = session.session_id

        worker = CalculationWorker(session)
        worker.signals.step_started.connect(lambda step: self.step_started.emit(sid, step.name))
        worker.signals.step_finished.connect(
            lambda step: self.step_finished.emit(sid, step.name, step.status.name == "SUCCESS")
        )
        worker.signals.log_line.connect(lambda sname, line: self.log_line.emit(sid, sname, line))
        worker.signals.completed.connect(lambda: self._on_completed(sid))
        worker.signals.failed.connect(lambda msg: self._on_failed(sid, msg))
        worker.signals.cancelled.connect(lambda: self.session_cancelled.emit(sid))

        self._workers[sid] = worker
        self._pool.start(worker)

    def cancel(self, session_id: str) -> None:
        worker = self._workers.get(session_id)
        if worker:
            worker.cancel()

    def _on_completed(self, session_id: str) -> None:
        self._workers.pop(session_id, None)
        self.session_completed.emit(session_id)

    def _on_failed(self, session_id: str, message: str) -> None:
        self._workers.pop(session_id, None)
        self.session_failed.emit(session_id, message)
