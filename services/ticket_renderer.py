from datetime import datetime

from PIL import Image, ImageDraw, ImageFont

import config

MARGIN = 12


def _money(value: int) -> str:
    return "$" + f"{value:,}".replace(",", ".")


def _font(bold: bool, size: float):
    name = "Poppins-Bold.ttf" if bold else "Poppins-Regular.ttf"
    try:
        return ImageFont.truetype(str(config.RESOURCE_DIR / "assets" / "fonts" / name), int(size))
    except OSError:
        return ImageFont.load_default()


def _wrap(draw, text: str, font, max_w: float) -> list[str]:
    lines, cur = [], ""
    for word in text.split():
        test = f"{cur} {word}".strip()
        if not cur or draw.textlength(test, font=font) <= max_w:
            cur = test
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines or [""]


def _load_logo(max_w: int, max_h: int):
    """Logo opcional en assets/logo.png (negro sobre blanco o transparente)."""
    path = config.RESOURCE_DIR / "assets" / "logo.png"
    if not path.exists():
        return None
    img = Image.open(path).convert("RGBA")
    bg = Image.new("RGBA", img.size, (255, 255, 255, 255))
    bg.alpha_composite(img)
    gray = bg.convert("L")
    scale = min(max_w / gray.width, max_h / gray.height)
    gray = gray.resize((max(1, int(gray.width * scale)), max(1, int(gray.height * scale))),
                       Image.Resampling.LANCZOS)
    return gray.convert("1").convert("L")      # tramado para que la térmica lo imprima bien


def render_ticket(ticket_number: int, items, total: int) -> Image.Image:
    W = config.PAPER_PX
    s = W / 384                                 # escala para papel de 80 mm

    f_small = _font(False, 19 * s)
    f_norm = _font(False, 22 * s)
    f_bold = _font(True, 22 * s)
    f_big = _font(True, 30 * s)

    img = Image.new("L", (W, 6000), 255)
    d = ImageDraw.Draw(img)
    y = 10

    def lh(font) -> int:
        return int(getattr(font, "size", 12) * 1.45)

    def center(text, font, gap=0):
        nonlocal y
        for part in _wrap(d, text, font, W - 2 * MARGIN):
            x = (W - d.textlength(part, font=font)) / 2
            d.text((x, y), part, font=font, fill=0)
            y += lh(font)
        y += gap

    def hline(thick=2, gap=10):
        nonlocal y
        y += gap // 2
        d.rectangle([MARGIN, y, W - MARGIN, y + thick - 1], fill=0)
        y += thick + gap // 2

    def row(left, right, font):
        nonlocal y
        d.text((MARGIN, y), left, font=font, fill=0)
        d.text((W - MARGIN - d.textlength(right, font=font), y), right, font=font, fill=0)
        y += lh(font)

    def label_value(label, value, value_font):
        nonlocal y
        d.text((MARGIN, y), label, font=f_norm, fill=0)
        d.text((MARGIN + d.textlength(label, font=f_norm), y), value, font=value_font, fill=0)
        y += lh(f_norm)

    # --- Logo y encabezado ---
    logo = _load_logo(int(W * 0.62), int(150 * s))
    if logo:
        img.paste(logo, ((W - logo.width) // 2, y))
        y += logo.height + 8
        center(config.NOMBRE_LOCAL.upper(), f_bold)
    else:
        center(config.NOMBRE_LOCAL.upper(), f_big)
    for line in config.TICKET_HEADER:
        center(line, f_norm)
    hline(3, 14)

    # --- Fecha y pedido ---
    label_value("Fecha: ", datetime.now().strftime("%Y-%m-%d %H:%M:%S"), f_norm)
    label_value("Pedido: ", f"#{ticket_number}", f_bold)

    # --- Caja PREFACTURA ---
    y += 8
    box_h = lh(f_big) + 14
    d.rectangle([MARGIN, y, W - MARGIN, y + box_h], outline=0, width=4)
    title = "PREFACTURA"
    d.text(((W - d.textlength(title, font=f_big)) / 2, y + 7), title, font=f_big, fill=0)
    y += box_h + 14

    # --- Tabla ---
    hline(2)
    qty_w, val_w = int(54 * s), int(112 * s)
    prod_x = MARGIN + qty_w
    prod_w = W - 2 * MARGIN - qty_w - val_w
    d.text((MARGIN, y), "Cant", font=f_bold, fill=0)
    d.text((prod_x, y), "Producto", font=f_bold, fill=0)
    d.text((W - MARGIN - d.textlength("Valor", font=f_bold), y), "Valor", font=f_bold, fill=0)
    y += lh(f_bold)
    hline(2)

    for it in items:
        top = y
        d.text((MARGIN, top), str(it.quantity), font=f_norm, fill=0)
        value = _money(it.product.price * it.quantity)
        d.text((W - MARGIN - d.textlength(value, font=f_norm), top), value, font=f_norm, fill=0)
        for ln in _wrap(d, it.product.name.upper(), f_norm, prod_w):
            d.text((prod_x, y), ln, font=f_norm, fill=0)
            y += lh(f_norm)
        for a in it.addons:
            for k, ln in enumerate(_wrap(d, f"+ {a.name}", f_small, prod_w)):
                d.text((prod_x, y), ln, font=f_small, fill=0)
                if k == 0:
                    av = _money(a.price * it.quantity)
                    d.text((W - MARGIN - d.textlength(av, font=f_small), y), av, font=f_small, fill=0)
                y += lh(f_small)
        y += 6

    # --- Totales ---
    hline(2)
    row("Subtotal:", _money(total), f_norm)
    y += 4
    row("TOTAL:", _money(total), f_big)
    hline(3, 16)

    # --- Pie ---
    center("Paga en caja con este ticket", f_bold, gap=2)
    center("¡Gracias por tu compra!", f_norm)
    y += 40
    return img.crop((0, 0, W, y))

