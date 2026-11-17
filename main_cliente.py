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

    # sesiones repetibles: la X del kiosco vuelve al login, y "Salir del
    # kiosco" (en el login) cierra la app. Cada empleado tiene su turno.
    while True:
        login = LoginDialog(kiosk=config.KIOSK_FULLSCREEN)
        if config.KIOSK_FULLSCREEN:
            login.setWindowFlag(Qt.FramelessWindowHint)
            login.showFullScreen()
        if login.exec() != QDialog.Accepted or not login.employee:
            return 0
        if not _correr_sesion(app, login.employee):
            return 0


def _correr_sesion(app: QApplication, employee: dict) -> bool:
    """Corre el kiosco para un empleado. Devuelve True si hay que volver al login.

    Abre el turno del empleado al entrar (mismos RPC que el panel web,
    «Roles y turnos» → «En turno ahora») y lo cierra al salir.
    """
    window = ClientWindow()
    window.employee = employee
    if config.KIOSK_FULLSCREEN:
        window.showFullScreen()
    else:
        window.resize(800, 480)          # pantalla táctil oficial de 7" de Raspberry Pi
        window.showMaximized()

    shift = {}

    def on_shift_open(_shift):
        shift["open"] = True

    def on_shift_fail(_message):
        pass   # ya quedó registrado en kiosko.log; no molesta al kiosco

    run_async(shift_service.start_shift, on_shift_open, on_shift_fail)

    def close_shift():
        if not shift.get("open"):
            return
        shift["open"] = False            # evita el doble cierre
        # en otro hilo, pero esperando hasta 3s: al apagar no debe colgar la Pi
        t = threading.Thread(target=shift_service.end_shift, daemon=True)
        t.start()
        t.join(timeout=3.0)

    app.aboutToQuit.connect(close_shift)

    volver = {"flag": False}

    def volver_al_login():
        volver["flag"] = True
        app.quit()                       # termina el ciclo de eventos de la sesión

    window.exit_requested.connect(volver_al_login)

    try:
        app.exec()
    finally:
        try:
            app.aboutToQuit.disconnect(close_shift)
        except Exception:
            pass
        close_shift()                    # por si la salida no pasó por aboutToQuit
        window.close()
    return volver["flag"]


if __name__ == "__main__":
    sys.exit(main())
