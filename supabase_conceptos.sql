-- =====================================================
-- Migración: Tabla maestra `conceptos` + FK en `pagos`
-- Fecha: 2026-05-02
-- Ejecutar en Supabase SQL Editor
-- =====================================================
--
-- Objetivo:
--   - Reemplazar `pagos.concepto` (TEXT libre) por FK a tabla maestra.
--   - `contactos` ya cubre el rol de "persona" (FK existente: pagos.contacto_id).
--   - Mantener `pagos.concepto` TEXT vivo durante migración (rollback safety).
--
-- Estrategia de coexistencia:
--   1. Esta migración crea `conceptos` y agrega `pagos.concepto_id` NULLABLE.
--   2. Código viejo sigue leyendo/escribiendo `pagos.concepto` TEXT sin romperse.
--   3. UI nueva escribe ambos campos durante transición.
--   4. Drop `pagos.concepto` TEXT en una migración futura cuando todo migre.

-- ---------- Tabla maestra de conceptos ----------
CREATE TABLE IF NOT EXISTS conceptos (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre TEXT UNIQUE NOT NULL,
    activo BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Índice pa búsquedas case-insensitive por nombre
CREATE INDEX IF NOT EXISTS conceptos_nombre_lower_idx
    ON conceptos (LOWER(nombre));

-- ---------- FK en pagos (nullable durante coexistencia) ----------
ALTER TABLE pagos
    ADD COLUMN IF NOT EXISTS concepto_id BIGINT REFERENCES conceptos(id) ON DELETE SET NULL;

CREATE INDEX IF NOT EXISTS pagos_concepto_id_idx ON pagos (concepto_id);

-- ---------- RLS ----------
ALTER TABLE conceptos ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Acceso total conceptos" ON conceptos;
CREATE POLICY "Acceso total conceptos" ON conceptos FOR ALL USING (true) WITH CHECK (true);

-- ---------- Verificación post-migración ----------
-- Ejecutar después para validar:
--   SELECT COUNT(*) FROM conceptos;                          -- 0 inicial
--   SELECT column_name, data_type, is_nullable
--     FROM information_schema.columns
--     WHERE table_name='pagos' AND column_name='concepto_id';
