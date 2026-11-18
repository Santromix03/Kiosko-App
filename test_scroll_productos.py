# -*- coding: utf-8 -*-
"""Prueba el drag-scroll de la cuadrícula de productos (como la barra de categorías).

- Un arrastre con el dedo/mouse desliza la lista y NO agrega el producto.
- Un toque corto SÍ agrega el producto al carrito.
"""
import sys

from PySide6.QtCore import QEvent, QPointF, Qt
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QApplication

import config
config.KIOSK_FULLSCREEN = False
config.SUPABASE_URL, config.SUPABASE_ANON_KEY = "x", "y"

from core.models import Category, Product
from ui.cliente.main_window import ClientWindow

app = QApplication(sys.argv)
win = ClientWindow()

# ---- menu falso: 2 categorias x 24 productos (para que sobre espacio de scroll)
cats = [Category(101, "Prueba A", 1), Category(102, "Prueba B", 2)]
prods = [
    Product(id=i + 1, category_id=101, name=f"Producto {i + 1}", price=1000 + i)
    for i in range(24)
] + [
    Product(id=100 + i, category_id=102, name=f"Otro {i}", price=500)
    for i in range(5)
]
win._on_loaded((cats, prods, []))
win.resize(800, 480)
win.show()
app.processEvents()

win._show_category(101)
app.processEvents()

card = None
for i in range(win.grid.count()):
    w = win.grid.itemAt(i).widget()
    if hasattr(w, "product"):
        card = w
        break
assert card is not None, "no hay tarjeta"

bar = win.grid_scroll.verticalScrollBar()
top = bar.minimum()
bar.setValue(top)
app.processEvents()
print("scrollbar rango:", bar.minimum(), "-", bar.maximum())

g = card.mapToGlobal(QPointF(card.width() / 2, card.height() / 2))


def ev(t, gp):
    """Construye el mouse event correcto: press (botón izq), move (buttons izq), release."""
    local = card.mapFromGlobal(gp)
    if t == QEvent.MouseButtonPress:
        return QMouseEvent(t, QPointF(local), QPointF(gp), Qt.LeftButton,
                           Qt.LeftButton, Qt.NoModifier)
    if t == QEvent.MouseMove:
        return QMouseEvent(t, QPointF(local), QPointF(gp), Qt.NoButton,
                           Qt.LeftButton, Qt.NoModifier)
    return QMouseEvent(t, QPointF(local), QPointF(gp), Qt.LeftButton,
                       Qt.NoButton, Qt.NoModifier)


# ---- 1) ARRASTRE hacia arriba (el contenido baja y la barra avanza): no agrega
app.sendEvent(card, ev(QEvent.MouseButtonPress, g))
app.processEvents()
for step in (1, 2, 3, 4):
    gp = QPointF(g.x(), g.y() - 40 * step)
    app.sendEvent(card, ev(QEvent.MouseMove, gp))
    app.processEvents()
app.sendEvent(card, ev(QEvent.MouseButtonRelease, QPointF(g.x(), g.y() - 160)))
app.processEvents()

scrolled = bar.value()
qty = win.cart.product_qty(card.product.id)
print(f"tras arrastre: scroll={scrolled}px, cantidad en carrito={qty}")
ok_drag = scrolled > 0 and qty == 0

# ---- 2) TOQUE corto: sí agrega al carrito
app.sendEvent(card, ev(QEvent.MouseButtonPress, g))
app.processEvents()
app.sendEvent(card, ev(QEvent.MouseButtonRelease, g))
app.processEvents()
qty2 = win.cart.product_qty(card.product.id)
print(f"tras toque corto: cantidad en carrito={qty2}")
ok_tap = qty2 == 1

print("DRAG-SCROLL OK" if (ok_drag and ok_tap) else "FALLO")
