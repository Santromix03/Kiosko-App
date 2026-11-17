from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QApplication, QDialog, QFrame, QLabel, QLineEdit, QPushButton, QVBoxLayout,
)

import config
from core.workers import run_async
from services import auth_service


class LoginDialog(QDialog):
    """Pantalla de entrada: un empleado debe identificarse antes de tomar pedidos."""

    def __init__(self, parent=None, kiosk: bool = False):
        super().__init__(parent)
        self.setObjectName("LoginDialog")
        self.setWindowTitle("Acceso de empleado")
        self.employee = None
        self._busy = False
        self._kiosk = kiosk

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)   # fullscreen: el fondo completo es de la app
        root.setSpacing(0)
        root.addStretch(1)

        # --- tarjeta compacta centrada (no estira los campos) ---
        card = QFrame()
        card.setObjectName("LoginCard")
        card.setFixedWidth(340)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(6)

        logo_path = config.RESOURCE_DIR / "assets" / "logo.png"
        if logo_path.exists():
            logo = QLabel()
            logo.setAlignment(Qt.AlignCenter)
            logo.setPixmap(QPixmap(str(logo_path)).scaled(
                40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            layout.addWidget(logo)

        title = QLabel(config.NOMBRE_LOCAL.upper())
        title.setObjectName("LoginTitle")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel("Acceso de empleado")
        subtitle.setObjectName("LoginSubtitle")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)
        layout.addSpacing(2)

        self.email = QLineEdit()
        self.email.setObjectName("LoginInput")
        self.email.setPlaceholderText("correo@ejemplo.com")
        self.email.setClearButtonEnabled(True)
        layout.addWidget(self.email)

        self.password = QLineEdit()
        self.password.setObjectName("LoginInput")
        self.password.setPlaceholderText("Contraseña")
        self.password.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password)
        self.password.returnPressed.connect(self._submit)
        self.email.returnPressed.connect(self.password.setFocus)

        self.error = QLabel()
        self.error.setObjectName("LoginError")
        self.error.setAlignment(Qt.AlignCenter)
        self.error.setWordWrap(True)
        self.error.hide()
        layout.addWidget(self.error)
        layout.addSpacing(2)

        self.btn = QPushButton("Entrar")
        self.btn.setObjectName("ConfirmButton")
        self.btn.setMinimumHeight(38)
        self.btn.clicked.connect(self._submit)
        layout.addWidget(self.btn)

        # salida: funciona igual en Windows y Linux (cierra el diálogo y la app)
        self.btn_quit = QPushButton("X  Salir del kiosco")
        self.btn_quit.setObjectName("LoginClose")
        self.btn_quit.setCursor(Qt.PointingHandCursor)
        self.btn_quit.clicked.connect(self._salir_del_kiosco)
        layout.addWidget(self.btn_quit)

        root.addWidget(card, 0, Qt.AlignHCenter)
        root.addStretch(1)

        # en modo kiosco: teclado táctil propio, siempre visible abajo
        if self._kiosk:
            from ui.common.touch_keyboard import TouchKeyboard
            self.keyboard = TouchKeyboard()
            self.keyboard.accepted.connect(self._submit)
            root.addWidget(self.keyboard)

        self.email.setFocus()

    def _salir_del_kiosco(self):
        """Cierra el diálogo y toda la app, igual en Windows y en Linux."""
        self.reject()
        app = QApplication.instance()
        if app is not None:
            app.quit()

    def _submit(self):
        if self._busy:
            return
        self._busy = True
        self.error.hide()
        self.setEnabled(False)
        self.btn.setText("Verificando…")
        run_async(auth_service.sign_in, self._on_ok, self._on_error,
                  self.email.text(), self.password.text())

    def _on_ok(self, employee):
        self.employee = employee
        self.accept()

    def _on_error(self, message):
        lines = [ln.strip() for ln in message.splitlines() if ln.strip()]
        msg = lines[-1] if lines else "No se pudo verificar"
        # el error llega como "ValueError: el mensaje": se quita el prefijo
        while ": " in msg and msg.split(": ", 1)[0].replace(".", "").isidentifier():
            msg = msg.split(": ", 1)[1]
        low = msg.lower()
        if "invalid login credentials" in low:
            msg = "Correo o contraseña incorrectos"
        elif "email not confirmed" in low:
            msg = "Este correo aún no está confirmado en el sistema"
        self.setEnabled(True)
        self._busy = False
        self.btn.setText("Entrar")
        self.password.setFocus()
        self.error.setText("⚠ " + msg)
        self.error.show()
