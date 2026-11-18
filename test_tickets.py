# -*- coding: utf-8 -*-
"""Prueba la pantalla Tickets: lista del día, reimprimir, cancelar y deslizar.

Usa tickets falsos (no toca Supabase ni la impresora) y Qt en modo offscreen:
    $env:QT_QPA_PLATFORM="offscreen"; .\\venv\\Scripts\\python.exe test_tickets.py
"""
import json
import sys
import time
from datetime import datetime, timedelta

from PySide6.QtCore import QEvent, QPointF, Qt
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QApplication

import config
import ui.cliente.tickets_dialog as td
from services.tickets_service import (
    BOGOTA, Ticket, TicketAddon, TicketItem, _tickets_from_payload,
)
from ui.common.assets import load_fonts


def pump(app, seconds=1.0, until=None):
    end = time.time() + seconds
    while time.time() < end:
        app.processEvents()
        if until is not None and until():
            return True
        time.sleep(0.01)
    return until() if until is not None else True


def main():
    # ---- 0) parseo del JSON que devuelve get_today_tickets ----
    raw = [{
        "id": 7, "ticket_number": 45,
        "created_at": "2026-03-30T14:22:10-05:00", "total": 24000,
        "items": [{
            "name": "Hamburguesa doble", "quantity": 1, "unit_price": 20000,
            "addons": [{"name": "Queso", "unit_price": 4000}],
        }],
    }]
    parsed = _tickets_from_payload(raw)
    assert parsed[0].number == 45
    assert parsed[0].time_label == "14:22"
    assert parsed[0].summary() == "1× Hamburguesa doble (+ Queso)"
    assert parsed[0].items[0].addons[0].price == 4000
    assert len(_tickets_from_payload(json.dumps(raw))) == 1
    print("parseo RPC OK")

    now = datetime.now(BOGOTA)
    tickets = [
        Ticket(
            id=100 + i,
            number=45 + i,
            created_at=now - timedelta(minutes=7 * i),
            total=12000 + 3500 * i,
            items=(
                TicketItem("Hamburguesa doble", 1, 20000, (TicketAddon("Queso", 4000),)),
                TicketItem("Perro sencillo", 2, 6000),
            ),
        )
        for i in range(9)
    ]

    calls = {"reprint": [], "cancel": []}

    def fake_fetch():
        return list(tickets)

    def fake_reprint(ticket):
        calls["reprint"].append(ticket.number)

    def fake_cancel(ticket):
        calls["cancel"].append(ticket.number)
        tickets.remove(ticket)
        return ticket.number

    class FakeConfirm:
        def __init__(self, ticket, parent=None):
            pass

        def exec(self):
            return True

    td.fetch_today_tickets = fake_fetch
    td.reprint_ticket = fake_reprint
    td.cancel_ticket = fake_cancel
    td.ConfirmCancelDialog = FakeConfirm

    app = QApplication(sys.argv)
    load_fonts()
    qss = config.RESOURCE_DIR / "ui" / "common" / "styles.qss"
    app.setStyleSheet(qss.read_text(encoding="utf-8"))
    dialog = td.TicketsDialog()
    dialog.show()
    ok_rows = pump(app, 3, lambda: len(dialog.host.findChildren(td.TicketRow)) == 9)
    rows = dialog.host.findChildren(td.TicketRow)
    print("filas:", len(rows), "| estado:", dialog.status.text())
    assert ok_rows

    # ---- 1) deslizar la lista con el dedo ----
    row = rows[0]
    bar = dialog.scroll.verticalScrollBar()
    bar.setValue(bar.minimum())
    app.processEvents()
    print("scrollbar:", bar.minimum(), "-", bar.maximum())

    g = row.mapToGlobal(QPointF(row.width() / 2, row.height() / 2))

    def ev(t, gp):
        local = row.mapFromGlobal(gp)
        buttons = Qt.LeftButton if t in (QEvent.MouseButtonPress, QEvent.MouseMove) else Qt.NoButton
        button = Qt.LeftButton if t != QEvent.MouseMove else Qt.NoButton
        return QMouseEvent(t, QPointF(local), QPointF(gp), button, buttons, Qt.NoModifier)

    app.sendEvent(row, ev(QEvent.MouseButtonPress, g))
    for step in (1, 2, 3):
        app.sendEvent(row, ev(QEvent.MouseMove, QPointF(g.x(), g.y() - 40 * step)))
        app.processEvents()
    app.sendEvent(row, ev(QEvent.MouseButtonRelease, QPointF(g.x(), g.y() - 120)))
    pump(app, 0.2)
    print("tras arrastre: scroll =", bar.value(), "| carrito de acciones =", calls)
    ok_drag = bar.value() > 0 and not calls["reprint"] and not calls["cancel"]

    # ---- 1b) arrastre que empieza sobre el botón Imprimir: NO reimprime ----
    btn = rows[2].btn_print
    gb = btn.mapToGlobal(QPointF(btn.width() / 2, btn.height() / 2))

    def ev_btn(t, gp):
        local = btn.mapFromGlobal(gp)
        buttons = Qt.LeftButton if t in (QEvent.MouseButtonPress, QEvent.MouseMove) else Qt.NoButton
        button = Qt.LeftButton if t != QEvent.MouseMove else Qt.NoButton
        return QMouseEvent(t, QPointF(local), QPointF(gp), button, buttons, Qt.NoModifier)

    app.sendEvent(btn, ev_btn(QEvent.MouseButtonPress, gb))
    for step in (1, 2, 3):
        app.sendEvent(btn, ev_btn(QEvent.MouseMove, QPointF(gb.x(), gb.y() - 30 * step)))
        app.processEvents()
    app.sendEvent(btn, ev_btn(QEvent.MouseButtonRelease, QPointF(gb.x(), gb.y() - 90)))
    pump(app, 0.2)
    print("arrastre sobre botón -> reimpresos:", calls["reprint"])
    ok_drag = ok_drag and not calls["reprint"]

    # ---- 2) reimprimir el primer ticket ----
    rows[0].btn_print.click()
    ok_print = pump(
        app, 3,
        lambda: len(calls["reprint"]) == 1 and "reimpreso" in dialog.status.text(),
    )
    print("reimprimir ->", calls["reprint"], "| estado:", dialog.status.text())

    # ---- 3) cancelar el segundo ticket ----
    target = rows[1].ticket.number
    rows[1].btn_cancel.click()
    ok_cancel = pump(
        app, 5,
        lambda: calls["cancel"] == [target]
        and len(dialog.host.findChildren(td.TicketRow)) == 8
        and "cancelado" in dialog.status.text(),
    )
    print("cancelar ->", calls["cancel"], "| filas:", len(dialog.host.findChildren(td.TicketRow)),
          "| estado:", dialog.status.text())

    import os
    import tempfile
    shot = os.path.join(tempfile.gettempdir(), "preview_tickets.png")
    dialog.grab().save(shot)
    print("captura:", shot)

    ok = ok_drag and ok_print and ok_cancel
    print("TICKETS OK" if ok else "FALLO")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
