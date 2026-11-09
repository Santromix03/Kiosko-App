import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Con PyInstaller hay dos carpetas distintas:
#   RESOURCE_DIR = recursos empaquetados (assets, estilos), solo lectura
#   BASE_DIR     = junto al ejecutable (.env, cache, tickets), editable
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