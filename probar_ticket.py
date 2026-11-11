from core.models import Addon, CartItem, Product
from services.printer_service import print_ticket
from services.ticket_renderer import render_ticket

p1 = Product(1, 1, "Hamburguesa clásica", 15000)
p2 = Product(2, 2, "Gaseosa postobon", 3000)
aloe = Addon(1, "Aloe", 3500, 10)
items = [CartItem(p1, 2, (aloe,)), CartItem(p2, 1)]
total = sum(i.subtotal for i in items)

img = render_ticket(7, items, total)
img.save("ticket_prueba.png")
print("Guardado ticket_prueba.png")

if input("¿Imprimir con PRINTER_MODE actual? (s/n) ").lower() == "s":
    print_ticket(img)