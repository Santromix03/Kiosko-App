# -*- coding: utf-8 -*-
"""Detalle del pedido a pantalla completa, con su X para volver al menú.

Qt en modo offscreen:
    $env:QT_QPA_PLATFORM="offscreen"; .\\venv\\Scripts\\python.exe test_cart_detail.py
"""
import os
import sys
import tempfile

from PySide6.QtWidgets import QApplication, QLabel, QPushButton

import config
from core.cart import Cart
from core.models import Addon, Product
from ui.cliente.cart_detail_dialog import CartDetailDialog
from ui.cliente.cart_panel import CartPanel
from ui.common.assets import load_fonts


def main():
    hamburguesa = Product(id=1, category_id=20, name="Hamburguesa doble", price=20000)
    gaseosa = Product(id=2, category_id=20, name="Gaseosa 400 ml", price=4000)
    queso = Addon(id=10, name="Queso cheddar", price=3000, stock=5, category_ids=(20,))

    cart = Cart()
    assert cart.add(hamburguesa, (queso,), "sin cebolla")
    assert cart.add(gaseosa)
    assert cart.add(gaseosa)
    assert cart.total == 31000

    app = QApplication(sys.argv)
    load_fonts()
    qss = config.RESOURCE_DIR / "ui" / "common" / "styles.qss"
    app.setStyleSheet(qss.read_text(encoding="utf-8"))

    # ---- 1) la ventana abre a pantalla completa ----
    dialog = CartDetailDialog(cart)
    dialog.showFullScreen()
    app.processEvents()
    print("pantalla completa:", dialog.isFullScreen(), "| tamaño:", dialog.size())
    assert dialog.isFullScreen()
    assert dialog.list_layout.count() == 2
    assert dialog.total_label.text() == "$31.000"

    textos = " | ".join(lbl.text() for lbl in dialog.findChildren(QLabel))
    assert "Hamburguesa doble" in textos
    assert "Queso cheddar" in textos
    assert "sin cebolla" in textos
    assert "Gaseosa 400 ml" in textos
    print("detalle completo OK")

    # ---- 2) la X cierra la ventana ----
    assert dialog.close_btn.text() == "X"
    dialog.close_btn.click()
    app.processEvents()
    assert not dialog.isVisible()
    print("X para cerrar OK")

    # ---- 3) + y − funcionan desde el detalle ----
    dialog = CartDetailDialog(cart)
    dialog.showFullScreen()
    app.processEvents()
    cambios = []
    dialog.changed.connect(lambda: cambios.append(1))

    frame = dialog.list_layout.itemAt(0).widget()
    botones = frame.findChildren(QPushButton)
    plus = next(b for b in botones if b.text() == "+")
    plus.click()
    app.processEvents()
    assert cart.items[0].quantity == 2
    assert dialog.total_label.text() == "$54.000"
    assert cambios, "no avisó el cambio al carrito"

    frame = dialog.list_layout.itemAt(0).widget()
    botones = frame.findChildren(QPushButton)
    minus = next(b for b in botones if b.text() == "−")
    minus.click()
    app.processEvents()
    assert cart.items[0].quantity == 1
    assert dialog.total_label.text() == "$31.000"
    print("cantidades desde el detalle OK")

    shot = os.path.join(tempfile.gettempdir(), "preview_detalle.png")
    dialog.grab().save(shot)
    print("captura:", shot)
    dialog.close()

    # ---- 4) el título "Tu pedido" avisa que quiere abrir el detalle ----
    panel = CartPanel(cart)
    abiertos = []
    panel.detail_requested.connect(lambda: abiertos.append(1))
    assert panel.title_btn.text().startswith("Tu pedido")
    panel.title_btn.click()
    assert abiertos == [1]
    print("botón Tu pedido OK")

    # ---- 5) carrito vacío ----
    vacio = CartDetailDialog(Cart())
    vacio.showFullScreen()
    app.processEvents()
    assert vacio.total_label.text() == "$0"
    assert any("Todavía no has agregado" in lbl.text()
               for lbl in vacio.findChildren(QLabel))
    vacio.close()
    print("carrito vacío OK")

    print("DETALLE DEL PEDIDO OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
