"""Pantalla «Tickets» del kiosco: pedidos del día, con reimprimir y cancelar.

Se abre con el botón Tickets de la pantalla de pedidos. Muestra una fila por
ticket (las más recientes abajo, igual que el panel) y a la izquierda de cada
una los botones Imprimir y Cancelar. La lista se desliza con el dedo, como la
cuadrícula de productos.
"""
from datetime import datetime

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtWidgets import (
    QDialog, QFrame, QHBoxLayout, QLabel, QMessageBox, QPushButton,
    QScrollArea, QVBoxLayout, QWidget,
)

from core.workers import run_async
from services.tickets_service import (
    BOGOTA, Ticket, cancel_ticket, fetch_today_tickets, reprint_ticket,
)
from ui.common.widgets import DragScroll, format_price

REFRESH_MS = 25000          # refresco automático de la lista


class TicketRow(QFrame):
    """Un ticket del día con sus dos acciones a la izquierda."""

    reprint = Signal(object)
    cancel = Signal(object)

    def __init__(self, ticket: Ticket):
        super().__init__()
        self.ticket = ticket
        self.setObjectName("TicketRow")
        self.setMinimumHeight(78)

        self.btn_print = QPushButton("Imprimir")
        self.btn_print.setObjectName("TicketPrint")
        self.btn_print.setFixedSize(104, 34)
        self.btn_print.setCursor(Qt.PointingHandCursor)
        self.btn_print.clicked.connect(lambda: self.reprint.emit(self.ticket))

        self.btn_cancel = QPushButton("Cancelar")
        self.btn_cancel.setObjectName("TicketCancel")
        self.btn_cancel.setFixedSize(104, 34)
        self.btn_cancel.setCursor(Qt.PointingHandCursor)
        self.btn_cancel.clicked.connect(lambda: self.cancel.emit(self.ticket))

        actions = QVBoxLayout()
        actions.setSpacing(6)
        actions.addWidget(self.btn_print)
        actions.addWidget(self.btn_cancel)

        number = QLabel(f"Ticket #{ticket.number}")
        number.setObjectName("TicketRowNumber")
        hour = QLabel(ticket.time_label)
        hour.setObjectName("TicketTime")
        total = QLabel(format_price(ticket.total))
        total.setObjectName("TicketRowTotal")

        head = QHBoxLayout()
        head.setSpacing(10)
        head.addWidget(number)
        head.addWidget(hour)
        head.addStretch()
        head.addWidget(total)

        items = QLabel(ticket.summary())
        items.setObjectName("TicketItems")
        items.setWordWrap(True)

        info = QVBoxLayout()
        info.setSpacing(4)
        info.addLayout(head)
        info.addWidget(items)
        info.addStretch()

        root = QHBoxLayout(self)
        root.setContentsMargins(12, 10, 14, 10)
        root.setSpacing(14)
        root.addLayout(actions)
        root.addLayout(info, 1)


