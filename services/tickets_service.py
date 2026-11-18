"""Tickets del día para el kiosco (mismos datos que usa el panel web).

El panel los lee con la RPC `get_daily_report`, que es solo para
administradores. Para el kiosco, `deploy/tickets_kiosko.sql` crea dos RPC
para empleados activos: `get_today_tickets` (pedidos de hoy con productos y
adiciones) y `cancel_ticket` (cancelar devolviendo stock). Así la app no
necesita permisos de lectura sobre las tablas de ventas.
"""
import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

from postgrest.exceptions import APIError

from core.supabase_client import get_client
from services.printer_service import print_ticket
from services.ticket_renderer import render_ticket

# Colombia no tiene horario de verano: UTC-5 todo el año.
BOGOTA = timezone(timedelta(hours=-5))

_INSTALL_HINT = (
    "Falta activar la pantalla de tickets en Supabase: pega el archivo "
    "deploy/tickets_kiosko.sql en el SQL Editor y ejecútalo."
)


def _missing_function(error: APIError) -> bool:
    message = str(getattr(error, "message", "") or error).lower()
    return (
        "could not find the function" in message
        or "pgrst202" in message
        or "does not exist" in message
    )


@dataclass
class TicketAddon:
    name: str
    price: int


@dataclass
class TicketItem:
    name: str
    quantity: int
    unit_price: int
    addons: tuple[TicketAddon, ...] = ()


@dataclass
class Ticket:
    id: int
    number: int
    created_at: datetime
    total: int
    items: tuple[TicketItem, ...] = ()

    @property
    def time_label(self) -> str:
        return self.created_at.astimezone(BOGOTA).strftime("%H:%M")

    def summary(self, max_len: int = 150) -> str:
        """Productos en una línea: «2× Hamburguesa doble (+ Queso) · 1× Perro»."""
        partes = []
        for it in self.items:
            texto = f"{it.quantity}× {it.name}"
            if it.addons:
                texto += " (+ " + ", ".join(a.name for a in it.addons) + ")"
            partes.append(texto)
        texto = " · ".join(partes) or "Sin productos"
        if len(texto) <= max_len:
            return texto
        return texto[: max_len - 1].rstrip() + "…"


def _parse_when(value) -> datetime:
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return datetime.now(BOGOTA)


def _tickets_from_payload(data) -> list[Ticket]:
    """Convierte el JSON de get_today_tickets en objetos Ticket."""
    if isinstance(data, str):
        data = json.loads(data or "[]")
    if isinstance(data, dict):
        data = data.get("tickets") or []
    tickets = []
    for o in data or []:
        items = []
        for it in o.get("items") or []:
            addons = tuple(
                TicketAddon(
                    name=a.get("name") or "",
                    price=int(a.get("unit_price") or 0),
                )
                for a in it.get("addons") or []
            )
            items.append(
                TicketItem(
                    name=it.get("name") or "",
                    quantity=int(it.get("quantity") or 1),
                    unit_price=int(it.get("unit_price") or 0),
                    addons=addons,
                )
            )
        tickets.append(
            Ticket(
                id=int(o["id"]),
                number=int(o["ticket_number"]),
                created_at=_parse_when(o.get("created_at")),
                total=int(o.get("total") or 0),
                items=tuple(items),
            )
        )
    return tickets


def fetch_today_tickets() -> list[Ticket]:
    """Pedidos de hoy (hora de Colombia), con productos y adiciones."""
    try:
        resp = get_client().rpc("get_today_tickets").execute()
    except APIError as e:
        if _missing_function(e):
            raise ValueError(_INSTALL_HINT) from e
        raise ValueError(getattr(e, "message", str(e))) from e
    return _tickets_from_payload(resp.data)


def cancel_ticket(ticket: Ticket) -> int:
    """Borra el ticket del día (devuelve stock) y devuelve su número."""
    try:
        resp = get_client().rpc("cancel_ticket", {"p_order_id": ticket.id}).execute()
    except APIError as e:
        if _missing_function(e):
            raise ValueError(_INSTALL_HINT) from e
        raise ValueError(getattr(e, "message", str(e))) from e

    data = resp.data
    if isinstance(data, dict):
        return int(data.get("ticket_number") or ticket.number)
    return ticket.number


def reprint_ticket(ticket: Ticket) -> None:
    """Vuelve a imprimir un ticket con la misma imagen que el original."""
    lineas = [
        SimpleNamespace(
            quantity=it.quantity,
            product=SimpleNamespace(name=it.name, price=it.unit_price),
            addons=tuple(
                SimpleNamespace(name=a.name, price=a.price) for a in it.addons
            ),
        )
        for it in ticket.items
    ]
    imagen = render_ticket(
        ticket.number,
        lineas,
        ticket.total,
        when=ticket.created_at.astimezone(BOGOTA),
    )
    print_ticket(imagen)
