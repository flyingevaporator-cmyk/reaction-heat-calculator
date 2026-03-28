"""WorkflowConfigWidget: preset selection + step enable/disable + parameter editing."""
from __future__ import annotations
from typing import List, Dict, Any, Optional

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QGroupBox, QCheckBox, QLineEdit,
    QFormLayout, QDoubleSpinBox, QSpinBox,
    QScrollArea, QFrame,
)

from domain.presets import PresetLibrary


class _StepRow(QWidget):
    """One row per workflow step."""
    changed = pyqtSignal()

    def __init__(self, step_def: Dict[str, Any], parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._step_def = dict(step_def)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 2, 0, 2)

        self._check = QCheckBox(self._label())
        self._check.setChecked(step_def.get("enabled", True))
        self._check.stateChanged.connect(self.changed.emit)
        layout.addWidget(self._check, 0)

        self._method_edit = QLineEdit(step_def.get("params", {}).get("method", ""))
        self._method_edit.setPlaceholderText("method")
        self._method_edit.setMaximumWidth(140)
        self._method_edit.textChanged.connect(self.changed.emit)
        layout.addWidget(QLabel("method:"))
        layout.addWidget(self._method_edit)

        self._basis_edit = QLineEdit(step_def.get("params", {}).get("basis", ""))
        self._basis_edit.setPlaceholderText("basis")
        self._basis_edit.setMaximumWidth(120)
        self._basis_edit.textChanged.connect(self.changed.emit)
        layout.addWidget(QLabel("basis:"))
        layout.addWidget(self._basis_edit)

        layout.addStretch()

    def _label(self) -> str:
        names = {
            "neb":   "1. xTB NEB (TS初期構造探索)",
            "tsopt": "2. DFT TS最適化",
            "freq":  "3. 振動数計算",
            "irc":   "4. IRC計算",
            "ccsd":  "5. CCSD(T) 単点（任意）",
        }
        return names.get(self._step_def.get("name", ""), self._step_def.get("name", ""))

    def to_step_def(self) -> Dict[str, Any]:
        d = dict(self._step_def)
        d["enabled"] = self._check.isChecked()
        params = dict(d.get("params", {}))
        if self._method_edit.text():
            params["method"] = self._method_edit.text()
        if self._basis_edit.text():
            params["basis"] = self._basis_edit.text()
        d["params"] = params
        return d

    def update_from_preset(self, step_def: Dict[str, Any]) -> None:
        self._step_def = dict(step_def)
        self._check.setChecked(step_def.get("enabled", True))
        params = step_def.get("params", {})
        self._method_edit.setText(params.get("method", ""))
        self._basis_edit.setText(params.get("basis", ""))


class WorkflowConfigWidget(QWidget):
    config_changed = pyqtSignal()

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._preset_lib = PresetLibrary()
        self._step_rows: List[_StepRow] = []

        layout = QVBoxLayout(self)

        # Preset selector
        preset_box = QHBoxLayout()
        preset_box.addWidget(QLabel("反応タイプ:"))
        self._preset_combo = QComboBox()
        for label in self._preset_lib.labels():
            self._preset_combo.addItem(label)
        self._preset_combo.currentTextChanged.connect(self._on_preset_changed)
        preset_box.addWidget(self._preset_combo, 1)
        layout.addLayout(preset_box)

        # Common params
        common = QGroupBox("共通パラメータ")
        form = QFormLayout(common)
        self._ncores = QSpinBox()
        self._ncores.setRange(1, 64)
        self._ncores.setValue(4)
        form.addRow("並列コア数:", self._ncores)
        self._memory = QDoubleSpinBox()
        self._memory.setRange(1.0, 256.0)
        self._memory.setValue(8.0)
        self._memory.setSuffix(" GB")
        form.addRow("メモリ:", self._memory)
        layout.addWidget(common)

        # Steps
        steps_group = QGroupBox("ワークフローステップ")
        steps_layout = QVBoxLayout(steps_group)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        self._steps_layout = QVBoxLayout(container)
        self._steps_layout.setSpacing(2)
        scroll.setWidget(container)
        steps_layout.addWidget(scroll)
        layout.addWidget(steps_group)

        # Initialize with first preset
        self._load_preset(self._preset_combo.currentText())

    def _on_preset_changed(self, label: str) -> None:
        self._load_preset(label)
        self.config_changed.emit()

    def _load_preset(self, label: str) -> None:
        preset = self._preset_lib.get_by_label(label)
        if not preset:
            return
        # Find key for this label
        key = next((k for k, v in self._preset_lib.all_presets().items()
                    if v.get("label") == label), None)
        if not key:
            return
        steps = self._preset_lib.build_steps(key)

        if self._step_rows:
            for row in self._step_rows:
                row.changed.disconnect()
            for i in reversed(range(self._steps_layout.count())):
                w = self._steps_layout.itemAt(i).widget()
                if w:
                    w.setParent(None)
            self._step_rows.clear()

        for step_def in steps:
            row = _StepRow(step_def)
            row.changed.connect(self.config_changed.emit)
            self._steps_layout.addWidget(row)
            self._step_rows.append(row)

        # IRC → freq linkage
        self._wire_irc_freq_dependency()

    def _wire_irc_freq_dependency(self) -> None:
        irc_row = next((r for r in self._step_rows if "irc" in r._step_def.get("name", "")), None)
        freq_row = next((r for r in self._step_rows if "freq" in r._step_def.get("name", "")), None)
        if irc_row and freq_row:
            def _on_irc_changed():
                if irc_row._check.isChecked():
                    freq_row._check.setChecked(True)
            irc_row._check.stateChanged.connect(lambda _: _on_irc_changed())

    def get_step_defs(self) -> List[Dict[str, Any]]:
        for row in self._step_rows:
            d = row.to_step_def()
            d["params"]["n_cores"] = self._ncores.value()
            d["params"]["memory_gb"] = self._memory.value()
        return [r.to_step_def() for r in self._step_rows]
