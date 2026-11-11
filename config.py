import os
import sys
from pathlib import Path

from dotenv import load_dotenv


FROZEN = getattr(sys, "frozen", False)
RESOURCE_DIR = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
BASE_DIR = Path(sys.executable).resolve().parent if FROZEN else Path(__file__).resolve().parent

load_dotenv(BASE_DIR / ".env")

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")
NOMBRE_LOCAL = os.getenv("NOMBRE_LOCAL", "Mi Restaurante")
CACHE_DIR = BASE_DIR / "cache"

TICKET_WIDTH = int(os.getenv("TICKET_WIDTH", "32"))
PRINTER_MODE = os.getenv("PRINTER_MODE", "console")

PRINTER_MAC = os.getenv("PRINTER_MAC", "")
PRINTER_CHANNEL = int(os.getenv("PRINTER_CHANNEL") or 0)   # 0 = probar del 1 al 10
PAPER_MM = int(os.getenv("PAPER_MM", "58"))
PAPER_PX = 576 if PAPER_MM >= 80 else 384                  # puntos de ancho de la impresora
TICKET_HEADER = [x.strip() for x in os.getenv("TICKET_HEADER", "").split("|") if x.strip()]