from PySide6.QtCore import QByteArray, Qt
from PySide6.QtGui import QFontDatabase, QIcon, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer

import config

ASSETS = config.BASE_DIR / "assets"
RED = "#C21A1F"

CATEGORY_ICONS = {
    "bebidas calientes": "coffee",
    "bebidas frías": "glass-water",
    "hamburguesas": "hamburger",
    "sodas saborizadas": "cup-soda",
}
DEFAULT_ICON = "utensils"


def load_fonts():
    for f in (ASSETS / "fonts").glob("*.ttf"):
        QFontDatabase.addApplicationFont(str(f))


def svg_icon(name: str, color: str, size: int = 36) -> QIcon:
    """Carga un SVG de assets/icons y lo pinta del color pedido."""
    path = ASSETS / "icons" / f"{name}.svg"
    if not path.exists():
        path = ASSETS / "icons" / f"{DEFAULT_ICON}.svg"
    if not path.exists():
        return QIcon()
    svg = path.read_text(encoding="utf-8").replace("currentColor", color)
    renderer = QSvgRenderer(QByteArray(svg.encode("utf-8")))
    pm = QPixmap(size * 2, size * 2)      # al doble para que se vea nítido
    pm.fill(Qt.transparent)
    painter = QPainter(pm)
    renderer.render(painter)
    painter.end()
    return QIcon(pm)


def icon_for_category(name: str, color: str, size: int = 36) -> QIcon:
    return svg_icon(CATEGORY_ICONS.get(name.lower().strip(), DEFAULT_ICON), color, size)