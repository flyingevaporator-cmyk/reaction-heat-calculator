"""Application entry point."""
import sys
from pathlib import Path

# Ensure ts_calculator root is on sys.path
sys.path.insert(0, str(Path(__file__).parent))

# QtWebEngineWidgets MUST be imported before QApplication is created
try:
    from PyQt6.QtWebEngineWidgets import QWebEngineView  # noqa: F401
except ImportError:
    pass

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from gui.main_window import MainWindow


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("TS Calculator")
    app.setOrganizationName("Internal")

    # Dark-ish palette is handled via HTML/CSS in widgets;
    # use Fusion style for native widgets
    app.setStyle("Fusion")

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
