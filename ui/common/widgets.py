from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QPainter, QPainterPath, QPixmap
from PySide6.QtWidgets import QFrame, QLabel, QSizePolicy, QToolButton, QVBoxLayout

from core.models import Product
from services.image_cache import cached_image_path
from ui.common.assets import RED, icon_for_category

IMG_W, IMG_H = 180, 130


def format_price(value: int) -> str:
    return "$" + f"{value:,}".replace(",", ".")


class CategoryButton(QToolButton):
    def __init__(self, name: str):
        super().__init__()
        self.setObjectName("CategoryButton")
        self.setText(name)
        self.setCheckable(True)
        self.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.setIconSize(QSize(36, 36))
        self.setMinimumHeight(96)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._normal = icon_for_category(name, RED)
        self._active = icon_for_category(name, "#FFFFFF")
        self.setIcon(self._normal)
        self.toggled.connect(self._on_toggled)

    def _on_toggled(self, on: bool):
        self.setIcon(self._active if on else self._normal)


class ProductCard(QFrame):
    clicked = Signal(object)

    def __init__(self, product: Product):
        super().__init__()
        self.product = product
        self.sold_out = product.max_qty is not None and product.max_qty <= 0
        self.setObjectName("ProductCard")
        self.setProperty("soldOut", self.sold_out)
        self.setFixedSize(200, 250)
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
        if not self.sold_out:
            self.clicked.emit(self.product)