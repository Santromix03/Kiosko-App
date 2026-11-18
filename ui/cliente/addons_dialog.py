from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox, QDialog, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QScrollArea, QVBoxLayout, QWidget,
)

from ui.common.touch_keyboard import TouchKeyboard
from ui.common.widgets import DragScroll, format_price

MAX_NOTE = 120


class NoteDialog(QDialog):
    """Observaciones del producto (opcional), escritas con el teclado táctil."""

    def __init__(self, note: str = "", parent=None):
        super().__init__(parent)
        self.setWindowTitle("Observaciones")
        self.setObjectName("NoteDialog")
        self.setModal(True)
        self.setFixedWidth(600)

        title = QLabel("Observaciones")
        title.setObjectName("AddonTitle")

        subtitle = QLabel("Opcional: lo que debe saber la cocina de este producto.")
        subtitle.setObjectName("AddonSub")
        subtitle.setWordWrap(True)

        self.edit = QLineEdit(note)
        self.edit.setObjectName("NoteInput")
        self.edit.setPlaceholderText("Ej: sin cebolla, bien cocida, sin salsa…")
        self.edit.setMaxLength(MAX_NOTE)
        self.edit.setClearButtonEnabled(True)
        self.edit.setMinimumHeight(44)

        clear = QPushButton("Borrar")
        clear.setObjectName("NoteClear")
        clear.setMinimumHeight(44)
        clear.clicked.connect(self.edit.clear)

        cancel = QPushButton("Cancelar")
        cancel.setObjectName("ClearButton")
        cancel.setMinimumHeight(44)
        cancel.clicked.connect(self.reject)

        ok = QPushButton("Listo")
        ok.setObjectName("ConfirmButton")
        ok.setMinimumHeight(44)
        ok.clicked.connect(self.accept)

        buttons = QHBoxLayout()
        buttons.setSpacing(8)
        buttons.addWidget(clear)
        buttons.addWidget(cancel)
        buttons.addWidget(ok, 1)

        self.keyboard = TouchKeyboard()
        self.keyboard.accepted.connect(self.accept)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(8)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(self.edit)
        layout.addLayout(buttons)
        layout.addWidget(self.keyboard)

        self.edit.setFocus()

    def text(self) -> str:
        return self.edit.text().strip()


class AddonsDialog(QDialog):
    """Pregunta qué adiciones quiere el cliente para un producto.

    También permite dejar una observación opcional (se imprime en el ticket).
    """

    def __init__(self, product, addons, left_by_id, parent=None, note: str = ""):
        super().__init__(parent)
        self.setWindowTitle("Adiciones")
        self.setObjectName("AddonsDialog")
        self.setModal(True)
        self.setFixedWidth(470)
        self.product = product
        self._rows = []
        self._note = (note or "").strip()

        title = QLabel(product.name)
        title.setObjectName("AddonTitle")
        title.setWordWrap(True)
        pending = [a for a in addons if left_by_id.get(a.id, 0) >= 1]
        if addons and not pending:
            subtitle_text = "Adiciones agotadas por ahora: puedes pedir el producto solo."
        elif addons:
            subtitle_text = "¿Quieres agregarle algo?"
        else:
            subtitle_text = "Sin adiciones para este producto"
        subtitle = QLabel(subtitle_text)
        subtitle.setObjectName("AddonSub")
        subtitle.setWordWrap(True)
        self.subtitle = subtitle

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(6)
        layout.addWidget(title)
        layout.addWidget(subtitle)

        if addons:
            host = QWidget()
            rows = QVBoxLayout(host)
            rows.setContentsMargins(0, 0, 0, 0)
            rows.setSpacing(2)
            rows.setAlignment(Qt.AlignTop)

            self.scroll = DragScroll(Qt.Vertical)
            self.scroll.setObjectName("AddonsScroll")
            self.scroll.setFrameShape(QScrollArea.NoFrame)
            self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            self.scroll.setWidgetResizable(True)
            self.scroll.setFixedHeight(200)
            self.scroll.setWidget(host)
            self.scroll.watch_host(host)

            for addon in addons:
                sold_out = left_by_id.get(addon.id, 0) < 1
                text = (f"{addon.name}  ·  Agotado" if sold_out
                        else f"{addon.name}  ·  +{format_price(addon.price)}")
                check = QCheckBox(text)
                check.setObjectName("AddonCheck")
                check.setEnabled(not sold_out)
                check.setMinimumHeight(36)
                check.toggled.connect(self._update_total)
                self.scroll.watch(check)
                rows.addWidget(check)
                self._rows.append((check, addon))
            layout.addWidget(self.scroll)
        else:
            self.scroll = None

        self.note_btn = QPushButton()
        self.note_btn.setObjectName("NoteButton")
        self.note_btn.setMinimumHeight(38)
        self.note_btn.setCursor(Qt.PointingHandCursor)
        self.note_btn.clicked.connect(self._edit_note)
        self._update_note_button()
        layout.addWidget(self.note_btn)

        self.total_label = QLabel()
        self.total_label.setObjectName("AddonTotal")
        self.total_label.setAlignment(Qt.AlignRight)
        layout.addWidget(self.total_label)

        buttons = QHBoxLayout()
        buttons.setSpacing(8)
        cancel = QPushButton("Cancelar")
        cancel.setObjectName("ClearButton")
        cancel.setMinimumHeight(44)
        cancel.clicked.connect(self.reject)
        ok = QPushButton("Agregar al pedido")
        ok.setObjectName("ConfirmButton")
        ok.setMinimumHeight(44)
        ok.clicked.connect(self.accept)
        buttons.addWidget(cancel)
        buttons.addWidget(ok, 1)
        layout.addLayout(buttons)

        self._update_total()

    def selected_addons(self) -> tuple:
        return tuple(a for check, a in self._rows if check.isChecked())

    def selected_note(self) -> str:
        return self._note

    def _edit_note(self):
        dialog = NoteDialog(self._note, self)
        if dialog.exec():
            self._note = dialog.text()
            self._update_note_button()

    def _update_note_button(self):
        if self._note:
            short = self._note if len(self._note) <= 44 else self._note[:43] + "…"
            self.note_btn.setText("Nota: " + short)
        else:
            self.note_btn.setText("Añadir observación (opcional)")

    def _update_total(self):
        total = self.product.price + sum(a.price for a in self.selected_addons())
        self.total_label.setText(f"Total: {format_price(total)}")
