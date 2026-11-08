from dataclasses import dataclass


@dataclass
class Category:
    id: int
    name: str
    sort_order: int = 0
    active: bool = True


@dataclass
class Product:
    id: int
    category_id: int
    name: str
    price: int
    description: str | None = None
    image_url: str | None = None
    available: bool = True
    sort_order: int = 0
    max_qty: int | None = None   # None = sin control de stock


@dataclass
class Addon:
    id: int
    name: str
    price: int
    stock: int = 0
    active: bool = True
    category_ids: tuple[int, ...] = ()


@dataclass
class CartItem:
    product: Product
    quantity: int = 1
    addons: tuple[Addon, ...] = ()

    @property
    def key(self) -> tuple:
        """Identifica la línea: mismo producto + mismas adiciones."""
        return (self.product.id, tuple(sorted(a.id for a in self.addons)))

    @property
    def unit_price(self) -> int:
        return self.product.price + sum(a.price for a in self.addons)

    @property
    def subtotal(self) -> int:
        return self.unit_price * self.quantity