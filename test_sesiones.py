"""Prueba de sesiones repetibles: X del kiosco -> login; Salir -> fin de app."""
import sys

from PySide6.QtWidgets import QApplication, QDialog, QWidget
from PySide6.QtCore import QTimer

import config
import services.shift_service as shift_service
from ui.cliente.main_window import ClientWindow

# ---- supabase falso para los turnos ----
calls = []


class R:
    def __init__(self, data):
        self.data = data

    def execute(self):
        return self


class FakeClient:
    def rpc(self, name):
        calls.append(("rpc", name))
        return R([{"id": 5}] if name == "start_shift" else [])


shift_service.get_client = lambda: FakeClient()

config.KIOSK_FULLSCREEN = False
config.SUPABASE_URL, config.SUPABASE_ANON_KEY = "x", "y"

import main_cliente

# ---- ventana real del kiosco, pero se pulsa la X sola a los 800ms ----
RealWindow = ClientWindow


class AutoExitWindow(RealWindow):
    def __init__(self):
        super().__init__()
        QTimer.singleShot(800, self.btn_exit.click)


main_cliente.ClientWindow = AutoExitWindow

# ---- login falso con guion: 1) entra, 2) "Salir del kiosco" ----
script = {"n": 0}


class FakeLogin(QWidget):
    employee = None

    def exec(self):
        script["n"] += 1
        if script["n"] == 1:
            FakeLogin.employee = {"id": "u-123", "email": "e@x.com", "rol": "empleado", "name": "Andrés"}
            return QDialog.Accepted
        FakeLogin.employee = None
        return QDialog.Rejected          # simula "Salir del kiosco"


main_cliente.LoginDialog = lambda **k: FakeLogin()

rc = main_cliente.main()
rpcs = [c[1] for c in calls if c[0] == "rpc"]
print("exit code:", rc, "| logins:", script["n"], "| rpcs:", rpcs)
ok = rc == 0 and script["n"] == 2 and "start_shift" in rpcs and "end_shift" in rpcs
print("FLUJO COMPLETO OK" if ok else "FALLO")

# ---- captura del kiosco con la X ----
app = QApplication(sys.argv)
win = ClientWindow()
win.resize(800, 480)
win.show()


def snap():
    win.grab().save("preview_kiosco_x.png")
    app.quit()


QTimer.singleShot(1500, snap)
app.exec()
