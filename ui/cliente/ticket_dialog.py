from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QDialog, QLabel, QPushButton, QVBoxLayout


class TicketDialog(QDialog):
    def __init__(self, ticket_number, printed=True, seconds=15, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Pedido recibido")
        self.setModal(True)
        self.setMinimumWidth(520)
        self._left = seconds

        title = QLabel("¡Pedido recibido!")
        title.setObjectName("TicketTitle")
        title.setAlignment(Qt.AlignCenter)

        number = QLabel(f"#{ticket_number}")
        number.setObjectName("TicketNumber")
        number.setAlignment(Qt.AlignCenter)

        msg = QLabel(
            "Toma tu ticket y paga en caja"
            if printed
            else "No se pudo imprimir. Anota tu número y díselo al cajero"
        )
        msg.setWordWrap(True)
        msg.setAlignment(Qt.AlignCenter)

        self.btn = QPushButton()
        self.btn.setObjectName("ConfirmButton")
        self.btn.setMinimumHeight(60)
        self.btn.clicked.connect(self.accept)

        layout = QVBoxLayout(self)
        layout.addWidget(title)
        layout.addWidget(number)
        layout.addWidget(msg)
        layout.addWidget(self.btn)

        self._update_button()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(1000)

    def _update_button(self):
        self.btn.setText(f"Listo ({self._left})")

    def _tick(self):
        self._left -= 1
        if self._left <= 0:
            self.accept()
        else:
            self._update_button()