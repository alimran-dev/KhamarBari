import os
from typing import Dict, Any

try:
    import mysql.connector  # type: ignore
except Exception:
    mysql = None  # type: ignore


def _config() -> Dict[str, Any]:
    return {
        "host": os.getenv("DB_HOST", "127.0.0.1"),
        "port": int(os.getenv("DB_PORT", "3306")),
        "user": os.getenv("DB_USER", "root"),
        "password": os.getenv("DB_PASSWORD", ""),
        "database": os.getenv("DB_NAME"),  # may be None
    }


def get_connection():
    """Create a direct MySQL connection. Caller must .close()."""
    if "mysql" not in globals() or mysql is None:
        raise RuntimeError(
            "mysql-connector-python is not installed. Install it to enable DB access."
        )
    cfg = _config()
    conn = mysql.connector.connect(
        host=cfg["host"],
        port=cfg["port"],
        user=cfg["user"],
        password=cfg["password"],
        database=cfg.get("database") or None,
    )
    return conn
