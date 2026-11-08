from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QPushButton, QScrollArea, QVBoxLayout, QWidget,
)

from core.cart import Cart
from ui.common.widgets import format_price
from PySide6.QtCore import Qt, QTimer, Signal




class CartPanel(QFrame):
    confirm_requested = Signal()

    def __init__(self, cart: Cart):
        super().__init__()
        self.cart = cart
        self.setObjectName("CartPanel")
        self.setFixedWidth(340)                    
        title = QLabel("TU SELECCIÓN")               
        self.clear_btn = QPushButton("Vaciar pedido")

        title = QLabel("Tu pedido")
        title.setObjectName("CartTitle")
        title.setAlignment(Qt.AlignCenter)

        self.list_host = QWidget()
        self.list_layout = QVBoxLayout(self.list_host)
        self.list_layout.setAlignment(Qt.AlignTop)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        scroll.setWidget(self.list_host)

        self.note_label = QLabel()
        self._note_timer = QTimer(self)
        self._note_timer.setSingleShot(True)
        self._note_timer.timeout.connect(lambda: self.note_label.setText(""))
        self.note_label.setObjectName("CartNote")
        self.note_label.setAlignment(Qt.AlignCenter)
        self.note_label.setWordWrap(True)

        self.total_label = QLabel()
        self.total_label.setObjectName("CartTotal")

        self.confirm_btn = QPushButton("Confirmar pedido")
        self.confirm_btn.setObjectName("ConfirmButton")
        self.confirm_btn.setMinimumHeight(64)
        self.confirm_btn.clicked.connect(self.confirm_requested.emit)

        self.clear_btn = QPushButton("Vaciar")
        self.clear_btn.setObjectName("ClearButton")
        self.clear_btn.clicked.connect(self._clear)

        layout = QVBoxLayout(self)
        layout.addWidget(title)
        layout.addWidget(scroll, 1)
        layout.addWidget(self.total_label)
        layout.addWidget(self.note_label)
        layout.addWidget(self.confirm_btn)
        layout.addWidget(self.clear_btn)

        self.refresh()

    def _row(self, item):
        row = QWidget()
        h = QHBoxLayout(row)
        h.setContentsMargins(0, 0, 0, 0)

        text = item.product.name
        if item.addons:
            text += "\n+ " + ", ".join(a.name for a in item.addons)
        text += f"\n{format_price(item.subtotal)}"
        name = QLabel(text)
        name.setWordWrap(True)

        minus = QPushButton("−")
        minus.setObjectName("QtyButton")
        minus.setFixedSize(44, 44)
        minus.clicked.connect(lambda: self._minus(item.key))

        qty = QLabel(str(item.quantity))
        qty.setAlignment(Qt.AlignCenter)
        qty.setMinimumWidth(28)

        plus = QPushButton("+")
        plus.setObjectName("QtyButton")
        plus.setFixedSize(44, 44)
        plus.clicked.connect(lambda: self._plus(item))

        h.addWidget(name, 1)
        h.addWidget(minus)
        h.addWidget(qty)
        h.addWidget(plus)
        return row

    def _plus(self, item):
        reason = self.cart.blocked_reason(item.product, item.addons)
        if reason:
            self.flash(reason)
            return
        self.cart.add(item.product, item.addons)
        self.refresh()

    def _minus(self, key):
        self.cart.remove_one(key)
        self.refresh()

    def _clear(self):
        self.cart.clear()
        self.refresh()

    def set_busy(self, busy: bool):
        self.confirm_btn.setText("Enviando…" if busy else "Confirmar pedido")
        self.confirm_btn.setEnabled(not busy and not self.cart.is_empty)

    def refresh(self):
        while self.list_layout.count():
            w = self.list_layout.takeAt(0).widget()
            if w:
                w.deleteLater()

        if self.cart.is_empty:
            empty = QLabel("Toca un producto\npara agregarlo")
            empty.setAlignment(Qt.AlignCenter)
            self.list_layout.addWidget(empty)
        for item in self.cart.items:
            self.list_layout.addWidget(self._row(item))

        self.total_label.setText(f"Total: {format_price(self.cart.total)}")
        self.confirm_btn.setEnabled(not self.cart.is_empty)
        self.clear_btn.setEnabled(not self.cart.is_empty)

    def flash(self, text: str):
        self.note_label.setText(text)
        self._note_timer.start(4000)   

