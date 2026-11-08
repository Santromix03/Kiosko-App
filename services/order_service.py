from dataclasses import dataclass

from postgrest.exceptions import APIError

from core.cart import Cart
from core.supabase_client import get_client


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
    return OrderResult(
        ticket_number=row["out_ticket"],
        total=row["out_total"],
    )