import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QDialog, QMessageBox

import config
from ui.cliente.login_dialog import LoginDialog
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

    # 1) el empleado se identifica antes de poder tomar pedidos
    login = LoginDialog(kiosk=config.KIOSK_FULLSCREEN)
    if config.KIOSK_FULLSCREEN:
        login.setWindowFlag(Qt.FramelessWindowHint)
        login.showFullScreen()
    if login.exec() != QDialog.Accepted or not login.employee:
        return 0

    # 2) kiosco de pedidos
    window = ClientWindow()
    window.employee = login.employee
    if config.KIOSK_FULLSCREEN:
        window.showFullScreen()
    else:
        window.resize(800, 480)          # pantalla táctil oficial de 7" de Raspberry Pi
        window.showMaximized()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
