#!/usr/bin/env python3
"""Extrae conceptos distintos de pagos.concepto y genera CSV pa revisión manual.

Uso:
    python scripts/extraer_conceptos.py

Output:
    conceptos_mapeo.csv con columnas:
      - concepto_original     (texto actual en pagos.concepto)
      - cantidad              (cuántos pagos lo usan)
      - concepto_propuesto    (sugerencia normalizada — REVISAR)
      - contacto_propuesto    (sugerencia persona — REVISAR, vacio = ninguna)

El usuario edita el CSV ajustando concepto_propuesto y contacto_propuesto,
luego corre `aplicar_conceptos.py` que crea masters y actualiza pagos.
"""

import csv
import os
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from supabase import create_client

from config import settings


OUTPUT_CSV = ROOT / "conceptos_mapeo.csv"


def _norm(s: str) -> str:
    """Normaliza texto: lower, sin tildes simples, sin caracteres raros."""
    s = (s or "").strip().lower()
    s = (
        s.replace("á", "a").replace("é", "e").replace("í", "i")
        .replace("ó", "o").replace("ú", "u").replace("ñ", "n")
    )
    s = re.sub(r"[^a-z0-9_\s]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _split_concepto_persona(texto: str, nombres_contactos: list[str]) -> tuple[str, str]:
    """Heurística: separa 'cuota_liliana' → ('cuota','liliana').

    Si encuentra nombre de contacto dentro del texto, lo extrae como persona.
    Si no, devuelve (concepto, "").
    """
    n = _norm(texto)
    if not n:
        return ("sin_concepto", "")

    contacto_match = ""
    for nombre in nombres_contactos:
        nn = _norm(nombre)
        if nn and re.search(rf"\b{re.escape(nn)}\b", n):
            contacto_match = nombre
            n = re.sub(rf"\b{re.escape(nn)}\b", "", n)
            n = re.sub(r"[_\s]+", " ", n).strip(" _-")
            break

    n = n.replace(" ", "_") or "sin_concepto"
    return (n, contacto_match)


def main() -> int:
    settings.validate()

    client = create_client(
        settings.SUPABASE_URL,
        settings.SUPABASE_SERVICE_KEY or settings.SUPABASE_ANON_KEY,
    )

    print("Cargando pagos…")
    pagos = client.table("pagos").select("concepto").execute().data or []
    print(f"  {len(pagos)} pagos leídos.")

    print("Cargando contactos…")
    contactos = client.table("contactos").select("nombre").execute().data or []
    nombres = [c["nombre"] for c in contactos if c.get("nombre")]
    print(f"  {len(nombres)} contactos.")

    counter: Counter[str] = Counter()
    for p in pagos:
        c = (p.get("concepto") or "").strip()
        counter[c] += 1

    print(f"Conceptos distintos: {len(counter)}")

    rows = []
    for concepto_original, cantidad in counter.most_common():
        concepto_prop, contacto_prop = _split_concepto_persona(
            concepto_original, nombres
        )
        rows.append(
            {
                "concepto_original": concepto_original,
                "cantidad": cantidad,
                "concepto_propuesto": concepto_prop,
                "contacto_propuesto": contacto_prop,
            }
        )

    with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "concepto_original",
                "cantidad",
                "concepto_propuesto",
                "contacto_propuesto",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    print()
    print(f"OK → {OUTPUT_CSV}")
    print()
    print("Siguiente paso:")
    print(f"  1. Abrir {OUTPUT_CSV.name} y revisar columnas concepto_propuesto/contacto_propuesto.")
    print("  2. Ajustar nombres como quieras (minúsculas, snake_case sugerido).")
    print("  3. Vaciar 'contacto_propuesto' si no aplica (ej: pago_luz no tiene persona).")
    print("  4. Correr: python scripts/aplicar_conceptos.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
