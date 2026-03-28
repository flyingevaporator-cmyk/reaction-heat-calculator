"""CalculationWorker: runs WorkflowOrchestrator in a QThreadPool thread."""
from __future__ import annotations
from PyQt6.QtCore import QRunnable, QObject, pyqtSignal

from .workflow_orchestrator import WorkflowOrchestrator
from .workflow_session import WorkflowSession, WorkflowStep


class WorkerSignals(QObject):
    step_started = pyqtSignal(object)     # WorkflowStep
    step_finished = pyqtSignal(object)    # WorkflowStep
    log_line = pyqtSignal(str, str)       # step_name, line
    completed = pyqtSignal()
    failed = pyqtSignal(str)              # error message
    cancelled = pyqtSignal()


class CalculationWorker(QRunnable):
    def __init__(self, session: WorkflowSession) -> None:
        super().__init__()
        self.setAutoDelete(True)
        self.signals = WorkerSignals()
        self._orchestrator = WorkflowOrchestrator(
            session=session,
            on_step_start=self.signals.step_started.emit,
            on_step_done=self.signals.step_finished.emit,
            on_log_line=self.signals.log_line.emit,
            on_cancelled=self.signals.cancelled.emit,
        )

    def run(self) -> None:
        try:
            self._orchestrator.run()
            if not self._orchestrator._cancel_requested:
                self.signals.completed.emit()
        except Exception as e:
            self.signals.failed.emit(str(e))

    def cancel(self) -> None:
        self._orchestrator.cancel()
