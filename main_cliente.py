import os
import sys
import threading

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QDialog, QMessageBox

import config
from core.workers import run_async
from services import shift_service
from ui.cliente.login_dialog import LoginDialog
from ui.cliente.main_window import ClientWindow
from ui.common.assets import load_fonts


def main() -> int:
    # La app trae su propio teclado táctil (el login lo usa). Si el entorno
    # tiene configurado un IME de Qt (p.ej. QT_IM_MODULE=qtvirtualkeyboard
    # instalado a mano o por una versión anterior), se desactiva: así ningún
    # teclado del sistema asoma en los diálogos de la Pi.
    os.environ.pop("QT_IM_MODULE", None)
    for var in [k for k in os.environ if k.startswith("QT_VIRTUALKEYBOARD")]:
        os.environ.pop(var, None)

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

    employee = login.employee

    # 2) kiosco de pedidos
    window = ClientWindow()
    window.employee = employee
    if config.KIOSK_FULLSCREEN:
        window.showFullScreen()
    else:
        window.resize(800, 480)          # pantalla táctil oficial de 7" de Raspberry Pi
        window.showMaximized()

    # 3) turno del empleado: se abre al entrar y se cierra al salir de la app.
    #    Mismos RPC que el panel web («Roles y turnos» → «En turno ahora»).
    shift = {}

    def on_shift_open(_shift):
        shift["open"] = True

    def on_shift_fail(_message):
        pass   # ya quedó registrado en kiosko.log; no molesta al kiosco

    run_async(shift_service.start_shift, on_shift_open, on_shift_fail)

    def close_shift():
        if not shift.get("open"):
            return
        # en otro hilo, pero esperando hasta 3s: al apagar no debe colgar la Pi
        t = threading.Thread(target=shift_service.end_shift, daemon=True)
        t.start()
        t.join(timeout=3.0)

    app.aboutToQuit.connect(close_shift)

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
