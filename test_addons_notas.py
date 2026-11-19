# -*- coding: utf-8 -*-
"""Adiciones siempre visibles + observaciones opcionales por producto.

No toca Supabase ni la impresora. Qt en modo offscreen:
    $env:QT_QPA_PLATFORM="offscreen"; .\\venv\\Scripts\\python.exe test_addons_notas.py
"""
import os
import sys
import tempfile

from PySide6.QtWidgets import QApplication

import config
import services.ticket_renderer as renderer
import ui.cliente.addons_dialog as ad
import ui.cliente.main_window as mw
from core.cart import Cart
from core.models import Addon, CartItem, Product
from services.tickets_service import notes_payload
from ui.common.assets import load_fonts

PIZZA = Product(id=1, category_id=20, name="Pizza hawaiiana", price=20000)
ADDS = [
    Addon(id=100 + i, name=f"Adición {i}", price=2000 * i, stock=0,
          category_ids=(20,))
    for i in range(1, 12)
]
ADDS[3].stock = 2                       # una sola con stock, para variar


def main():
    # ---- 1) carrito: la observación separa o une líneas ----
    cart = Cart()
    assert cart.add(PIZZA)
    assert cart.add(PIZZA, (), "sin cebolla")
    assert cart.add(PIZZA, (), "  SIN cebolla ")
    assert cart.add(PIZZA)

    items = cart.items
    assert len(items) == 2, [(i.product.name, i.quantity, i.note) for i in items]
    assert items[0].note == "" and items[0].quantity == 2
    assert items[1].note == "sin cebolla" and items[1].quantity == 2
    assert cart.count == 4 and cart.total == 80000

    payload = notes_payload(items)
    assert payload == [{"line": 1, "note": "sin cebolla"}], payload
    print("carrito con observaciones OK")

    # ---- 2) sync() no pierde la observación ----
    fresh_p = [Product(id=1, category_id=20, name="Pizza hawaiiana", price=20000)]
    fresh_a = [Addon(id=a.id, name=a.name, price=a.price, stock=9, category_ids=(20,))
               for a in ADDS]
    assert cart.sync(fresh_p, fresh_a) is False
    assert [i.note for i in cart.items] == ["", "sin cebolla"]
    print("sync conserva observaciones OK")

    app = QApplication(sys.argv)
    load_fonts()
    qss = config.RESOURCE_DIR / "ui" / "common" / "styles.qss"
    app.setStyleSheet(qss.read_text(encoding="utf-8"))

    # ---- 3) el cuadro de adiciones se abre con todo agotado ----
    left = {a.id: (0 if a.id != ADDS[3].id else 2) for a in ADDS}
    dialog = ad.AddonsDialog(PIZZA, ADDS, left)
    dialog.show()
    app.processEvents()

    assert len(dialog._rows) == 11
    agotadas = [c for c, a in dialog._rows if not c.isEnabled()]
    assert len(agotadas) == 10, len(agotadas)
    habilitada = [c for c, a in dialog._rows if c.isEnabled()]
    assert len(habilitada) == 1
    assert "Agotado" in agotadas[0].text()
    assert "Agotado" not in habilitada[0].text()
    assert dialog.note_btn.text().startswith("Añadir observación")

    dialog._note = "sin piña"
    dialog._update_note_button()
    assert "sin piña" in dialog.note_btn.text()
    assert dialog.selected_note() == "sin piña"
    assert dialog.selected_addons() == ()
    print("adiciones agotadas visibles OK")

    # ---- 3a) si todas están agotadas, el aviso lo dice ----
    todo_agotado = ad.AddonsDialog(PIZZA, ADDS, {a.id: 0 for a in ADDS})
    assert "agotadas" in todo_agotado.subtitle.text().lower()
    todo_agotado.close()
    print("aviso de todo agotado OK")

    # ---- 3b) cuadrícula: columnas de máximo 5 filas ----
    assert (dialog.columns, dialog.rows_per_column) == (3, 4), (
        dialog.columns, dialog.rows_per_column)
    assert dialog.width() >= 600, dialog.width()

    def grid_demo(n):
        adds = [
            Addon(id=200 + i, name=f"Adición {i}", price=1000, stock=1,
                  category_ids=(20,))
            for i in range(n)
        ]
        dlg = ad.AddonsDialog(PIZZA, adds, {a.id: 1 for a in adds})
        return dlg, adds

    for n, want_cols, want_rows in ((10, 2, 5), (15, 3, 5), (11, 3, 4), (20, 4, 5)):
        dlg, _adds = grid_demo(n)
        assert (dlg.columns, dlg.rows_per_column) == (want_cols, want_rows), (
            n, dlg.columns, dlg.rows_per_column)
        # La columna 2 empieza arriba: llenado por columnas, no por filas.
        assert dlg.grid.itemAtPosition(0, 1).widget() is dlg._rows[want_rows][0]
        assert dlg.grid.itemAtPosition(want_rows - 1, 0).widget() is dlg._rows[want_rows - 1][0]
        assert dlg.sizeHint().height() <= 480, (n, dlg.sizeHint().height())
        dlg.close()
    print("cuadrícula de adiciones OK")

    shot = os.path.join(tempfile.gettempdir(), "preview_addons.png")
    dialog.grab().save(shot)
    print("captura:", shot, "| alto:", dialog.sizeHint().height())
    assert dialog.sizeHint().height() <= 480, dialog.sizeHint().height()

    # ---- 4) el teclado táctil escribe en las observaciones ----
    note = ad.NoteDialog("", dialog)
    note.show()
    note.edit.setFocus()
    app.processEvents()
    assert note.keyboard._target() is note.edit, note.keyboard._target()

    for ch in "sin":
        note.keyboard._insert(ch)
    note.keyboard._insert(" salsa")
    note.keyboard._backspace()
    app.processEvents()
    assert note.text() == "sin sals", repr(note.text())

    note.keyboard._insert("a")
    app.processEvents()
    assert note.text() == "sin salsa"
    print("teclado de observaciones OK")

    shot_note = os.path.join(tempfile.gettempdir(), "preview_nota.png")
    note.grab().save(shot_note)
    print("captura:", shot_note, "| alto:", note.sizeHint().height())

    note.close()
    dialog.close()

    # ---- 5) la ventana abre el cuadro aunque el stock sea 0 ----
    opened = {}

    class FakeDialog:
        def __init__(self, product, addons, left_by_id, parent=None, note=""):
            opened["product"] = product
            opened["addons"] = list(addons)

        def exec(self):
            return True

        def selected_addons(self):
            return ()

        def selected_note(self):
            return "bien cocida"

    mw.run_async = lambda *a, **k: None          # sin red al construir
    mw.AddonsDialog = FakeDialog
    win = mw.ClientWindow()
    win.addons = ADDS
    win._add_to_cart(PIZZA)
    assert opened.get("product") is PIZZA, opened
    assert len(opened.get("addons") or []) == 11
    assert win.cart.items[0].note == "bien cocida"
    win.close()
    print("la ventana abre adiciones con stock 0 OK")

    # ---- 6) el ticket impreso incluye la observación ----
    vistos = []
    original_wrap = renderer._wrap

    def spy(draw, text, font, max_w):
        vistos.append(text)
        return original_wrap(draw, text, font, max_w)

    renderer._wrap = spy
    lineas = [CartItem(PIZZA, 1, (), "sin cebolla")]
    try:
        imagen = renderer.render_ticket(7, lineas, 20000)
    finally:
        renderer._wrap = original_wrap
    assert any(t.startswith("* sin cebolla") for t in vistos), vistos
    assert imagen.height > 0
    print("observación impresa en el ticket OK")

    print("ADICIONES + NOTAS OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
