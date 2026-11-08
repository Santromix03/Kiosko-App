import hashlib
from pathlib import Path
from urllib.parse import urlparse

import httpx

import config


def _path_for(url: str) -> Path:
    suffix = Path(urlparse(url).path).suffix or ".img"
    return config.CACHE_DIR / (hashlib.sha1(url.encode()).hexdigest() + suffix)


def cached_image_path(url: str | None) -> Path | None:
    """Ruta de la imagen si ya está descargada. Nunca usa la red (seguro para la UI)."""
    if not url:
        return None
    path = _path_for(url)
    return path if path.exists() else None


def download_image(url: str | None) -> None:
    """Descarga la imagen al caché. Usar solo en un hilo, no en la UI."""
    if not url or cached_image_path(url):
        return
    config.CACHE_DIR.mkdir(exist_ok=True)
    try:
        resp = httpx.get(url, timeout=10, follow_redirects=True)
        resp.raise_for_status()
        _path_for(url).write_bytes(resp.content)
    except Exception:
        pass  # sin imagen, la tarjeta muestra "Sin imagen"