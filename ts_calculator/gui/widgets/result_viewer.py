"""ResultViewerWidget: energy diagram, IRC curve, frequency list, 3D structure."""
from __future__ import annotations
from typing import List, Optional, TYPE_CHECKING

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTabWidget, QTableWidget,
    QTableWidgetItem, QLabel, QSplitter,
)
from PyQt6.QtCore import Qt

from app.workflow_session import WorkflowSession, StepStatus
from domain.models import CalcType
from .molecule_viewer_3d import MoleculeViewer3D

try:
    import matplotlib
    matplotlib.use("QtAgg")
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
    from matplotlib.figure import Figure
    _HAS_MPL = True
except ImportError:
    _HAS_MPL = False


class ResultViewerWidget(QWidget):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)

        self._tabs = QTabWidget()
        layout.addWidget(self._tabs)

        # Tab 1: Energy summary
        self._energy_tab = _EnergyTab()
        self._tabs.addTab(self._energy_tab, "エネルギー")

        # Tab 2: Frequencies
        self._freq_tab = _FrequencyTab()
        self._tabs.addTab(self._freq_tab, "振動数")

        # Tab 3: TS structure 3D
        self._struct_tab = MoleculeViewer3D()
        self._tabs.addTab(self._struct_tab, "TS構造")

        # Tab 4: IRC curve
        self._irc_tab = _IRCTab()
        self._tabs.addTab(self._irc_tab, "IRC")

    def update_from_session(self, session: WorkflowSession) -> None:
        self._energy_tab.update(session)
        self._freq_tab.update(session)
        self._irc_tab.update(session)

        # Show TS structure from tsopt step
        tsopt = session.step_by_name("tsopt")
        if tsopt and tsopt.result and tsopt.result.molecule:
            self._struct_tab.set_molecule(tsopt.result.molecule)


class _EnergyTab(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        self._table = QTableWidget(0, 3)
        self._table.setHorizontalHeaderLabels(["ステップ", "エネルギー (Hartree)", "状態"])
        self._table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self._table)
        if _HAS_MPL:
            fig = Figure(figsize=(5, 2.5), facecolor="#1e1e2e")
            self._ax = fig.add_subplot(111)
            self._canvas = FigureCanvasQTAgg(fig)
            layout.addWidget(self._canvas)

    def update(self, session: WorkflowSession) -> None:
        rows = []
        for step in session.steps:
            if step.result and step.result.energy is not None:
                rows.append((step.name, step.result.energy, step.status.name))

        self._table.setRowCount(len(rows))
        for i, (name, e, status) in enumerate(rows):
            self._table.setItem(i, 0, QTableWidgetItem(name))
            self._table.setItem(i, 1, QTableWidgetItem(f"{e:.8f}"))
            self._table.setItem(i, 2, QTableWidgetItem(status))

        if _HAS_MPL and rows:
            self._draw_energy_diagram(rows)

    def _draw_energy_diagram(self, rows: list) -> None:
        self._ax.clear()
        self._ax.set_facecolor("#1e1e2e")
        self._ax.tick_params(colors="#cdd6f4")
        self._ax.spines[:].set_color("#45475a")
        names = [r[0] for r in rows]
        energies = [r[1] for r in rows]
        e0 = energies[0]
        rel = [(e - e0) * 627.5 for e in energies]  # Hartree → kcal/mol
        self._ax.plot(names, rel, "o-", color="#89b4fa")
        self._ax.set_ylabel("ΔE (kcal/mol)", color="#cdd6f4")
        self._ax.set_title("エネルギープロファイル", color="#cdd6f4")
        self._canvas.draw()


class _FrequencyTab(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        self._warning = QLabel("")
        self._warning.setStyleSheet("color: #f38ba8; font-weight: bold;")
        layout.addWidget(self._warning)
        self._table = QTableWidget(0, 2)
        self._table.setHorizontalHeaderLabels(["#", "振動数 (cm⁻¹)"])
        self._table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self._table)

    def update(self, session: WorkflowSession) -> None:
        freq_step = session.step_by_name("freq")
        if not freq_step or not freq_step.result or not freq_step.result.frequency_data:
            return
        fd = freq_step.result.frequency_data
        warnings = freq_step.result.extra.get("warnings", [])
        self._warning.setText("\n".join(warnings))

        self._table.setRowCount(len(fd.frequencies))
        for i, f in enumerate(fd.frequencies):
            self._table.setItem(i, 0, QTableWidgetItem(str(i + 1)))
            item = QTableWidgetItem(f"{f:.2f}")
            if f < 0:
                item.setForeground(Qt.GlobalColor.red)
            self._table.setItem(i, 1, item)


class _IRCTab(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        self._label = QLabel("IRC結果なし")
        layout.addWidget(self._label)
        if _HAS_MPL:
            fig = Figure(figsize=(5, 3), facecolor="#1e1e2e")
            self._ax = fig.add_subplot(111)
            self._canvas = FigureCanvasQTAgg(fig)
            layout.addWidget(self._canvas)

    def update(self, session: WorkflowSession) -> None:
        irc_step = session.step_by_name("irc")
        if not irc_step or not irc_step.result or not irc_step.result.irc_data:
            return
        irc = irc_step.result.irc_data
        if not _HAS_MPL:
            self._label.setText(f"IRC: {len(irc.forward_path)} forward / {len(irc.reverse_path)} reverse images")
            return

        self._ax.clear()
        self._ax.set_facecolor("#1e1e2e")
        self._ax.tick_params(colors="#cdd6f4")
        self._ax.spines[:].set_color("#45475a")

        if irc.reverse_energies:
            rev = list(reversed([(e - irc.reverse_energies[-1]) * 627.5 for e in irc.reverse_energies]))
            self._ax.plot(range(len(rev)), rev, color="#a6e3a1", label="逆方向")
        if irc.forward_energies:
            offset = len(irc.reverse_energies) if irc.reverse_energies else 0
            fwd = [(e - irc.forward_energies[0]) * 627.5 for e in irc.forward_energies]
            self._ax.plot(range(offset, offset + len(fwd)), fwd, color="#89b4fa", label="順方向")

        self._ax.set_ylabel("ΔE (kcal/mol)", color="#cdd6f4")
        self._ax.set_title("IRC経路", color="#cdd6f4")
        self._ax.legend(facecolor="#313244", labelcolor="#cdd6f4")
        self._canvas.draw()
