"""Resolución centralizada de la base URL del servidor Laya (Jev) para los scripts.

Orden de prioridad:
1. Variable de entorno `LAYA_BASE` (si ya está exportada).
2. Valor `LAYA_BASE=` en el fichero `.env` de la raíz del proyecto (si existe).
3. Default `http://localhost:8432`.

Stdlib-only; los scripts importan `BASE` y `URL` de aquí para no duplicar el parser.
La IP de la intranet vive en `.env` (git-ignored), nunca en código versionado.
"""
import os

DEFAULT_BASE = "http://localhost:8432"
_ENV_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")


def _from_env_file() -> str | None:
    try:
        with open(_ENV_FILE, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, value = line.partition("=")
                if key.strip() == "LAYA_BASE":
                    return value.strip().strip('"').strip("'")
    except FileNotFoundError:
        pass
    return None


def resolve_base() -> str:
    return (
        os.environ.get("LAYA_BASE")
        or _from_env_file()
        or DEFAULT_BASE
    )


BASE = resolve_base().rstrip("/")
URL = f"{BASE}/v1/systemone"
HEALTH = f"{BASE}/health"
