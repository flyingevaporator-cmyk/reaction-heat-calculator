"""JobMonitorWidget: real-time log display + step status indicators."""
from __future__ import annotations
from typing import Dict, Optional

from PyQt6.QtCore import pyqtSlot, Qt
from PyQt6.QtGui import QFont, QColor, QTextCharFormat, QTextCursor
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTextEdit, QPushButton, QProgressBar, QFrame,
    QSizePolicy,
)

from app.workflow_session import StepStatus


_STATUS_ICONS = {
    StepStatus.PENDING:  ("⬜", "#6c7086"),
    StepStatus.RUNNING:  ("🔄", "#fab387"),
    StepStatus.SUCCESS:  ("✅", "#a6e3a1"),
    StepStatus.FAILED:   ("❌", "#f38ba8"),
    StepStatus.SKIPPED:  ("⏭", "#6c7086"),
}


class _StepIndicator(QLabel):
    def __init__(self, step_name: str, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._step_name = step_name
        self.set_status(StepStatus.PENDING)
        self.setMinimumWidth(240)

    def set_status(self, status: StepStatus, detail: str = "") -> None:
        icon, color = _STATUS_ICONS[status]
        label = f"{icon} {self._step_name}"
        if detail:
            label += f"  <span style='color:#f38ba8;font-size:11px'>{detail}</span>"
        self.setText(f"<span style='color:{color}'>{label}</span>")


class JobMonitorWidget(QWidget):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)

        # Step status panel
        self._step_labels: Dict[str, _StepIndicator] = {}
        self._steps_frame = QFrame()
        self._steps_frame.setFrameShape(QFrame.Shape.StyledPanel)
        self._steps_layout = QVBoxLayout(self._steps_frame)
        self._steps_layout.setSpacing(2)
        layout.addWidget(self._steps_frame)

        # Progress bar
        self._progress = QProgressBar()
        self._progress.setRange(0, 100)
        self._progress.setValue(0)
        layout.addWidget(self._progress)

        # Log output
        self._log = QTextEdit()
        self._log.setReadOnly(True)
        self._log.setFont(QFont("Consolas", 10))
        self._log.setStyleSheet("background: #1e1e2e; color: #cdd6f4;")
        layout.addWidget(self._log)

        # Cancel button
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        self._cancel_btn = QPushButton("キャンセル")
        self._cancel_btn.setEnabled(False)
        btn_row.addWidget(self._cancel_btn)
        layout.addLayout(btn_row)

    def setup_steps(self, step_names: list[str]) -> None:
        """Initialize step indicators from step name list."""
        # Clear existing
        for i in reversed(range(self._steps_layout.count())):
            w = self._steps_layout.itemAt(i).widget()
            if w:
                w.setParent(None)
        self._step_labels.clear()

        for name in step_names:
            ind = _StepIndicator(name)
            self._steps_layout.addWidget(ind)
            self._step_labels[name] = ind

        self._progress.setValue(0)
        self._log.clear()
        self._cancel_btn.setEnabled(True)

    @pyqtSlot(str)
    def on_step_started(self, step_name: str) -> None:
        if step_name in self._step_labels:
            self._step_labels[step_name].set_status(StepStatus.RUNNING)

    @pyqtSlot(str, bool)
    def on_step_finished(self, step_name: str, success: bool) -> None:
        if step_name in self._step_labels:
            status = StepStatus.SUCCESS if success else StepStatus.FAILED
            self._step_labels[step_name].set_status(status)
        # Update progress
        done = sum(1 for lbl in self._step_labels.values()
                   if "✅" in lbl.text() or "❌" in lbl.text())
        total = len(self._step_labels)
        self._progress.setValue(int(done / total * 100) if total else 0)

    @pyqtSlot(str, str)
    def on_log_line(self, step_name: str, line: str) -> None:
        fmt = QTextCharFormat()
        if "error" in line.lower() or "fatal" in line.lower():
            fmt.setForeground(QColor("#f38ba8"))
        elif "warning" in line.lower():
            fmt.setForeground(QColor("#f9e2af"))
        else:
            fmt.setForeground(QColor("#cdd6f4"))

        cursor = self._log.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertText(f"[{step_name}] {line}\n", fmt)
        self._log.setTextCursor(cursor)
        self._log.ensureCursorVisible()

    @pyqtSlot()
    def on_session_completed(self) -> None:
        self._progress.setValue(100)
        self._cancel_btn.setEnabled(False)
        self._log.append("\n✅ 全ワークフロー完了")

    @pyqtSlot(str)
    def on_session_failed(self, message: str) -> None:
        self._cancel_btn.setEnabled(False)
        self._log.append(f"\n❌ エラー: {message}")

    def set_warning(self, step_name: str, warning: str) -> None:
        if step_name in self._step_labels:
            self._step_labels[step_name].set_status(StepStatus.SUCCESS, warning)

    @property
    def cancel_button(self) -> QPushButton:
        return self._cancel_btn
