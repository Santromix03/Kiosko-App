"""Turnos: el kiosco abre el turno del empleado al iniciar sesión y lo cierra
al salir. Usa los mismos RPC que la página de administración (start_shift /
end_shift): así el panel «Roles y turnos» ve al empleado de la app igual que
los que entran por la web, en «En turno ahora».

- start_shift: valida que el empleado esté activo, cierra turnos olvidados
  (>14 h) y devuelve el turno abierto (el nuevo o el que ya tenía).
- end_shift: marca ended_at = now() y ended_by = el propio empleado (el
  servidor usa auth.uid(); aquí no se envía nada sensible).
"""
from core.supabase_client import get_client


def start_shift() -> dict | None:
    """Abre (o recupera) el turno del empleado autenticado en el kiosco."""
    res = get_client().rpc("start_shift").execute()
    data = getattr(res, "data", None)
    if isinstance(data, list):
        return data[0] if data else None
    return data if isinstance(data, dict) else None


def end_shift() -> None:
    """Cierra el turno abierto del empleado autenticado."""
    get_client().rpc("end_shift").execute()
