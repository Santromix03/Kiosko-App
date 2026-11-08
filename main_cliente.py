import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from ui.cliente.main_window import ClientWindow
from ui.common.assets import load_fonts


def main():
    app = QApplication(sys.argv)
    load_fonts()
    qss = Path(__file__).parent / "ui" / "common" / "styles.qss"
    app.setStyleSheet(qss.read_text(encoding="utf-8"))

    window = ClientWindow()
    window.resize(1280, 760)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()