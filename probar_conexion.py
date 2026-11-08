from core.cart import Cart
from services.catalog_service import get_products
from services.order_service import create_order

productos = get_products()
cart = Cart()
cart.add(productos[0], 2)
cart.add(productos[1])

resultado = create_order(cart)
print("Ticket #", resultado.ticket_number)
print("Total:", resultado.total)