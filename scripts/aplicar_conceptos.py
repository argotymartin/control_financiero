#!/usr/bin/env python3
"""Aplica el mapeo revisado en `conceptos_mapeo.csv` a Supabase.

Pasos:
    1. Lee CSV (output de extraer_conceptos.py + edición manual).
    2. Inserta filas únicas en `conceptos` (idempotente).
    3. Inserta contactos faltantes en `contactos` (idempotente, solo si no existen).
    4. UPDATE pagos.concepto_id (y pagos.contacto_id si está vacío) según mapeo.

Idempotente: se puede correr varias veces. NO borra `pagos.concepto` TEXT viejo.

Uso:
    python scripts/aplicar_conceptos.py [--dry-run]
"""

import argparse
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from supabase import create_client

from config import settings


CSV_PATH = ROOT / "conceptos_mapeo.csv"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Muestra cambios sin escribir")
    args = parser.parse_args()

    settings.validate()
    if not settings.SUPABASE_SERVICE_KEY:
        print("ERROR: requiere SUPABASE_SERVICE_KEY (admin) para UPDATE pagos.", file=sys.stderr)
        return 1

    if not CSV_PATH.exists():
        print(f"ERROR: no existe {CSV_PATH}. Corre primero extraer_conceptos.py", file=sys.stderr)
        return 1

    client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)

    with CSV_PATH.open("r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    print(f"Filas CSV: {len(rows)}")

    conceptos_unicos = sorted({(r["concepto_propuesto"] or "").strip() for r in rows if r["concepto_propuesto"].strip()})
    contactos_unicos = sorted({(r["contacto_propuesto"] or "").strip() for r in rows if r["contacto_propuesto"].strip()})
    print(f"Conceptos únicos a crear: {len(conceptos_unicos)}")
    print(f"Contactos únicos referenciados: {len(contactos_unicos)}")

    existing_conc = {
        c["nombre"]: c["id"]
        for c in (client.table("conceptos").select("id,nombre").execute().data or [])
    }
    existing_cont = {
        (c.get("nombre") or "").lower(): c["id"]
        for c in (client.table("contactos").select("id,nombre").execute().data or [])
    }

    # ---------- Insertar conceptos faltantes ----------
    a_crear_conc = [n for n in conceptos_unicos if n and n not in existing_conc]
    print(f"Conceptos por insertar: {len(a_crear_conc)} → {a_crear_conc}")
    if a_crear_conc and not args.dry_run:
        resp = client.table("conceptos").insert(
            [{"nombre": n} for n in a_crear_conc]
        ).execute()
        for c in resp.data or []:
            existing_conc[c["nombre"]] = c["id"]

    # ---------- Insertar contactos faltantes ----------
    a_crear_cont = [n for n in contactos_unicos if n and n.lower() not in existing_cont]
    print(f"Contactos por insertar: {len(a_crear_cont)} → {a_crear_cont}")
    if a_crear_cont and not args.dry_run:
        resp = client.table("contactos").insert(
            [{"nombre": n} for n in a_crear_cont]
        ).execute()
        for c in resp.data or []:
            existing_cont[(c.get("nombre") or "").lower()] = c["id"]

    # ---------- UPDATE pagos ----------
    pagos = client.table("pagos").select("id,concepto,contacto_id").execute().data or []
    print(f"Pagos a evaluar: {len(pagos)}")

    mapa_original = {r["concepto_original"]: r for r in rows}

    actualizados = 0
    sin_match = 0
    for p in pagos:
        original = (p.get("concepto") or "").strip()
        m = mapa_original.get(original)
        if not m:
            sin_match += 1
            continue

        nuevo = {}
        cn = (m["concepto_propuesto"] or "").strip()
        if cn and cn in existing_conc:
            nuevo["concepto_id"] = existing_conc[cn]

        # Solo asignar contacto_id si pagos.contacto_id está vacío (no pisar manual)
        contn = (m["contacto_propuesto"] or "").strip().lower()
        if contn and contn in existing_cont and not p.get("contacto_id"):
            nuevo["contacto_id"] = existing_cont[contn]

        if not nuevo:
            continue

        if args.dry_run:
            print(f"  [dry] pago {p['id']} '{original}' → {nuevo}")
        else:
            client.table("pagos").update(nuevo).eq("id", p["id"]).execute()
        actualizados += 1

    print()
    print(f"Pagos actualizados: {actualizados}")
    print(f"Pagos sin match en CSV: {sin_match}")
    print(f"Modo: {'DRY-RUN (sin escribir)' if args.dry_run else 'APLICADO'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
