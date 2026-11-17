from core.supabase_client import get_client


def sign_in(email: str, password: str) -> dict:
    """Valida al empleado con Supabase Auth y lee su perfil de `employees`.

    Las cuentas se crean desde el panel con la función Edge `create-employee`
    (ya confirmadas); la contraseña la comprueba Auth en el servidor. El rol
    lo decide la base de datos con `my_role()` (tablas admins/employees), y
    las cuentas desactivadas o sin acceso se rechazan aquí mismo.
    """
    email = (email or "").strip().lower()
    if not email or not password:
        raise ValueError("Escribe tu correo y contraseña")

    client = get_client()
    try:
        res = client.auth.sign_in_with_password(
            {"email": email, "password": password}
        )
    except Exception as exc:
        text = str(exc).lower()
        if "invalid login credentials" in text:
            raise ValueError("Correo o contraseña incorrectos")
        if "email not confirmed" in text:
            raise ValueError("Este correo aún no está confirmado en el sistema")
        raise ValueError("No se pudo iniciar sesión: " + str(exc))

    user = getattr(res, "user", None)
    if user is None or not getattr(user, "id", None):
        raise ValueError("Correo o contraseña incorrectos")

    # Rol oficial según la base (igual que usa el panel de administración)
    role = _my_role(client)
    if role not in ("admin", "employee"):
        try:
            client.auth.sign_out()
        except Exception:
            pass
        if role == "inactive":
            raise ValueError("Tu cuenta está desactivada; habla con el administrador")
        raise ValueError("Esta cuenta no tiene acceso al kiosco")

    # Perfil del empleado en la tabla `employees` (la crea la Edge Function
    # junto con la cuenta). Si aún no existiera, se usa lo de la cuenta.
    name = ""
    try:
        prof = (
            client.table("employees")
            .select("full_name, role")
            .eq("id", user.id)
            .limit(1)
            .execute()
        )
        rows = getattr(prof, "data", None) or []
        if rows:
            name = (rows[0].get("full_name") or "").strip()
    except Exception:
        pass

    if not name:
        meta = getattr(user, "user_metadata", None) or {}
        name = (meta.get("full_name") or "").strip()
    if not name:
        name = email.split("@")[0].capitalize()

    return {
        "id": user.id,
        "email": getattr(user, "email", None) or email,
        "rol": "admin" if role == "admin" else "empleado",
        "name": name,
    }


def _my_role(client) -> str | None:
    """Devuelve 'admin' | 'employee' | 'inactive' | None según la base de datos."""
    try:
        data = getattr(client.rpc("my_role").execute(), "data", None)
    except Exception:
        return None
    if isinstance(data, str):
        return data or None
    if isinstance(data, list) and data:
        first = data[0]
        if isinstance(first, str):
            return first or None
        if isinstance(first, dict):
            return first.get("my_role")
    return None
