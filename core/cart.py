from core.models import Addon, CartItem, Product

MAX_PER_PRODUCT = 20


class Cart:
    def __init__(self):
        self._items: dict[tuple, CartItem] = {}

    # ---------- límites ----------
    @staticmethod
    def limit_for(product: Product) -> int:
        if product.max_qty is None:      # sin receta = sin control de stock
            return MAX_PER_PRODUCT
        return min(MAX_PER_PRODUCT, product.max_qty)

    def product_qty(self, product_id: int) -> int:
        """Unidades de un producto en todo el carrito (con o sin adiciones)."""
        return sum(i.quantity for i in self._items.values() if i.product.id == product_id)

    def addon_usage(self, addon_id: int) -> int:
        return sum(i.quantity for i in self._items.values()
                   if any(a.id == addon_id for a in i.addons))

    def addon_left(self, addon: Addon) -> int:
        """Unidades de la adición que aún se pueden pedir."""
        return addon.stock - self.addon_usage(addon.id)

    def blocked_reason(self, product: Product, addons=()) -> str | None:
        limit = self.limit_for(product)
        if self.product_qty(product.id) >= limit:
            return f"Solo hay {limit} de {product.name}"
        for a in addons:
            if self.addon_left(a) < 1:
                return f"Ya no quedan más unidades de {a.name}"
        return None

    def can_add(self, product: Product, addons=()) -> bool:
        return self.blocked_reason(product, addons) is None

    # ---------- edición ----------
    def add(self, product: Product, addons=()) -> bool:
        if self.blocked_reason(product, addons):
            return False
        item = CartItem(product, 1, tuple(addons))
        existing = self._items.get(item.key)
        if existing:
            existing.quantity += 1
        else:
            self._items[item.key] = item
        return True

    def remove_one(self, key: tuple) -> None:
        item = self._items.get(key)
        if item is None:
            return
        item.quantity -= 1
        if item.quantity <= 0:
            del self._items[key]

    def remove(self, key: tuple) -> None:
        self._items.pop(key, None)

    def clear(self) -> None:
        self._items.clear()

    def sync(self, products: list[Product], addons: list[Addon]) -> bool:
        """Refresca productos y adiciones del carrito con datos nuevos y ajusta
        cantidades al stock. Devuelve True si tuvo que reducir o quitar algo."""
        fresh_p = {p.id: p for p in products}
        fresh_a = {a.id: a for a in addons}
        used_p: dict[int, int] = {}
        used_a: dict[int, int] = {}
        kept: dict[tuple, CartItem] = {}
        changed = False

        for key, item in self._items.items():
            product = fresh_p.get(item.product.id)
            line_addons = [fresh_a.get(a.id) for a in item.addons]
            if product is None or any(
                a is None or product.category_id not in a.category_ids for a in line_addons
            ):
                changed = True
                continue

            allowed = min(
                item.quantity,
                self.limit_for(product) - used_p.get(product.id, 0),
                *[a.stock - used_a.get(a.id, 0) for a in line_addons],
            )
            if allowed <= 0:
                changed = True
                continue
            if allowed < item.quantity:
                changed = True

            item.product = product
            item.addons = tuple(line_addons)
            item.quantity = allowed
            used_p[product.id] = used_p.get(product.id, 0) + allowed
            for a in line_addons:
                used_a[a.id] = used_a.get(a.id, 0) + allowed
            kept[key] = item

        self._items = kept
        return changed

    # ---------- consulta ----------
    @property
    def items(self) -> list[CartItem]:
        return list(self._items.values())

    @property
    def total(self) -> int:
        return sum(i.subtotal for i in self._items.values())

    @property
    def count(self) -> int:
        return sum(i.quantity for i in self._items.values())

    @property
    def is_empty(self) -> bool:
        return not self._items

    def to_order_payload(self) -> list[dict]:
        """Formato que espera create_order en Supabase."""
        return [
            {"product_id": i.product.id, "qty": i.quantity, "addons": [a.id for a in i.addons]}
            for i in self._items.values()
        ]