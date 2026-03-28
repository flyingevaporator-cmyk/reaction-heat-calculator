"""Ketcher 2D molecular editor widget embedded in QWebEngineView."""
from __future__ import annotations
from pathlib import Path
from typing import Optional

from PyQt6.QtCore import pyqtSignal, QUrl, QTimer
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtGui import QFont

_KETCHER_INDEX = (
    Path(__file__).parent.parent / "resources" / "ketcher" / "standalone" / "index.html"
)

try:
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    from PyQt6.QtWebEngineCore import QWebEngineSettings
    _HAS_WEBENGINE = True
except ImportError:
    _HAS_WEBENGINE = False


class KetcherEditor(QWidget):
    """2D molecular structure editor using Ketcher (EPAM, Apache-2.0).

    Embeds the Ketcher standalone build in a QWebEngineView.
    Emits ``molfile_exported`` when the user requests a Molfile export.

    Export strategy: Ketcher's getMolfile() returns a Promise.
    QWebEngineView.runJavaScript cannot resolve JS Promises directly.
    So we store the result in a global variable via .then(), then read
    it on the next tick with a plain (non-async) runJavaScript call.
    """

    molfile_exported = pyqtSignal(str)  # V2000 Molfile text

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._web: Optional[QWebEngineView] = None
        self._ready = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        if _HAS_WEBENGINE and _KETCHER_INDEX.exists():
            try:
                self._web = QWebEngineView(self)
                self._web.settings().setAttribute(
                    QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True
                )
                self._web.settings().setAttribute(
                    QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True
                )
                self._web.loadFinished.connect(self._on_load_finished)
                self._web.load(QUrl.fromLocalFile(str(_KETCHER_INDEX.resolve())))
                layout.addWidget(self._web)
            except Exception:
                self._web = None

        if self._web is None:
            label = QLabel(
                "Ketcher 2Dエディタを利用するにはQtWebEngineが必要です。\n"
                "ファイル読み込みで分子を入力してください。"
            )
            label.setFont(QFont("Meiryo", 10))
            label.setStyleSheet("background: #1e1e2e; color: #f38ba8; padding: 16px;")
            label.setWordWrap(True)
            layout.addWidget(label)

    def _on_load_finished(self, ok: bool) -> None:
        if ok:
            # Inject helper: stores Molfile in a global so Python can read it
            helper_js = """
            window._molfileResult = null;
            window._molfileError = null;
            window.exportMolfile = function() {
                window._molfileResult = null;
                window._molfileError = null;
                if (!window.ketcher) {
                    window._molfileError = 'Ketcher not ready';
                    return;
                }
                window.ketcher.getMolfile('v2000').then(function(mol) {
                    window._molfileResult = mol;
                }).catch(function(e) {
                    window._molfileError = e.toString();
                });
            };
            """
            self._web.page().runJavaScript(helper_js)
            self._poll_ready()

    def _poll_ready(self, attempts: int = 0) -> None:
        """Wait until window.ketcher is available (up to ~10 seconds)."""
        if attempts > 100:
            self._ready = True
            return
        js = "typeof window.ketcher !== 'undefined' && window.ketcher !== null"
        self._web.page().runJavaScript(js, lambda ok: self._on_ready_check(ok, attempts))

    def _on_ready_check(self, ready: bool, attempts: int) -> None:
        if ready:
            self._ready = True
        else:
            QTimer.singleShot(100, lambda: self._poll_ready(attempts + 1))

    # ----- Public API -----

    def export_molfile(self) -> None:
        """Request Molfile export from Ketcher. Result emitted via molfile_exported signal."""
        if not self._web or not self._ready:
            return
        # Step 1: trigger the async export (stores result in window._molfileResult)
        self._web.page().runJavaScript("window.exportMolfile();")
        # Step 2: poll for result after a short delay
        self._poll_molfile_result(attempts=0)

    def _poll_molfile_result(self, attempts: int) -> None:
        """Poll for the Molfile result (async getMolfile may take a moment)."""
        if attempts > 20:  # give up after ~2 seconds
            return

        def on_result(val):
            if val and isinstance(val, str) and val.strip():
                self.molfile_exported.emit(val)
            else:
                # Not ready yet, try again
                QTimer.singleShot(100, lambda: self._poll_molfile_result(attempts + 1))

        self._web.page().runJavaScript("window._molfileResult", on_result)

    def set_molfile(self, molfile: str) -> None:
        """Load a Molfile into the Ketcher editor."""
        if not self._web or not self._ready:
            return
        escaped = molfile.replace("\\", "\\\\").replace("`", "\\`").replace("\n", "\\n")
        js = f"window.ketcher.setMolecule(`{escaped}`);"
        self._web.page().runJavaScript(js)

    def is_available(self) -> bool:
        """Whether the Ketcher editor is ready."""
        return self._web is not None and self._ready
