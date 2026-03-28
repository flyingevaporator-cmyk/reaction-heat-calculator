"""MainWindow: top-level application window."""
from __future__ import annotations
from pathlib import Path
from typing import Optional

from PyQt6.QtCore import pyqtSlot, Qt
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QStatusBar, QPushButton, QLabel,
    QMessageBox, QFileDialog, QSplitter,
)

from app.job_manager import JobManager
from app.workflow_session import WorkflowSession, WorkflowStep, StepStatus
from domain.models import ReactionSystem
from domain.presets import PresetLibrary
from infrastructure.workspace_manager import WorkspaceManager
from infrastructure.session_serializer import SessionSerializer

from .widgets.molecule_input import MoleculeInputWidget
from .widgets.workflow_config import WorkflowConfigWidget
from .widgets.job_monitor import JobMonitorWidget
from .widgets.result_viewer import ResultViewerWidget


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("TS Calculator")
        self.setMinimumSize(1200, 800)

        self._job_manager = JobManager(self)
        self._workspace = WorkspaceManager()
        self._current_session: Optional[WorkflowSession] = None

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(2, 0, 2, 0)
        root.setSpacing(0)

        # Main splitter: left panel (input) | right panel (config/monitor/results)
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left: molecule input (maximized)
        self._mol_input = MoleculeInputWidget()
        splitter.addWidget(self._mol_input)

        # Right: compact tabs for config, monitor, results + action buttons
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(2)

        # Action bar (計算実行 / セッション) — compact, inside right panel
        action_bar = QHBoxLayout()
        action_bar.setContentsMargins(4, 2, 4, 2)
        action_bar.setSpacing(4)
        self._run_btn = QPushButton("▶ 計算実行")
        self._run_btn.setEnabled(False)
        self._run_btn.setFixedHeight(24)
        self._run_btn.setStyleSheet(
            "QPushButton { padding: 2px 12px; background: #89b4fa; color: #1e1e2e; "
            "border-radius: 3px; font-weight: bold; font-size: 11px; }"
            "QPushButton:disabled { background: #45475a; color: #6c7086; }"
            "QPushButton:hover { background: #74c7ec; }"
        )
        action_bar.addWidget(self._run_btn)
        self._load_btn = QPushButton("📂")
        self._load_btn.setFixedSize(24, 24)
        self._load_btn.setToolTip("セッションを開く")
        self._load_btn.setStyleSheet("padding: 0; font-size: 13px;")
        action_bar.addWidget(self._load_btn)
        self._session_label = QLabel("")
        self._session_label.setStyleSheet("color: #6c7086; font-size: 10px;")
        action_bar.addWidget(self._session_label)
        action_bar.addStretch()
        right_layout.addLayout(action_bar)

        right_tabs = QTabWidget()
        right_tabs.setStyleSheet("QTabBar::tab { padding: 3px 10px; font-size: 11px; }")

        self._workflow_config = WorkflowConfigWidget()
        right_tabs.addTab(self._workflow_config, "計算設定")

        self._job_monitor = JobMonitorWidget()
        right_tabs.addTab(self._job_monitor, "モニタ")

        self._result_viewer = ResultViewerWidget()
        right_tabs.addTab(self._result_viewer, "結果")

        right_layout.addWidget(right_tabs, 1)
        splitter.addWidget(right_panel)

        # Give ~70% to molecule input, ~30% to right panel
        splitter.setSizes([840, 360])
        splitter.setStretchFactor(0, 7)
        splitter.setStretchFactor(1, 3)
        root.addWidget(splitter)

        # Status bar
        self._status_bar = QStatusBar()
        self._status_bar.setFixedHeight(20)
        self._status_bar.setStyleSheet("font-size: 11px;")
        self.setStatusBar(self._status_bar)
        self._status_bar.showMessage("準備完了")

    def _connect_signals(self) -> None:
        self._mol_input.molecules_ready.connect(self._on_molecules_ready)
        self._workflow_config.config_changed.connect(self._on_config_changed)
        self._run_btn.clicked.connect(self._on_run_clicked)
        self._load_btn.clicked.connect(self._load_session)

        # JobManager → monitor
        self._job_manager.step_started.connect(
            lambda sid, name: self._job_monitor.on_step_started(name))
        self._job_manager.step_finished.connect(
            lambda sid, name, ok: self._on_step_finished(name, ok))
        self._job_manager.log_line.connect(
            lambda sid, name, line: self._job_monitor.on_log_line(name, line))
        self._job_manager.session_completed.connect(self._on_session_completed)
        self._job_manager.session_failed.connect(
            lambda sid, msg: self._job_monitor.on_session_failed(msg))
        self._job_manager.session_cancelled.connect(
            lambda sid: self._status_bar.showMessage("計算をキャンセルしました"))

        self._job_monitor.cancel_button.clicked.connect(self._on_cancel_clicked)

    @pyqtSlot(object, object)
    def _on_molecules_ready(self, reactants, products) -> None:
        r_info = " + ".join(f"{m.n_atoms}原子" for m in reactants)
        p_info = " + ".join(f"{m.n_atoms}原子" for m in products)
        self._status_bar.showMessage(f"反応物: {r_info}  →  生成物: {p_info}")
        self._run_btn.setEnabled(True)

    @pyqtSlot()
    def _on_config_changed(self) -> None:
        pass  # Could validate and show warnings

    @pyqtSlot()
    def _on_run_clicked(self) -> None:
        reactants = self._mol_input.reactants
        products = self._mol_input.products
        if not reactants or not products:
            QMessageBox.warning(self, "入力エラー", "反応物と生成物を両方入力してください。")
            return

        step_defs = self._workflow_config.get_step_defs()
        session_id = WorkspaceManager.new_session_id()
        session_dir = self._workspace.create_session_dir(session_id)

        rs = ReactionSystem(reactants=reactants, products=products)
        steps = [
            WorkflowStep(
                name=d["name"],
                calc_type=__import__("domain.models", fromlist=["CalcType"]).CalcType[d["calc_type"]],
                engine=d["engine"],
                params=d.get("params", {}),
                enabled=d.get("enabled", True),
            )
            for d in step_defs
        ]
        session = WorkflowSession(
            session_id=session_id,
            reaction_system=rs,
            steps=steps,
            session_dir=str(session_dir),
        )
        self._current_session = session
        self._session_label.setText(f"セッション: {session_id}")

        enabled_steps = [s.name for s in steps if s.enabled]
        self._job_monitor.setup_steps(enabled_steps)
        self._run_btn.setEnabled(False)
        self._status_bar.showMessage("計算実行中...")
        self._job_manager.submit(session)

    @pyqtSlot(str, bool)
    def _on_step_finished(self, step_name: str, success: bool) -> None:
        self._job_monitor.on_step_finished(step_name, success)
        # Show TS validator warnings
        if self._current_session and success:
            step = self._current_session.step_by_name(step_name)
            if step and step.result:
                warnings = step.result.extra.get("warnings", [])
                for w in warnings:
                    self._job_monitor.set_warning(step_name, w)

    @pyqtSlot(str)
    def _on_session_completed(self, session_id: str) -> None:
        self._job_monitor.on_session_completed()
        self._run_btn.setEnabled(True)
        self._status_bar.showMessage("計算完了")
        if self._current_session:
            self._result_viewer.update_from_session(self._current_session)

    @pyqtSlot()
    def _on_cancel_clicked(self) -> None:
        if self._current_session:
            self._job_manager.cancel(self._current_session.session_id)
            self._run_btn.setEnabled(True)

    def _load_session(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "セッションファイルを開く",
            str(Path.home() / ".ts_calculator"),
            "Session files (session.json);;JSON files (*.json)",
        )
        if not path:
            return
        try:
            session = SessionSerializer.load(Path(path))
            self._current_session = session
            self._session_label.setText(f"セッション: {session.session_id}")
            self._result_viewer.update_from_session(session)
            self._status_bar.showMessage(f"セッションを読み込みました: {path}")
        except Exception as e:
            QMessageBox.critical(self, "読み込みエラー", str(e))
