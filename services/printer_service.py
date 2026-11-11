import socket
import time
from datetime import datetime

from PIL import Image, ImageOps

import config

CHUNK = 512          # bytes por envío; si la impresora pierde líneas, baja a 256
CHUNK_DELAY = 0.02   # segundos entre envíos
BAND = 256           # filas de imagen por comando
_channel_cache = None


def image_to_raster(img: Image.Image) -> bytes:
    """Convierte la imagen en comandos ESC/POS (GS v 0), por franjas."""
    bw = ImageOps.invert(img.convert("L")).point(lambda p: 255 if p > 100 else 0, mode="1")
    row_bytes = bw.width // 8

    out = bytearray(b"\x1b@")                       # inicializar
    for top in range(0, bw.height, BAND):
        chunk = bw.crop((0, top, bw.width, min(top + BAND, bw.height)))
        h = chunk.height
        out += b"\x1d\x76\x30\x00" + bytes([row_bytes & 0xFF, row_bytes >> 8, h & 0xFF, h >> 8])
        out += chunk.tobytes()
    out += b"\x1b\x64\x04"                          # avanza 4 líneas para poder cortar
    return bytes(out)


def _send_bluetooth(data: bytes) -> None:
    global _channel_cache
    if not hasattr(socket, "AF_BLUETOOTH"):
        raise RuntimeError("Este Python no incluye soporte Bluetooth (socket.AF_BLUETOOTH)")
    if not config.PRINTER_MAC:
        raise RuntimeError("Falta PRINTER_MAC en el .env")

    if config.PRINTER_CHANNEL:
        channels = [config.PRINTER_CHANNEL]
    else:
        channels = ([_channel_cache] if _channel_cache else []) + list(range(1, 11))

    last_error = None
    for ch in channels:
        s = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
        s.settimeout(10)
        try:
            s.connect((config.PRINTER_MAC, ch))
        except OSError as e:
            last_error = e
            s.close()
            continue

        try:
            _channel_cache = ch
            print(f"Impresora conectada por el canal {ch}")
            for i in range(0, len(data), CHUNK):
                s.sendall(data[i:i + CHUNK])
                time.sleep(CHUNK_DELAY)
            time.sleep(2)                           # deja que termine de imprimir antes de cerrar
            return
        finally:
            s.close()

    raise RuntimeError(f"No se pudo conectar a la impresora {config.PRINTER_MAC}: {last_error}")


def print_ticket(img: Image.Image) -> None:
    mode = config.PRINTER_MODE
    if mode == "file":
        out_dir = config.BASE_DIR / "tickets"
        out_dir.mkdir(exist_ok=True)
        img.save(out_dir / datetime.now().strftime("ticket_%Y%m%d_%H%M%S.png"))
    elif mode == "bluetooth":
        _send_bluetooth(image_to_raster(img))
    else:
        raise ValueError(f"PRINTER_MODE desconocido: {mode} (usa 'file' o 'bluetooth')")