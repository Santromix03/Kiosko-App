import sys

from PySide6.QtWidgets import QApplication, QMessageBox

import config
from ui.cliente.main_window import ClientWindow
from ui.common.assets import load_fonts


def main() -> int:
    app = QApplication(sys.argv)
    load_fonts()

    qss = config.RESOURCE_DIR / "ui" / "common" / "styles.qss"
    app.setStyleSheet(qss.read_text(encoding="utf-8"))

    if not (config.SUPABASE_URL and config.SUPABASE_ANON_KEY):
        QMessageBox.critical(
            None,
            "Falta la configuración",
            "No se encontró el archivo .env con SUPABASE_URL y SUPABASE_ANON_KEY.\n\n"
            f"Créalo en esta carpeta (hay una plantilla .env.example):\n{config.BASE_DIR}",
        )
        return 1

    window = ClientWindow()
    window.resize(1280, 760)
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())