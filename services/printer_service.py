from datetime import datetime

import config


def _money(value: int) -> str:
    return "$" + f"{value:,}".replace(",", ".")


def _line(left: str, right: str, width: int) -> str:
    space = width - len(left) - len(right)
    if space < 1:
        left = left[: max(width - len(right) - 1, 1)]
        space = 1
    return left + " " * space + right


def build_ticket_text(ticket_number: int, items, total: int, width: int | None = None) -> str:
    width = width or config.TICKET_WIDTH
    sep = "-" * width
    lines = [
        config.NOMBRE_LOCAL.center(width),
        sep,
        f"TICKET #{ticket_number}".center(width),
        datetime.now().strftime("%d/%m/%Y %H:%M").center(width),
        sep,
    ]
    for it in items:
        lines.append(_line(f"{it.quantity}x {it.product.name}",
                           _money(it.product.price * it.quantity), width))
        for a in it.addons:
            lines.append(_line(f"  + {a.name}", _money(a.price * it.quantity), width))
    return "\n".join(lines)


def print_ticket(text: str) -> None:
    mode = config.PRINTER_MODE
    if mode == "file":
        out_dir = config.BASE_DIR / "tickets"
        out_dir.mkdir(exist_ok=True)
        name = datetime.now().strftime("ticket_%Y%m%d_%H%M%S.txt")
        (out_dir / name).write_text(text, encoding="utf-8")
    elif mode == "console":
        print(text)
    elif mode == "escpos":
        raise NotImplementedError("La impresora térmica se configura en la Raspberry Pi")
    else:
        raise ValueError(f"PRINTER_MODE desconocido: {mode}")