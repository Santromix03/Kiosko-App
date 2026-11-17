from core.supabase_client import get_client


def sign_in(email: str, password: str) -> dict:
    """Valida el empleado contra la tabla `empleados` (vía RPC verificar_empleado).

    La verificación del hash ocurre en el servidor con pgcrypto; al cliente
    nunca llegan contraseñas, solo id, email y rol.
    """
    email = (email or "").strip().lower()
    if not email or not password:
        raise ValueError("Escribe tu correo y contraseña")

    res = get_client().rpc(
        "verificar_empleado", {"p_email": email, "p_password": password}
    ).execute()
    rows = getattr(res, "data", None) or []
    if not rows:
        raise ValueError("Correo o contraseña incorrectos")

    row = rows[0]
    name = (row.get("email") or "empleado").split("@")[0].capitalize()
    return {
        "id": row.get("id"),
        "email": row.get("email"),
        "rol": row.get("rol", "empleado"),
        "name": name,
    }
