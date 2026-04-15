-- =====================================================
-- Control Financiero - Setup Supabase
-- Ejecutar este SQL en el SQL Editor de Supabase
-- =====================================================

-- Tabla de pagos/movimientos
CREATE TABLE IF NOT EXISTS pagos (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    fecha TEXT NOT NULL,
    valor INTEGER NOT NULL DEFAULT 0,
    tipo TEXT NOT NULL DEFAULT 'egreso',
    concepto TEXT DEFAULT '',
    medio TEXT DEFAULT '',
    referencia TEXT DEFAULT '',
    observacion TEXT DEFAULT '',
    imagen TEXT DEFAULT '',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabla de destinatarios de correo
CREATE TABLE IF NOT EXISTS destinatarios (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    correo TEXT UNIQUE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Destinatarios por defecto
INSERT INTO destinatarios (correo) VALUES
    ('martin.argoty@hotmail.com'),
    ('lipamoan@hotmail.com')
ON CONFLICT (correo) DO NOTHING;

-- Tabla para rastrear pagos vistos por usuario
CREATE TABLE IF NOT EXISTS pagos_vistos (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    usuario TEXT NOT NULL,
    pago_id BIGINT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(usuario, pago_id)
);

-- Habilitar Row Level Security (RLS)
ALTER TABLE pagos ENABLE ROW LEVEL SECURITY;
ALTER TABLE destinatarios ENABLE ROW LEVEL SECURITY;
ALTER TABLE pagos_vistos ENABLE ROW LEVEL SECURITY;

-- Policies para acceso total (el service role bypassing RLS)
CREATE POLICY "Acceso total pagos" ON pagos FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Acceso total destinatarios" ON destinatarios FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Acceso total pagos_vistos" ON pagos_vistos FOR ALL USING (true) WITH CHECK (true);

-- Crear buckets de Storage para imagenes
INSERT INTO storage.buckets (id, name, public) VALUES ('comprobantes', 'comprobantes', true)
ON CONFLICT (id) DO NOTHING;

-- Policies de Storage
CREATE POLICY "Lectura publica comprobantes" ON storage.objects
    FOR SELECT USING (bucket_id = 'comprobantes');

CREATE POLICY "Subir comprobantes" ON storage.objects
    FOR INSERT WITH CHECK (bucket_id = 'comprobantes');

CREATE POLICY "Eliminar comprobantes" ON storage.objects
    FOR DELETE USING (bucket_id = 'comprobantes');

-- Tabla para suscripciones de push notifications (Control Financiero)
CREATE TABLE IF NOT EXISTS push_subscriptions_control_financiero (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    usuario TEXT NOT NULL,
    endpoint TEXT UNIQUE NOT NULL,
    auth TEXT NOT NULL,
    p256dh TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE push_subscriptions_control_financiero ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Acceso total push subs" ON push_subscriptions_control_financiero FOR ALL USING (true) WITH CHECK (true);

-- Habilitar Auth en Supabase
-- Ve a Authentication -> Providers -> Email y activa "Enable Email Signups"
-- Para Google OAuth: Authentication -> Providers -> Google