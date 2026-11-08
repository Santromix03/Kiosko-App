from core.supabase_client import get_client
from core.models import Category, Product
from core.models import Addon, Category, Product


def get_categories() -> list[Category]:
    rows = (
        get_client()
        .table("categories")
        .select("*")
        .order("sort_order")
        .execute()
        .data
    )
    return [Category(**r) for r in rows]


def get_products(category_id: int | None = None) -> list[Product]:
    query = get_client().table("menu_products").select("*")
    if category_id is not None:
        query = query.eq("category_id", category_id)
    rows = query.order("sort_order").execute().data
    return [Product(**r) for r in rows]

def get_addons() -> list[Addon]:
    client = get_client()
    rows = client.table("addons").select("*").order("id").execute().data
    links = client.table("addon_categories").select("addon_id, category_id").execute().data

    by_addon: dict[int, list[int]] = {}
    for link in links:
        by_addon.setdefault(link["addon_id"], []).append(link["category_id"])

    return [Addon(**r, category_ids=tuple(sorted(by_addon.get(r["id"], [])))) for r in rows]

