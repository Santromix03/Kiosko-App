from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QApplication, QGridLayout, QLineEdit, QPushButton, QWidget


class TouchKeyboard(QWidget):
    """Teclado en pantalla propio de la app: botones Qt, cero dependencias.

    Escribe sobre el QLineEdit que tenga el foco. Pensado para el kiosco
    táctil: teclas grandes, no roba el foco, y ✓ dispara `accepted`.
    """

    accepted = Signal()

    LETTER_ROWS = ("qwertyuiop", "asdfghjklñ", "zxcvbnm")

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("TouchKeyboard")
        self.setFocusPolicy(Qt.NoFocus)
        self._caps = False
        self._letter_keys = []

        g = QGridLayout(self)
        g.setContentsMargins(3, 3, 3, 3)
        g.setSpacing(3)
        for col in range(10):
            g.setColumnStretch(col, 1)

        # fila 1: números
        for i, ch in enumerate("1234567890"):
            g.addWidget(self._key(ch), 0, i)

        # filas de letras
        for r, row in enumerate(self.LETTER_ROWS, start=1):
            for i, ch in enumerate(row):
                b = self._key(ch)
                self._letter_keys.append((b, ch))
                g.addWidget(b, r, i)

        # fila 4: mayúsculas + zxcvbnm + , .
        g.addWidget(self._key("ABC", action=self._toggle_caps), 3, 0)
        for i, ch in enumerate("zxcvbnm"):
            b = self._key(ch)
            self._letter_keys.append((b, ch))
            g.addWidget(b, 3, i + 1)
        g.addWidget(self._key(","), 3, 8)
        g.addWidget(self._key("."), 3, 9)

        # fila 5: útiles para correos + espacio + borrar + listo
        g.addWidget(self._key("@", action=lambda: self._insert("@"), span=2), 4, 0)
        g.addWidget(self._key("-"), 4, 2)
        g.addWidget(self._key("_"), 4, 3)
        g.addWidget(self._key("."), 4, 4)
        g.addWidget(self._key("ESPACIO", action=lambda: self._insert(" "), span=3), 4, 5, 1, 3)
        g.addWidget(self._key("DEL", action=self._backspace), 4, 8)
        g.addWidget(self._key("OK", action=self.accepted.emit), 4, 9)

    # --- construcción ---
    def _key(self, text, action=None, span=1):
        b = QPushButton(text)
        b.setObjectName("KeyButton" if action is None else "KeyAction")
        b.setMinimumHeight(34)
        b.setFocusPolicy(Qt.NoFocus)
        b.setCursor(Qt.PointingHandCursor)
        if action is None:
            b.clicked.connect(lambda _=False, t=text: self._insert(t))
        else:
            b.clicked.connect(action)
        if span > 1:
            b.setProperty("span", span)
        return b

    # --- comportamiento ---
    def _target(self):
        w = QApplication.focusWidget()
        return w if isinstance(w, QLineEdit) else None

    def _insert(self, text):
        le = self._target()
        if le is None:
            return
        if self._caps and text.isalpha():
            text = text.upper()
        le.insert(text)

    def _backspace(self):
        le = self._target()
        if le is not None:
            le.backspace()

    def _toggle_caps(self):
        self._caps = not self._caps
        for b, ch in self._letter_keys:
            b.setText(ch.upper() if self._caps else ch)
