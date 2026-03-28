"""MoleculeInputWidget: one Ketcher canvas per side for multi-fragment input.

Draw A + B as disconnected fragments in a single Ketcher canvas.
RDKit splits them into individual Molecules on 3D conversion.
"""
from __future__ import annotations
from pathlib import Path
from typing import List, Optional

from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QSpinBox, QSplitter, QFrame,
    QFileDialog, QMessageBox,
)

from domain.models import Molecule
from infrastructure.structure_file_io import StructureFileIO
from infrastructure.molfile_converter import (
    molfile_to_molecules, is_rdkit_available,
)
from .ketcher_editor import KetcherEditor
from .molecule_viewer_3d import MoleculeViewer3D


class _ReactionSide(QWidget):
    """One side of the reaction: single Ketcher canvas + 3D viewer.

    The user draws one or more disconnected fragments in Ketcher (A + B).
    On 3D-convert, RDKit splits them into individual Molecules.
    """
    molecules_changed = pyqtSignal()

    def __init__(self, title: str, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._title = title
        self._molecules: List[Molecule] = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(2)

        # ── Header row ──
        header = QHBoxLayout()
        header.setSpacing(4)
        header.addWidget(QLabel(f"<b style='font-size:13px;'>{title}</b>"))

        file_btn = QPushButton("📂 ファイル")
        file_btn.setFixedHeight(22)
        file_btn.setToolTip("XYZ/SDF/MOLファイルから読み込み")
        file_btn.clicked.connect(self._open_file)
        header.addWidget(file_btn)

        self._convert_btn = QPushButton("▶ 3D変換")
        self._convert_btn.setFixedHeight(22)
        self._convert_btn.setToolTip(
            "Ketcher → RDKit 3D座標生成\n"
            "複数フラグメントは自動分割されます"
        )
        self._convert_btn.setStyleSheet(
            "QPushButton { background: #89b4fa; color: #1e1e2e; font-weight: bold; "
            "border-radius: 3px; padding: 2px 10px; font-size: 11px; }"
            "QPushButton:hover { background: #74c7ec; }"
            "QPushButton:disabled { background: #45475a; color: #6c7086; }"
        )
        self._convert_btn.setEnabled(is_rdkit_available())
        self._convert_btn.clicked.connect(self._on_convert_clicked)
        header.addWidget(self._convert_btn)

        header.addWidget(QLabel("電荷:"))
        self._charge = QSpinBox()
        self._charge.setRange(-10, 10)
        self._charge.setValue(0)
        self._charge.setFixedWidth(48)
        self._charge.setFixedHeight(22)
        header.addWidget(self._charge)

        header.addWidget(QLabel("多重度:"))
        self._mult = QSpinBox()
        self._mult.setRange(1, 10)
        self._mult.setValue(1)
        self._mult.setFixedWidth(48)
        self._mult.setFixedHeight(22)
        header.addWidget(self._mult)

        self._info_label = QLabel("")
        self._info_label.setStyleSheet("color: #89b4fa; font-size: 11px;")
        header.addWidget(self._info_label)
        header.addStretch()
        layout.addLayout(header)

        # ── Resizable splitter: Ketcher (top) | 3D viewer (bottom) ──
        self._splitter = QSplitter(Qt.Orientation.Vertical)
        self._splitter.setHandleWidth(5)
        self._splitter.setStyleSheet(
            "QSplitter::handle { background: #313244; border-radius: 2px; }"
            "QSplitter::handle:hover { background: #89b4fa; }"
        )

        self._ketcher = KetcherEditor(self)
        self._ketcher.molfile_exported.connect(self._on_molfile_exported)
        self._splitter.addWidget(self._ketcher)

        # 3D viewer with a subtle frame
        viewer_frame = QFrame()
        viewer_frame.setFrameShape(QFrame.Shape.StyledPanel)
        viewer_frame.setStyleSheet(
            "QFrame { border: 1px solid #313244; border-radius: 2px; }"
        )
        vf_layout = QVBoxLayout(viewer_frame)
        vf_layout.setContentsMargins(0, 0, 0, 0)
        self._viewer = MoleculeViewer3D(self)
        vf_layout.addWidget(self._viewer)
        self._splitter.addWidget(viewer_frame)

        # Default: 75% Ketcher, 25% 3D viewer (user can drag to resize)
        self._splitter.setStretchFactor(0, 3)
        self._splitter.setStretchFactor(1, 1)
        # Set minimum heights so neither collapses completely
        self._ketcher.setMinimumHeight(120)
        viewer_frame.setMinimumHeight(80)

        layout.addWidget(self._splitter, 1)

        if not is_rdkit_available():
            warn = QLabel("⚠ RDKit未インストール: pip install rdkit")
            warn.setStyleSheet("color: #f38ba8; font-size: 10px;")
            layout.addWidget(warn)

    # ── Actions ──

    def _on_convert_clicked(self) -> None:
        self._ketcher.export_molfile()

    def _on_molfile_exported(self, molfile: str) -> None:
        lines = molfile.strip().splitlines()
        counts_line = lines[3] if len(lines) > 3 else ""
        if counts_line.strip().startswith("0  0"):
            QMessageBox.information(
                self, "3D変換",
                "分子が描画されていません。\n"
                "Ketcherで構造を描いてから3D変換してください。",
            )
            return
        try:
            mols = molfile_to_molecules(
                molfile,
                charge=self._charge.value(),
                multiplicity=self._mult.value(),
            )
            self._set_molecules(mols)
        except Exception as e:
            QMessageBox.warning(self, "3D変換エラー", str(e))

    def _open_file(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "構造ファイルを選択",
            str(Path.home()),
            "Molecular files (*.xyz *.sdf *.mol *.mol2);;All files (*)",
        )
        if not path:
            return
        try:
            mol = StructureFileIO.read(Path(path))
            mol = Molecule(
                atoms=mol.atoms,
                charge=self._charge.value(),
                multiplicity=self._mult.value(),
                name=Path(path).stem,
            )
            self._set_molecules([mol])
        except Exception as e:
            QMessageBox.critical(self, "読み込みエラー", str(e))

    def _set_molecules(self, mols: List[Molecule]) -> None:
        self._molecules = mols
        # Update info label
        if len(mols) == 1:
            self._info_label.setText(f"{mols[0].n_atoms}原子")
        else:
            parts = [f"{m.n_atoms}" for m in mols]
            total = sum(m.n_atoms for m in mols)
            self._info_label.setText(
                f"{len(mols)}分子 ({' + '.join(parts)} = {total}原子)"
            )
        # Show all molecules in 3D viewer
        if mols:
            self._viewer.set_molecules(mols)
        self.molecules_changed.emit()

    # ── Public API ──

    @property
    def molecules(self) -> List[Molecule]:
        return list(self._molecules)

    @property
    def all_filled(self) -> bool:
        return len(self._molecules) > 0


class MoleculeInputWidget(QWidget):
    """Molecule input panel: reactant side | product side.

    Each side is a single Ketcher canvas where multiple fragments
    can be drawn (A + B). RDKit splits them on 3D conversion.

    Signals:
        molecules_ready(list[Molecule], list[Molecule])
    """
    molecules_ready = pyqtSignal(object, object)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Horizontal splitter: reactant | arrow | product
        splitter = QSplitter(Qt.Orientation.Horizontal)

        self._reactant_side = _ReactionSide("反応物")
        self._product_side = _ReactionSide("生成物")

        splitter.addWidget(self._reactant_side)

        # Arrow separator
        arrow = QLabel("→")
        arrow.setFixedWidth(24)
        arrow.setAlignment(Qt.AlignmentFlag.AlignCenter)
        arrow.setStyleSheet("font-size: 24px; color: #89b4fa; font-weight: bold;")
        splitter.addWidget(arrow)

        splitter.addWidget(self._product_side)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 0)  # arrow doesn't stretch
        splitter.setStretchFactor(2, 1)
        layout.addWidget(splitter)

        self._reactant_side.molecules_changed.connect(self._check_ready)
        self._product_side.molecules_changed.connect(self._check_ready)

    def _check_ready(self) -> None:
        if self._reactant_side.all_filled and self._product_side.all_filled:
            self.molecules_ready.emit(
                self._reactant_side.molecules,
                self._product_side.molecules,
            )

    @property
    def reactant(self) -> Optional[Molecule]:
        mols = self._reactant_side.molecules
        return mols[0] if mols else None

    @property
    def product(self) -> Optional[Molecule]:
        mols = self._product_side.molecules
        return mols[0] if mols else None

    @property
    def reactants(self) -> List[Molecule]:
        return self._reactant_side.molecules

    @property
    def products(self) -> List[Molecule]:
        return self._product_side.molecules
