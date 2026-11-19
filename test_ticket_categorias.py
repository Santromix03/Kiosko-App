# -*- coding: utf-8 -*-
"""El ticket agrupa los productos por categoría y deja aire antes del corte.

No toca Supabase ni la impresora; solo dibuja la imagen y sus comandos ESC/POS:
    .\\venv\\Scripts\\python.exe test_ticket_categorias.py
"""
import os
import sys
import tempfile
from datetime import datetime

from PIL import ImageDraw

import config
import services.printer_service as printer
import services.tickets_service as tickets_service
from core.models import Addon, CartItem, Product
from services.ticket_renderer import render_ticket
from services.tickets_service import Ticket, TicketItem, reprint_ticket


def capture_text():
    """Espía las llamadas a ImageDraw.text para leer lo que se imprime y dónde."""
    calls = []
    original = ImageDraw.ImageDraw.text

    def spy(self, xy, text, *args, **kwargs):
        calls.append((str(text), float(xy[0]), float(xy[1])))
        return original(self, xy, text, *args, **kwargs)

    ImageDraw.ImageDraw.text = spy
    return calls, original


def y_of(calls, text):
    hits = [y for value, _x, y in calls if value == text]
    assert len(hits) == 1, (text, hits)
    return hits[0]


def blank_below(img):
    """Filas blancas al final de la imagen (lo que la impresora avanza antes de cortar)."""
    mono = img.convert("L").point(lambda p: 255 if p < 250 else 0)
    box = mono.getbbox()
    assert box, "el ticket salió vacío"
    return img.height - box[3]


def main():
    hamburguesa = Product(id=1, category_id=20, name="Hamburguesa", price=20000)
    perro = Product(id=2, category_id=21, name="Perro", price=6000)
    pizza = Product(id=3, category_id=20, name="Pizza", price=24000)
    queso = Addon(id=10, name="Queso", price=3000, stock=5, category_ids=(20,))

    # El pedido mezcla categorías a propósito: Hamburguesa, Perro, Pizza.
    items = [
        CartItem(hamburguesa, 1, (queso,), "sin cebolla"),
        CartItem(perro, 2),
        CartItem(pizza, 1),
    ]
    category_names = {20: "Hamburguesas", 21: "Perros"}

    calls, original = capture_text()
    try:
        live = render_ticket(99, items, 56000, category_names=category_names)
    finally:
        ImageDraw.ImageDraw.text = original

    # ---- 1) encabezados en MAYÚSCULAS, una sola vez y en orden ----
    heads = [text for text, _x, _y in calls
             if text in ("HAMBURGUESAS", "PERROS")]
    assert heads == ["HAMBURGUESAS", "PERROS"], heads

    y_head_1 = y_of(calls, "HAMBURGUESAS")
    y_hamb = y_of(calls, "HAMBURGUESA")
    y_pizza = y_of(calls, "PIZZA")
    y_head_2 = y_of(calls, "PERROS")
    y_perro = y_of(calls, "PERRO")

    # La pizza (misma categoría) sube al primer grupo, antes de "PERROS".
    assert y_head_1 < y_hamb < y_pizza < y_head_2 < y_perro, (
        y_head_1, y_hamb, y_pizza, y_head_2, y_perro)
    print("categorías agrupadas y en orden OK")

    # ---- 2) la categoría va arriba de sus productos ----
    assert y_head_1 < y_hamb and y_head_2 < y_perro
    print("encabezado arriba de los productos OK")

    # ---- 3) aire suficiente antes del corte (no sale mocho) ----
    margen = blank_below(live)
    print("espacio blanco al final:", margen, "px | alto:", live.height)
    assert margen >= 70, margen

    # ---- 4) los comandos ESC/POS avanzan 6 líneas antes de cortar ----
    raster = printer.image_to_raster(live)
    assert b"\x1b\x64\x06" in raster
    assert raster.endswith(b"\x1b\x64\x06")
    print("avance de papel antes del corte OK")

    # ---- 5) reimprimir usa la categoría guardada en la base ----
    ahora = datetime.now().astimezone()
    ticket = Ticket(
        id=7, number=45, created_at=ahora, total=26000,
        items=(
            TicketItem("Hamburguesa doble", 1, 20000, category="Hamburguesas"),
            TicketItem("Gaseosa 400 ml", 2, 3000, category="Bebidas"),
        ),
    )

    impresas = []
    original_print = tickets_service.print_ticket
    tickets_service.print_ticket = impresas.append
    calls, original = capture_text()
    try:
        reprint_ticket(ticket)
    finally:
        tickets_service.print_ticket = original_print
        ImageDraw.ImageDraw.text = original

    assert len(impresas) == 1
    reimpreso = impresas[0]
    textos = [text for text, _x, _y in calls]
    assert textos.count("HAMBURGUESAS") == 1, textos
    assert textos.count("BEBIDAS") == 1, textos
    assert blank_below(reimpreso) >= 70
    print("reimpresión con categoría OK")

    shot = os.path.join(tempfile.gettempdir(), "preview_ticket_categorias.png")
    live.save(shot)
    print("captura:", shot)

    print("CATEGORIAS EN EL TICKET OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
