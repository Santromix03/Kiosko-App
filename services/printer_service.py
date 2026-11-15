import os
import re
import shutil
import socket
import subprocess
import tempfile
import time
from datetime import datetime

from PIL import Image, ImageOps

import config

CHUNK = 512          # bytes por envío; si la impresora pierde líneas, baja a 256
CHUNK_DELAY = 0.02   # segundos entre envíos
BAND = 256           # filas de imagen por comando
_channel_cache = None

# Script que corre con el python del sistema (el de la Pi sí trae Bluetooth)
# cuando el python congelado no lo incluye.
_BT_PROXY_SCRIPT = r"""
import socket, sys, time

mac, path, channels = sys.argv[1], sys.argv[2], [int(c) for c in sys.argv[3].split(",")]
data = open(path, "rb").read()
errors = []
for ch in channels:
    s = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
    s.settimeout(10)
    try:
        s.connect((mac, ch))
    except OSError as e:
        errors.append(f"canal {ch}: {e.strerror or e}")
        s.close()
        continue
    print(f"Impresora conectada por el canal {ch}")
    for i in range(0, len(data), 512):
        s.sendall(data[i:i + 512])
        time.sleep(0.02)
    time.sleep(2)                       # deja que termine de imprimir antes de cerrar
    s.close()
    sys.exit(0)
print("No se pudo conectar a la impresora. " + "; ".join(errors[-3:]), file=sys.stderr)
sys.exit(1)
"""


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


def _find_system_python() -> str:
    for candidate in ("/usr/bin/python3", shutil.which("python3"), shutil.which("python")):
        if candidate and os.path.isfile(candidate) and os.access(candidate, os.X_OK):
            return candidate
    raise RuntimeError(
        "Este ejecutable no incluye soporte Bluetooth y no se encontró un "
        "python del sistema para delegar la impresión"
    )


def _send_bluetooth_proxy(data: bytes) -> None:
    """El python congelado no trae sockets Bluetooth: delega al python del sistema."""
    global _channel_cache
    if not config.PRINTER_MAC:
        raise RuntimeError("Falta PRINTER_MAC en el .env")
    py = _find_system_python()

    if config.PRINTER_CHANNEL:
        channels = [config.PRINTER_CHANNEL]
    else:
        channels = ([_channel_cache] if _channel_cache else []) + list(range(1, 11))

    fd, path = tempfile.mkstemp(suffix=".raster")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
        r = subprocess.run(
            [py, "-c", _BT_PROXY_SCRIPT, config.PRINTER_MAC, path,
             ",".join(map(str, channels))],
            capture_output=True, text=True, timeout=len(channels) * 12 + 30,
        )
    finally:
        os.unlink(path)

    out, err = (r.stdout or "").strip(), (r.stderr or "").strip()
    m = re.search(r"canal (\d+)", out)
    if m:
        _channel_cache = int(m.group(1))
    if r.returncode != 0:
        raise RuntimeError(err.splitlines()[-1] if err else f"El proceso terminó con error: {out}")


def _send_bluetooth(data: bytes) -> None:
    global _channel_cache
    if not (hasattr(socket, "AF_BLUETOOTH") and hasattr(socket, "BTPROTO_RFCOMM")):
        _send_bluetooth_proxy(data)          # python sin Bluetooth (release de CI)
        return
    if not config.PRINTER_MAC:
        raise RuntimeError("Falta PRINTER_MAC en el .env")

    if config.PRINTER_CHANNEL:
        channels = [config.PRINTER_CHANNEL]
    else:
        channels = ([_channel_cache] if _channel_cache else []) + list(range(1, 11))

    last_error = None
    channel_errors = []
    for ch in channels:
        s = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
        s.settimeout(10)
        try:
            s.connect((config.PRINTER_MAC, ch))
        except OSError as e:
            last_error = e
            channel_errors.append(f"canal {ch}: {e.strerror or e}")
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

    raise RuntimeError(
        f"No se pudo conectar a la impresora {config.PRINTER_MAC} "
        f"(probé canales {channels[0]}-{channels[-1]}). "
        + "; ".join(channel_errors[-3:])          # últimos 3 para no saturar la pantalla
    )


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