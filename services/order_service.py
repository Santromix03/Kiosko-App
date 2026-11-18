from dataclasses import dataclass

from postgrest.exceptions import APIError

from core.cart import Cart
from core.supabase_client import get_client
from services.tickets_service import save_order_notes


@dataclass
class OrderResult:
    ticket_number: int
    total: int


def create_order(cart: Cart) -> OrderResult:
    if cart.is_empty:
        raise ValueError("El carrito está vacío")

    try:
        resp = get_client().rpc(
            "create_order", {"p_items": cart.to_order_payload()}
        ).execute()
    except APIError as e:
        raise ValueError(getattr(e, "message", str(e))) from e

    row = resp.data[0] if isinstance(resp.data, list) else resp.data
    result = OrderResult(
        ticket_number=row["out_ticket"],
        total=row["out_total"],
    )

    # Las observaciones ya van impresas en el ticket; guardarlas es solo para
    # poder reimprimirlo después. Si falta el SQL, el pedido sigue valiendo.
    try:
        save_order_notes(result.ticket_number, cart.items)
    except Exception:
        pass
    return result