import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")
NOMBRE_LOCAL = os.getenv("NOMBRE_LOCAL", "Mi Restaurante")
CACHE_DIR = BASE_DIR / "cache"

TICKET_WIDTH = int(os.getenv("TICKET_WIDTH", "32"))
PRINTER_MODE = os.getenv("PRINTER_MODE", "console")

if not SUPABASE_URL or not SUPABASE_ANON_KEY:
    raise RuntimeError("Falta SUPABASE_URL o SUPABASE_ANON_KEY en el archivo .env")