class ConfirmCancelDialog(QDialog):
    """Confirmación táctil antes de borrar un ticket (no se puede deshacer)."""

    def __init__(self, ticket: Ticket, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Cancelar ticket")
        self.setModal(True)
        self.setObjectName("TicketsDialog")
        self.setFixedWidth(430)

        title = QLabel(f"¿Cancelar el ticket #{ticket.number}?")
        title.setObjectName("AddonTitle")
        title.setWordWrap(True)
        title.setAlignment(Qt.AlignCenter)

        detail = QLabel(
            f"{format_price(ticket.total)} · {ticket.summary(90)}\n\n"
            "El pedido se borra del día y el stock vuelve a la carta. "
            "Esta acción no se puede deshacer."
        )
        detail.setObjectName("ConfirmText")
        detail.setWordWrap(True)
        detail.setAlignment(Qt.AlignCenter)

        back = QPushButton("No, volver")
        back.setObjectName("ClearButton")
        back.setMinimumHeight(48)
        back.clicked.connect(self.reject)

        yes = QPushButton("Sí, cancelar")
        yes.setObjectName("ConfirmButton")
        yes.setMinimumHeight(48)
        yes.clicked.connect(self.accept)

        buttons = QHBoxLayout()
        buttons.setSpacing(10)
        buttons.addWidget(back)
        buttons.addWidget(yes, 1)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(10)
        layout.addWidget(title)
        layout.addWidget(detail)
        layout.addSpacing(4)
        layout.addLayout(buttons)


class TicketsDialog(QDialog):
    """Lista de los pedidos de hoy con reimpresión y cancelación."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Tickets del día")
        self.setObjectName("TicketsDialog")
        self.setModal(True)
        self.setWindowFlag(Qt.FramelessWindowHint)   # pantalla completa del kiosco
        self.resize(776, 468)

        self._alive = True
        self._loading = False
        self._busy = False
        self._asking = False
        self._notice = ""

        title = QLabel("Tickets del día")
        title.setObjectName("TicketsTitle")

        day = QLabel(datetime.now(BOGOTA).strftime("%d/%m/%Y"))
        day.setObjectName("TicketTime")

        back = QPushButton("Volver")
        back.setObjectName("TicketsBack")
        back.setFixedHeight(40)
        back.setMinimumWidth(96)
        back.setCursor(Qt.PointingHandCursor)
        back.clicked.connect(self.reject)

        self.btn_refresh = QPushButton("Actualizar")
        self.btn_refresh.setObjectName("TicketsRefresh")
        self.btn_refresh.setFixedHeight(40)
        self.btn_refresh.setMinimumWidth(112)
        self.btn_refresh.setCursor(Qt.PointingHandCursor)
        self.btn_refresh.clicked.connect(self._reload)

        top = QHBoxLayout()
        top.setSpacing(10)
        top.addWidget(back)
        top.addWidget(title, 1)
        top.addWidget(day)
        top.addWidget(self.btn_refresh)

        self.status = QLabel()
        self.status.setObjectName("TicketsStatus")
        self.status.setWordWrap(True)

        self.host = QWidget()
        self.rows = QVBoxLayout(self.host)
        self.rows.setContentsMargins(0, 0, 0, 0)
        self.rows.setSpacing(8)
        self.rows.setAlignment(Qt.AlignTop)

        self.scroll = DragScroll(Qt.Vertical)
        self.scroll.setObjectName("TicketsScroll")
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QScrollArea.NoFrame)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setWidget(self.host)
        self.scroll.watch_host(self.host)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 14)
        layout.setSpacing(8)
        layout.addLayout(top)
        layout.addWidget(self.status)
        layout.addWidget(self.scroll, 1)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._reload)
        self.timer.start(REFRESH_MS)

        self._reload()

    # ---------- carga ----------
    def _reload(self, *_):
        if not self._alive or self._loading or self._busy or self._asking:
            return
        self._loading = True
        self.btn_refresh.setEnabled(False)
        self.status.setText("Cargando pedidos de hoy…")
        run_async(fetch_today_tickets, self._on_loaded, self._on_load_error)

    def _on_loaded(self, tickets):
        self._loading = False
        if not self._alive:
            return
        self.btn_refresh.setEnabled(True)
        self._fill(tickets)
        if self._notice:
            self.status.setText(self._notice)
            self._notice = ""
        elif tickets:
            total = sum(t.total for t in tickets)
            self.status.setText(
                f"{len(tickets)} pedido{'s' if len(tickets) != 1 else ''} hoy "
                f"· {format_price(total)} en total"
            )
        else:
            self.status.setText("Hoy todavía no hay pedidos.")

    def _on_load_error(self, trace):
        self._loading = False
        if not self._alive:
            return
        self.btn_refresh.setEnabled(True)
        self.status.setText(f"No se pudieron leer los tickets: {_last_line(trace)}")

    def _fill(self, tickets):
        while self.rows.count():
            item = self.rows.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        if not tickets:
            empty = QLabel("Aún no hay tickets hoy.\nLos pedidos nuevos aparecen aquí solos.")
            empty.setObjectName("EmptyLabel")
            empty.setAlignment(Qt.AlignCenter)
            self.rows.addWidget(empty)
            return
        for ticket in tickets:
            row = TicketRow(ticket)
            row.reprint.connect(self._reprint)
            row.cancel.connect(self._cancel)
            self.scroll.watch(row)
            self.scroll.watch(row.btn_print)
            self.scroll.watch(row.btn_cancel)
            self.rows.addWidget(row)

    # ---------- acciones ----------
    def _reprint(self, ticket: Ticket):
        if not self._alive or self._busy or self.scroll.dragging:
            return
        self._set_busy(True)
        self.status.setText(f"Imprimiendo el ticket #{ticket.number}…")
        run_async(reprint_ticket, self._on_reprinted, self._on_action_error, ticket)

    def _on_reprinted(self, _):
        self._set_busy(False)
        if not self._alive:
            return
        self._notice = "Ticket reimpreso. Recoge el papel de la impresora."
        self.status.setText(self._notice)
        self._notice = ""

    def _cancel(self, ticket: Ticket):
        if not self._alive or self._busy or self.scroll.dragging:
            return
        self._asking = True
        try:
            accepted = ConfirmCancelDialog(ticket, self).exec()
        finally:
            self._asking = False
        if not accepted:
            return
        self._set_busy(True)
        self.status.setText(f"Cancelando el ticket #{ticket.number}…")
        run_async(cancel_ticket, self._on_cancelled, self._on_action_error, ticket)

    def _on_cancelled(self, number):
        self._set_busy(False)
        if not self._alive:
            return
        self._notice = f"Ticket #{number} cancelado. El stock volvió a la carta."
        self._reload()

    def _on_action_error(self, trace):
        self._set_busy(False)
        if not self._alive:
            return
        message = _last_line(trace)
        self.status.setText(message)
        QMessageBox.warning(
            self, "No se pudo completar",
            message if len(message) < 300 else message[:300] + "…",
        )

    def _set_busy(self, busy: bool):
        self._busy = busy
        self.btn_refresh.setEnabled(not busy and not self._loading)
        for row in self.host.findChildren(TicketRow):
            row.btn_print.setEnabled(not busy)
            row.btn_cancel.setEnabled(not busy)

    def done(self, result):
        self._alive = False
        self.timer.stop()
        super().done(result)


def _last_line(trace: str) -> str:
    """Motivo corto (última línea no vacía del traceback) para mostrar al usuario."""
    lines = [ln.strip() for ln in (trace or "").splitlines() if ln.strip()]
    line = lines[-1] if lines else "Error desconocido"
    for prefix in ("ValueError: ", "APIError: ", "postgrest.exceptions.APIError: "):
        if line.startswith(prefix):
            return line[len(prefix):]
    return line
