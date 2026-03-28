"""3D molecule editor with mouse interaction. Falls back to text if WebEngine unavailable."""
from __future__ import annotations
from pathlib import Path
from typing import Optional

from PyQt6.QtCore import pyqtSignal, pyqtSlot, QObject, QUrl
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLabel
from PyQt6.QtGui import QFont

from domain.models import Molecule

_HTML_PATH = Path(__file__).parent.parent / "resources" / "3dmol_editor.html"

try:
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    from PyQt6.QtWebEngineCore import QWebEngineSettings
    from PyQt6.QtWebChannel import QWebChannel
    _HAS_WEBENGINE = True
except ImportError:
    _HAS_WEBENGINE = False


class _JsBridge(QObject):
    """Python object exposed to JavaScript via QWebChannel."""
    molecule_changed = pyqtSignal(str)  # XYZ string

    @pyqtSlot(str)
    def onMoleculeChanged(self, xyz: str) -> None:
        self.molecule_changed.emit(xyz)


class MoleculeEditor3D(QWidget):
    """Interactive 3D molecular editor.

    Mouse controls:
    - 配置モード: left-click to place atoms; click near existing atom to auto-bond
    - 結合モード: click two atoms to create/edit bond
    - 移動モード: drag atoms
    - 削除モード: click atom to remove
    """
    molecule_edited = pyqtSignal(object)  # Molecule

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._molecule: Optional[Molecule] = None
        self._web = None
        self._bridge: Optional[_JsBridge] = None

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

                # Setup QWebChannel for JS ↔ Python communication
                self._bridge = _JsBridge(self)
                self._bridge.molecule_changed.connect(self._on_js_molecule_changed)
                channel = QWebChannel(self._web.page())
                channel.registerObject("pyBridge", self._bridge)
                self._web.page().setWebChannel(channel)

                layout.addWidget(self._web)

                # Load HTML with qwebchannel.js injection
                self._web.loadFinished.connect(self._on_load_finished)
                self._web.load(QUrl.fromLocalFile(str(_HTML_PATH.resolve())))
            except Exception:
                self._web = None

        if self._web is None:
            self._text = QTextEdit(self)
            self._text.setReadOnly(True)
            self._text.setFont(QFont("Consolas", 10))
            self._text.setStyleSheet("background: #1e1e2e; color: #a6e3a1;")
            self._text.setPlaceholderText("分子構造がここに表示されます")
            layout.addWidget(self._text)

    def _on_load_finished(self, ok: bool) -> None:
        if not ok:
            self._switch_to_fallback()
            return
        # Inject QWebChannel setup into the page
        setup_js = """
        new QWebChannel(qt.webChannelTransport, function(channel) {
            window.pyBridge = channel.objects.pyBridge;
        });
        """
        self._web.page().runJavaScript(setup_js)
        if self._molecule:
            self._push_molecule(self._molecule)

    def _switch_to_fallback(self) -> None:
        if self._web is not None:
            lay = self.layout()
            lay.removeWidget(self._web)
            self._web.deleteLater()
            self._web = None
            self._text = QTextEdit(self)
            self._text.setReadOnly(True)
            self._text.setFont(QFont("Consolas", 10))
            self._text.setStyleSheet("background: #1e1e2e; color: #a6e3a1;")
            lay.addWidget(self._text)
            if self._molecule:
                self._text.setPlainText(self._molecule.to_xyz_string())

    @pyqtSlot(str)
    def _on_js_molecule_changed(self, xyz: str) -> None:
        """Called when user edits molecule in the 3D editor."""
        if not xyz.strip():
            self._molecule = None
            return
        try:
            self._molecule = Molecule.from_xyz_string(xyz, name="edited")
            self.molecule_edited.emit(self._molecule)
        except Exception:
            pass

    def set_molecule(self, molecule: Molecule) -> None:
        self._molecule = molecule
        if self._web is not None:
            self._push_molecule(molecule)
        elif hasattr(self, "_text"):
            self._text.setPlainText(molecule.to_xyz_string())

    def _push_molecule(self, molecule: Molecule) -> None:
        xyz = molecule.to_xyz_string().replace("\\", "\\\\").replace("`", "\\`").replace("\n", "\\n")
        js = f"loadXYZ(`{xyz}`);"
        self._web.page().runJavaScript(js)

    def get_molecule(self) -> Optional[Molecule]:
        return self._molecule

    def set_2d_mode(self, enabled: bool) -> None:
        """Switch between 2D (top-down, locked Z) and 3D editing."""
        if self._web is not None:
            js = f"set2DMode({'true' if enabled else 'false'});"
            self._web.page().runJavaScript(js)

    def clear(self) -> None:
        self._molecule = None
        if self._web is not None:
            self._web.page().runJavaScript("loadXYZ('');")
        elif hasattr(self, "_text"):
            self._text.clear()
