from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtWidgets import (
    QApplication, QDialog, QFrame, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QVBoxLayout, QWidget,
)

from core.cart import Cart
from ui.common.widgets import DragScroll, format_price


class CartDetailDialog(QDialog):
    """El pedido completo a pantalla completa, con su X para volver al menú."""

    changed = Signal()

    def __init__(self, cart: Cart, parent=None):
        super().__init__(parent)
        self.cart = cart
        self.setWindowTitle("Tu pedido")
        self.setObjectName("CartDetailDialog")
        self.setModal(True)
        self.setWindowFlag(Qt.FramelessWindowHint, True)
        screen = QApplication.primaryScreen()
        if screen is not None:
            self.setGeometry(screen.geometry())

        # --- cabecera con la X ---
        title = QLabel("TU PEDIDO")
        title.setObjectName("CartDetailTitle")
        subtitle = QLabel("Revisa con calma lo que estás ordenando.")
        subtitle.setObjectName("CartDetailSub")
        texts = QVBoxLayout()
        texts.setSpacing(0)
        texts.addWidget(title)
        texts.addWidget(subtitle)

        self.close_btn = QPushButton("X")
        self.close_btn.setObjectName("ExitButton")
        self.close_btn.setFixedSize(44, 44)
        self.close_btn.setCursor(Qt.PointingHandCursor)
        self.close_btn.setToolTip("Cerrar y volver al menú")
        self.close_btn.clicked.connect(self.reject)

        head = QHBoxLayout()
        head.setSpacing(10)
        head.addLayout(texts, 1)
        head.addWidget(self.close_btn, 0, Qt.AlignTop)

        # --- lista detallada ---
        self.list_host = QWidget()
        self.list_layout = QVBoxLayout(self.list_host)
        self.list_layout.setContentsMargins(0, 0, 0, 0)
        self.list_layout.setSpacing(8)
        self.list_layout.setAlignment(Qt.AlignTop)

        self.scroll = DragScroll(Qt.Vertical)
        self.scroll.setObjectName("CartDetailScroll")
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QScrollArea.NoFrame)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setWidget(self.list_host)
        self.scroll.watch_host(self.list_host)

        # --- total y volver ---
        self.status = QLabel("")
        self.status.setObjectName("CartNote")
        self.status.setAlignment(Qt.AlignCenter)
        self.status.setWordWrap(True)
        self._status_timer = QTimer(self)
        self._status_timer.setSingleShot(True)
        self._status_timer.timeout.connect(lambda: self.status.setText(""))

        total_caption = QLabel("Total")
        total_caption.setObjectName("CartDetailTotalLabel")
        self.total_label = QLabel()
        self.total_label.setObjectName("CartDetailTotal")

        back = QPushButton("Volver al menú")
        back.setObjectName("ClearButton")
        back.setMinimumHeight(48)
        back.setCursor(Qt.PointingHandCursor)
        back.clicked.connect(self.reject)

        footer = QHBoxLayout()
        footer.setSpacing(12)
        footer.addWidget(total_caption)
        footer.addWidget(self.total_label)
        footer.addStretch(1)
        footer.addWidget(back)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(8)
        layout.addLayout(head)
        layout.addWidget(self.scroll, 1)
        layout.addWidget(self.status)
        layout.addLayout(footer)

        self.refresh()

    # --- ciclo de vida ---
    def run_fullscreen(self):
        """Abre el detalle ocupando toda la pantalla del kiosco."""
        self.showFullScreen()
        return self.exec()

    # --- filas ---
    def _row(self, item):
        frame = QFrame()
        frame.setObjectName("CartDetailRow")
        self.scroll.watch(frame)

        info = QVBoxLayout()
        info.setSpacing(1)

        name = QLabel(item.product.name)
        name.setObjectName("CartDetailName")
        name.setWordWrap(True)
        info.addWidget(name)

        if item.addons:
            addons = QLabel("+ " + ", ".join(a.name for a in item.addons))
            addons.setObjectName("CartDetailAddons")
            addons.setWordWrap(True)
            info.addWidget(addons)

        if item.note:
            note = QLabel(f"Nota: {item.note}")
            note.setObjectName("CartDetailNote")
            note.setWordWrap(True)
            info.addWidget(note)

        unit = QLabel(f"{format_price(item.unit_price)} c/u")
        unit.setObjectName("CartDetailUnit")
        info.addWidget(unit)

        minus = QPushButton("−")
        minus.setObjectName("QtyButton")
        minus.setFixedSize(46, 46)
        minus.setCursor(Qt.PointingHandCursor)
        minus.clicked.connect(lambda: self._minus(item.key))
        self.scroll.watch(minus)

        qty = QLabel(str(item.quantity))
        qty.setObjectName("CartDetailQty")
        qty.setAlignment(Qt.AlignCenter)
        qty.setMinimumWidth(34)

        plus = QPushButton("+")
        plus.setObjectName("QtyButton")
        plus.setFixedSize(46, 46)
        plus.setCursor(Qt.PointingHandCursor)
        plus.clicked.connect(lambda: self._plus(item))
        self.scroll.watch(plus)

        subtotal = QLabel(format_price(item.subtotal))
        subtotal.setObjectName("CartDetailSubtotal")
        subtotal.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        subtotal.setMinimumWidth(100)

        row = QHBoxLayout(frame)
        row.setContentsMargins(14, 10, 14, 10)
        row.setSpacing(10)
        row.addLayout(info, 1)
        row.addWidget(minus, 0, Qt.AlignVCenter)
        row.addWidget(qty, 0, Qt.AlignVCenter)
        row.addWidget(plus, 0, Qt.AlignVCenter)
        row.addWidget(subtotal, 0, Qt.AlignVCenter)
        return frame

    def _plus(self, item):
        reason = self.cart.blocked_reason(item.product, item.addons)
        if reason:
            self.flash(reason)
            return
        self.cart.add(item.product, item.addons, item.note)
        self.refresh()
        self.changed.emit()

    def _minus(self, key):
        self.cart.remove_one(key)
        self.refresh()
        self.changed.emit()

    def flash(self, text: str):
        self.status.setText(text)
        self._status_timer.start(4000)

    def refresh(self):
        while self.list_layout.count():
            w = self.list_layout.takeAt(0).widget()
            if w:
                w.deleteLater()

        if self.cart.is_empty:
            empty = QLabel("Todavía no has agregado nada a tu pedido.")
            empty.setObjectName("CartDetailEmpty")
            empty.setAlignment(Qt.AlignCenter)
            self.list_layout.addWidget(empty)
        for item in self.cart.items:
            self.list_layout.addWidget(self._row(item))

        self.total_label.setText(format_price(self.cart.total))
