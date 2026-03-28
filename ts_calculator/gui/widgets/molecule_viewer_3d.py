"""Read-only 3D molecule viewer using 3Dmol.js in QWebEngineView."""
from __future__ import annotations
from pathlib import Path
from typing import Optional

from PyQt6.QtCore import QUrl
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtGui import QFont

from domain.models import Molecule

_HTML_PATH = Path(__file__).parent.parent / "resources" / "3dmol_viewer.html"

try:
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    from PyQt6.QtWebEngineCore import QWebEngineSettings
    _HAS_WEBENGINE = True
except ImportError:
    _HAS_WEBENGINE = False


class MoleculeViewer3D(QWidget):
    """Read-only 3D molecular structure viewer.

    Displays a Molecule using 3Dmol.js.  No editing capability.
    Falls back to a text label when QWebEngine is unavailable.
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._molecule: Optional[Molecule] = None
        self._web: Optional[QWebEngineView] = None
        self._pending_mol: Optional[Molecule] = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        if _HAS_WEBENGINE and _HTML_PATH.exists():
            try:
                self._web = QWebEngineView(self)
                self._web.settings().setAttribute(
                    QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True
                )
                self._web.settings().setAttribute(
                    QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True
                )
                self._web.loadFinished.connect(self._on_load_finished)
                self._web.load(QUrl.fromLocalFile(str(_HTML_PATH.resolve())))
                layout.addWidget(self._web)
            except Exception:
                self._web = None

        if self._web is None:
            self._fallback = QLabel("3D表示は利用できません")
            self._fallback.setFont(QFont("Consolas", 10))
            self._fallback.setStyleSheet(
                "background: #1e1e2e; color: #a6e3a1; padding: 8px;"
            )
            self._fallback.setWordWrap(True)
            layout.addWidget(self._fallback)

    def _on_load_finished(self, ok: bool) -> None:
        if not ok:
            return
        if self._pending_mol:
            self._push_xyz(self._pending_mol)
            self._pending_mol = None

    def set_molecule(self, molecule: Molecule) -> None:
        """Display a single molecule in the 3D viewer."""
        self.set_molecules([molecule])

    def set_molecules(self, molecules: list[Molecule]) -> None:
        """Display one or more molecules in the 3D viewer.

        All molecules are merged into a single XYZ block so they
        appear together in the same scene.
        """
        self._molecule = molecules[0] if molecules else None
        if not molecules:
            self.clear()
            return

        # Merge all molecules into one XYZ string
        merged_xyz = self._merge_xyz(molecules)

        if self._web is not None:
            self._push_xyz_str(merged_xyz)
        elif hasattr(self, "_fallback"):
            self._fallback.setText(merged_xyz)

    @staticmethod
    def _merge_xyz(molecules: list[Molecule]) -> str:
        """Merge multiple Molecule objects into one XYZ string.

        Each fragment is offset along the X-axis so they don't overlap.
        The gap between fragments is based on each molecule's bounding box.
        """
        from domain.models.molecule import Atom

        if len(molecules) == 1:
            return molecules[0].to_xyz_string()

        all_atoms: list[Atom] = []
        x_cursor = 0.0
        GAP = 2.0  # Angstrom gap between fragments

        for mol in molecules:
            if not mol.atoms:
                continue
            # Bounding box of this fragment
            xs = [a.x for a in mol.atoms]
            ys = [a.y for a in mol.atoms]
            zs = [a.z for a in mol.atoms]
            min_x, max_x = min(xs), max(xs)
            # Shift so the fragment's left edge starts at x_cursor
            offset_x = x_cursor - min_x
            for a in mol.atoms:
                all_atoms.append(Atom(
                    symbol=a.symbol,
                    x=a.x + offset_x,
                    y=a.y,
                    z=a.z,
                ))
            x_cursor = max_x + offset_x + GAP

        n = len(all_atoms)
        lines = [str(n), f"{len(molecules)} molecule(s)"]
        for a in all_atoms:
            lines.append(f"{a.symbol}  {a.x:.8f}  {a.y:.8f}  {a.z:.8f}")
        return "\n".join(lines) + "\n"

    def _push_xyz(self, molecule: Molecule) -> None:
        self._push_xyz_str(molecule.to_xyz_string())

    def _push_xyz_str(self, xyz: str) -> None:
        escaped = (
            xyz
            .replace("\\", "\\\\")
            .replace("`", "\\`")
            .replace("\n", "\\n")
        )
        js = f"if(typeof loadXYZ==='function'){{loadXYZ(`{escaped}`);}};"
        self._web.page().runJavaScript(js)

    def get_molecule(self) -> Optional[Molecule]:
        return self._molecule

    def clear(self) -> None:
        self._molecule = None
        if self._web is not None:
            self._web.page().runJavaScript("if(typeof loadXYZ==='function'){loadXYZ('');}")
        elif hasattr(self, "_fallback"):
            self._fallback.setText("")
