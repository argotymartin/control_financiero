# 01 - Dominio

Entidades del negocio. Todas viven en tablas Supabase (PostgreSQL).

## Pago

Transaccion de dinero entre admin y destinatario.

### Tabla `pagos`

| Campo | Tipo | Req | Default | Notas |
|-------|------|-----|---------|-------|
| id | BIGINT PK | auto | - | supabase auto-incremental |
| fecha | TEXT | si | - | formato `YYYY-MM-DD` |
| valor | INTEGER | si | 0 | COP, sin decimales |
| tipo | TEXT | si | `egreso` | `ingreso` o `egreso` |
| concepto | TEXT | no | `""` | descripcion corta |
| medio | TEXT | no | `""` | efectivo / transferencia / nequi / daviplata |
| referencia | TEXT | no | `""` | numero transferencia u otro |
| observacion | TEXT | no | `""` | texto libre largo |
| imagen | TEXT | no | `""` | URL publica del comprobante en Storage |
| contacto_id | BIGINT FK | no | null | fk a `contactos.id` |
| gps_lat | DECIMAL | no | null | latitud GPS captura |
| gps_lng | DECIMAL | no | null | longitud GPS captura |
| created_at | TIMESTAMPTZ | auto | NOW() | |

### Invariantes

- `valor > 0` (aplicar validacion; negativos rechazados)
- `tipo` debe ser uno de: `ingreso`, `egreso`
- `fecha` debe ser valida (parseable como date)
- Si `imagen` presente: URL debe apuntar a bucket `comprobantes`
- `contacto_id` debe existir en `contactos` si no es null

### Terminologia codigo vs spec

El codigo usa `egreso`/`ingreso`. En chat/UX se habla `entrada`/`salida` a veces.
Convencion: **al nivel de dominio** siempre `egreso` (sale dinero) / `ingreso` (entra).

## Contacto

Destinatario de pagos.

### Tabla `contactos`

| Campo | Tipo | Req | Notas |
|-------|------|-----|-------|
| id | BIGINT PK | auto | |
| nombre | TEXT | si | nombre visible |
| email | TEXT | no | login destinatario si tiene |
| telefono | TEXT | no | formato `57XXXXXXXXX` (sin +) |
| created_at | TIMESTAMPTZ | auto | |

### Invariantes

- `nombre` no vacio
- `email` unico si presente (email repetido = mismo contacto)
- `telefono` sin `+`, con codigo pais Colombia (57)

### Rol permisos

El email del contacto es lo que define visibilidad destinatario:
- Destinatario loguea con email X
- Ve pagos donde `contacto.email == X`
- No es admin (no esta en env `ADMIN_USUARIOS`)

## Usuario

Abstracto. No existe tabla propia; auth manejado por Supabase.

### Identificacion

- `email` (string) - identificador primario
- Viene de Supabase Auth despues login
- Guardado en `session["email"]` (Flask session)

### Rol

Determinado por funcion `es_admin()`:

```python
def es_admin():
    email = session.get("email", "")
    return email in ADMIN_USUARIOS
```

`ADMIN_USUARIOS` = env var lista emails separados por coma.

Valor prod: `argoty.martin@gmail.com,martin.argoty@hotmail.com,admin@test.com`

## Destinatario (correo)

Lista de emails para reportes Excel masivos. **No confundir con Contacto**.

### Tabla `destinatarios`

| Campo | Tipo | Req | Notas |
|-------|------|-----|-------|
| id | BIGINT PK | auto | |
| correo | TEXT UNIQUE | si | email |
| created_at | TIMESTAMPTZ | auto | |

Usado solo por `/enviar-correo` para enviar Excel. Admin gestiona lista.

## Pago visto

Tracking de pagos que un usuario ya vio (para globito "nuevos").

### Tabla `pagos_vistos`

| Campo | Tipo | Req | Notas |
|-------|------|-----|-------|
| id | BIGINT PK | auto | |
| usuario | TEXT | si | email |
| pago_id | BIGINT | si | fk pagos.id |
| created_at | TIMESTAMPTZ | auto | |
| UNIQUE(usuario, pago_id) | | | |

## Push Subscription

Suscripcion Web Push por dispositivo/navegador.

### Tabla `push_subscriptions_control_financiero`

| Campo | Tipo | Req | Notas |
|-------|------|-----|-------|
| id | BIGINT PK | auto | |
| usuario | TEXT | si | email |
| endpoint | TEXT UNIQUE | si | URL servicio push navegador |
| auth | TEXT | si | key autenticacion |
| p256dh | TEXT | si | clave publica |
| created_at | TIMESTAMPTZ | auto | |

## Relaciones

```
contactos 1 ─── N pagos (contacto_id)
usuarios (session) ─── N pagos_vistos (usuario)
usuarios (session) ─── N push_subscriptions (usuario)
```

No hay relacion formal admin <-> pagos: admin puede ver/crear cualquiera.
Destinatario filtrado por match `contacto.email = session.email`.

## Storage

Bucket `comprobantes` (publico).

- Comprobantes imagenes subidos al registrar pago
- URL guardada en `pagos.imagen`
- Accesibles sin auth (bucket publico)

## Futuro / TBD

Posibles entidades cuando crezca:

- `categorias` (clasificacion gastos, pendiente feature)
- `mensajes` (chat usuarios, pendiente feature)
- `recordatorios` (pagos recurrentes)

Estos NO existen aun. Agregar a spec cuando se implementen.

## Estado actual codigo

- Definiciones tablas: `supabase_setup.sql` (parcial, falta `contactos`)
- Funciones CRUD: `web_pagos_supabase.py` funciones `cargar_pagos`, `guardar_pago`, `obtener_contacto`, etc.
- Helpers: `cargar_pagos_visibles()` (L122) filtra por rol
