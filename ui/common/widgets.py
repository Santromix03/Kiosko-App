import weakref

from PySide6.QtCore import QEvent, QSize, Qt, QTimer, Signal
from PySide6.QtGui import QPainter, QPainterPath, QPixmap
from PySide6.QtWidgets import (
    QAbstractButton, QFrame, QLabel, QScrollArea, QSizePolicy, QToolButton,
    QVBoxLayout,
)

from core.models import Product
from services.image_cache import cached_image_path
from ui.common.assets import RED, icon_for_category

IMG_W, IMG_H = 148, 104
CARD_W, CARD_H = 168, 200


def format_price(value: int) -> str:
    return "$" + f"{value:,}".replace(",", ".")


class CategoryButton(QToolButton):
    def __init__(self, name: str):
        super().__init__()
        self.setObjectName("CategoryButton")
        self.setText(name)
        self.setCheckable(True)
        self.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.setIconSize(QSize(22, 22))
        self.setMinimumHeight(48)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._normal = icon_for_category(name, RED)
        self._active = icon_for_category(name, "#FFFFFF")
        self.setIcon(self._normal)
        self.toggled.connect(self._on_toggled)

    def _on_toggled(self, on: bool):
        self.setIcon(self._active if on else self._normal)


class DragScroll(QScrollArea):
    """Lista o grilla deslizable con el dedo (horizontal o vertical).

    - Un toque corto hace el clic normal del elemento (categoría, producto,
      botón de un ticket).
    - Un arrastre mueve la lista y cancela ese clic.
    Los eventos de mouse fluyen normales (no se secuestran): así el mouse
    grabado se libera bien y nada más se rompe.

    `watch(widget, "dragging_check")` deja en el widget una función para
    saber si el toque terminó siendo arrastre (así ProductCard / TicketRow
    pueden ignorar el clic).
    """

    DRAG_THRESHOLD = 14   # px antes de considerar que es arrastre, no toque

    def __init__(self, orientation=Qt.Vertical):
        super().__init__()
        self._orientation = orientation
        self._press = None        # posición GLOBAL del press (no cambia al hacer scroll)
        self._dragging = False
        self._suppress = False    # el clic del elemento arrastrado se ignora
        self._watched = weakref.WeakSet()
        self._host = None

    def watch(self, widget, check_attr: str | None = None):
        if check_attr:
            setattr(widget, check_attr, lambda: self._suppress)
        self._watched.add(widget)
        widget.installEventFilter(self)

    def watch_host(self, host):
        """También permite arrastrar desde los espacios entre elementos."""
        self._host = host
        host.installEventFilter(self)

    @property
    def dragging(self):
        return self._suppress

    def _end_drag(self):
        self._suppress = False

    def eventFilter(self, obj, event):
        if obj is not self._host and obj not in self._watched:
            return super().eventFilter(obj, event)   # scrollbars internos, etc.

        t = event.type()
        if t == QEvent.MouseButtonPress:
            self._press = event.globalPosition()
            self._dragging = False
            self._suppress = False
        elif t == QEvent.MouseMove and self._press is not None:
            d = event.globalPosition() - self._press
            if self._orientation == Qt.Horizontal:
                passed = abs(d.x()) > self.DRAG_THRESHOLD
            else:
                passed = (abs(d.x()) > self.DRAG_THRESHOLD
                          or abs(d.y()) > self.DRAG_THRESHOLD)
            if not self._dragging and passed:
                self._dragging = True
                self._suppress = True
                if isinstance(obj, QAbstractButton):
                    obj.setDown(False)               # suelta el estado presionado
            if self._dragging:
                if self._orientation == Qt.Horizontal:
                    bar = self.horizontalScrollBar()
                    bar.setValue(bar.value() - int(d.x()))
                else:
                    bar = self.verticalScrollBar()
                    bar.setValue(bar.value() - int(d.y()))
                self._press = event.globalPosition()
        elif t == QEvent.MouseButtonRelease:
            if self._dragging:
                if isinstance(obj, QAbstractButton):
                    obj.setDown(False)
                # el clic emitido por este release se ignora (ver el check_attr)
                QTimer.singleShot(0, self._end_drag)
            self._press = None
            self._dragging = False
        return super().eventFilter(obj, event)


class ProductCard(QFrame):
    clicked = Signal(object)

    dragging_check = None   # lo asigna GridScroll: True si el toque fue arrastre

    def __init__(self, product: Product):
        super().__init__()
        self.product = product
        self.sold_out = product.max_qty is not None and product.max_qty <= 0
        self.setObjectName("ProductCard")
        self.setProperty("soldOut", self.sold_out)
        self.setFixedSize(CARD_W, CARD_H)
        self.setCursor(Qt.ArrowCursor if self.sold_out else Qt.PointingHandCursor)

        image = QLabel("Sin imagen")
        image.setObjectName("ProductImage")
        image.setFixedSize(IMG_W, IMG_H)
        image.setAlignment(Qt.AlignCenter)
        self._load_image(image, product.image_url)

        name = QLabel(product.name)
        name.setObjectName("ProductName")
        name.setWordWrap(True)

        price = QLabel("Agotado" if self.sold_out else format_price(product.price))
        price.setObjectName("SoldOutLabel" if self.sold_out else "ProductPrice")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 12)
        layout.setSpacing(6)
        layout.addWidget(image, 0, Qt.AlignHCenter)
        layout.addWidget(name)
        layout.addWidget(price)
        layout.addStretch()

    @staticmethod
    def _load_image(label: QLabel, url):
        path = cached_image_path(url)
        if path is None:
            return
        pm = QPixmap(str(path))
        if pm.isNull():
            return
        pm = pm.scaled(QSize(IMG_W, IMG_H), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        x = (pm.width() - IMG_W) // 2
        y = (pm.height() - IMG_H) // 2
        pm = pm.copy(x, y, IMG_W, IMG_H)

        rounded = QPixmap(IMG_W, IMG_H)       # esquinas redondeadas
        rounded.fill(Qt.transparent)
        painter = QPainter(rounded)
        painter.setRenderHint(QPainter.Antialiasing)
        clip = QPainterPath()
        clip.addRoundedRect(0, 0, IMG_W, IMG_H, 10, 10)
        painter.setClipPath(clip)
        painter.drawPixmap(0, 0, pm)
        painter.end()
        label.setPixmap(rounded)

    def mousePressEvent(self, event):
        # El click se emite al SOLTAR (no al presionar): así un arrastre de la
        # cuadrícula no agrega el producto al carrito por accidente.
        self._press_ok = not self.sold_out and event.button() == Qt.LeftButton

    def mouseReleaseEvent(self, event):
        if not self._press_ok:
            return
        self._press_ok = False
        if self.dragging_check is not None and self.dragging_check():
            return                       # fue un arrastre, no un toque
        self.clicked.emit(self.product)