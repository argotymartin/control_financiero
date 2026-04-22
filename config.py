"""Configuracion centralizada.

Carga vars entorno una sola vez al import. Valida criticas fail-fast.
Importar: `from config import settings` y usar `settings.SUPABASE_URL`, etc.
"""

import os
import sys
from dataclasses import dataclass, field
from typing import List


def _env(name: str, default: str = "") -> str:
    return os.environ.get(name, default)


def _env_first(*names: str, default: str = "") -> str:
    """Primer env var con valor no vacio de la lista."""
    for n in names:
        v = os.environ.get(n)
        if v:
            return v
    return default


@dataclass(frozen=True)
class Settings:
    # Supabase
    SUPABASE_URL: str = field(default_factory=lambda: _env("SUPABASE_URL"))
    SUPABASE_ANON_KEY: str = field(
        default_factory=lambda: _env_first("SUPABASE_ANON_KEY", "SUPABASE_KEY")
    )
    SUPABASE_SERVICE_KEY: str = field(
        default_factory=lambda: _env_first(
            "SUPABASE_SERVICE_KEY", "SUPABASE_SERVICE_ROLE_KEY", "SUPABASE_KEY"
        )
    )

    # Flask
    SECRET_KEY: str = field(
        default_factory=lambda: _env("SECRET_KEY", "pagos_liliana_supabase_2024")
    )

    # Correo
    CORREO_REMITENTE: str = field(
        default_factory=lambda: _env("CORREO_REMITENTE", "argoty.martin@gmail.com")
    )
    CORREO_CLAVE_APP: str = field(default_factory=lambda: _env("CORREO_CLAVE_APP"))

    # Admin
    ADMIN_USUARIOS: List[str] = field(
        default_factory=lambda: [
            u.strip()
            for u in _env("ADMIN_USUARIOS", "admin,admin@test.com").split(",")
            if u.strip()
        ]
    )

    # WhatsApp Cloud API
    WHATSAPP_TOKEN: str = field(default_factory=lambda: _env("WHATSAPP_TOKEN"))
    WHATSAPP_PHONE_ID: str = field(default_factory=lambda: _env("WHATSAPP_PHONE_ID"))
    WHATSAPP_NOTIFY_TO: str = field(default_factory=lambda: _env("WHATSAPP_NOTIFY_TO"))

    # Gemini (OCR/IA)
    GEMINI_API_KEY: str = field(default_factory=lambda: _env("GEMINI_API_KEY"))

    # Deploy webhook
    DEPLOY_TOKEN: str = field(default_factory=lambda: _env("DEPLOY_TOKEN"))

    def validate(self) -> None:
        """Fail-fast vars criticas. Llamar al arranque app."""
        missing = []
        if not self.SUPABASE_URL:
            missing.append("SUPABASE_URL")
        if not self.SUPABASE_ANON_KEY:
            missing.append("SUPABASE_ANON_KEY (o SUPABASE_KEY)")
        if missing:
            print("=" * 60, file=sys.stderr)
            print("  ERROR: Faltan variables de entorno:", file=sys.stderr)
            for m in missing:
                print(f"    - {m}", file=sys.stderr)
            print("=" * 60, file=sys.stderr)
            sys.exit(1)


settings = Settings()
