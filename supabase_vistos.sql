-- Tabla para registrar que pagos ya fueron vistos por cada usuario
CREATE TABLE pagos_vistos (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    usuario TEXT NOT NULL,
    pago_id BIGINT NOT NULL,
    visto_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(usuario, pago_id)
);

-- Seguridad
ALTER TABLE pagos_vistos ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Acceso total pagos_vistos" ON pagos_vistos FOR ALL USING (true) WITH CHECK (true);
