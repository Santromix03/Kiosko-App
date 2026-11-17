"""Pruebas de integración con Supabase falso (RPC my_role/start_shift/end_shift)."""
import sys

from PySide6.QtWidgets import QApplication, QDialog, QPushButton, QWidget
from PySide6.QtCore import Qt, QTimer
from PySide6.QtTest import QTest

import config
import services.auth_service as auth
import services.shift_service as shift_service

# ---------------------------------------------------------------- fakes ----
calls = []


class FakeUser:
    def __init__(self, uid="u-123", email="empleado@gmail.com"):
        self.id, self.email, self.user_metadata = uid, email, {"full_name": "Meta"}


class FakeSession:
    def __init__(self, user=None):
        self.user = user or FakeUser()


class FakeAuth:
    def sign_in_with_password(self, creds):
        calls.append(("auth.sign_in", creds["email"]))
        return FakeSession()

    def sign_out(self):
        calls.append(("auth.sign_out",))


class FakeProfile:
    def select(self, s):
        return self

    def eq(self, c, v):
        return self

    def limit(self, n):
        return self

    def execute(self):
        calls.append(("employees.select",))
        class R:
            data = [{"full_name": "Andrés Gómez", "role": "empleado", "active": True}]
        return R()


class FakeClient:
    def __init__(self, role="employee"):
        self.auth = FakeAuth()
        self._role = role

    def rpc(self, name):
        calls.append(("rpc", name))
        class R:
            data = self._role if name == "my_role" else [{"id": 5, "employee_id": "u-123"}]
            def execute(self):
                return self
        return R()

    def table(self, name):
        assert name == "employees", name
        return FakeProfile()


# (sin QApplication aquí: los tests 1-5 no tocan UI y el test 6 crea la suya)

# ---- 1) login empleado activo ----
calls.clear()
auth.get_client = lambda: FakeClient("employee")
r = auth.sign_in("empleado@gmail.com", "empleado 123")
print("1) empleado activo:", r)

# ---- 2) login admin (permitido en el kiosco) ----
calls.clear()
auth.get_client = lambda: FakeClient("admin")
r = auth.sign_in("admin@gmail.com", "admin 12345")
print("2) admin:", r["rol"], "-", r["name"])

# ---- 3) empleado desactivado ----
calls.clear()
auth.get_client = lambda: FakeClient("inactive")
try:
    auth.sign_in("empleado@gmail.com", "x")
except ValueError as e:
    print("3) desactivado ->", e, "| sign_out llamado:", any(c[0] == "auth.sign_out" for c in calls))

# ---- 4) cuenta sin acceso ----
calls.clear()
auth.get_client = lambda: FakeClient(None)
try:
    auth.sign_in("empleado@gmail.com", "x")
except ValueError as e:
    print("4) sin acceso ->", e)

# ---- 5) turnos por RPC ----
calls.clear()
shift_service.get_client = lambda: FakeClient("employee")
s = shift_service.start_shift()
print("5) start_shift rpc:", calls[:2], "->", s)
shift_service.end_shift()
print("   end_shift rpc:", [c for c in calls if c[0] == "rpc"])

# ---- 6) ciclo completo de la app (login -> turno abierto -> salir -> cerrado) ----
import main_cliente

class FakeLogin(QWidget):
    employee = {"id": "u-123", "email": "empleado@gmail.com", "rol": "empleado", "name": "Andrés"}
    def exec(self):
        return QDialog.Accepted

main_cliente.LoginDialog = lambda **k: FakeLogin()
main_cliente.ClientWindow = QWidget
client = FakeClient("employee")
shift_service.get_client = lambda: client
auth.get_client = lambda: client

config.KIOSK_FULLSCREEN = False
config.SUPABASE_URL, config.SUPABASE_ANON_KEY = "x", "y"

calls.clear()
orig_exec = QApplication.exec
def fake_exec():
    QTimer.singleShot(1500, QApplication.instance().quit)
    return orig_exec()
QApplication.exec = staticmethod(fake_exec)
rc = main_cliente.main()
QApplication.exec = orig_exec

rpcs = [c[1] for c in calls if c[0] == "rpc"]
ok = "start_shift" in rpcs and "end_shift" in rpcs
print("6) ciclo completo:", rpcs, "->", "OK" if ok and rc == 0 else "FALLO")
