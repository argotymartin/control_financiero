# 07 - Permisos

Reglas autorizacion admin vs destinatario. Aplicadas siempre server-side.

## Roles

**Admin**: email en env var `ADMIN_USUARIOS` (lista CSV).

**Destinatario**: usuario autenticado NO en lista admin.

**Anonimo**: sin sesion. Solo accede a paginas login/registro.

## Matriz permisos

| Accion | Anonimo | Destinatario | Admin |
|--------|---------|--------------|-------|
| Ver login/registro | si | si | si |
| Login facial | si | si | si |
| Ver lista pagos | no | solo suyos | todos |
| Crear pago para si mismo | no | si | si |
| Crear pago para otro destinatario | no | **no** | si |
| Editar pago | no | no | si (TBD) |
| Eliminar pago | no | no | si |
| Ver graficas/dashboard | no | solo suyos | todos |
| Descargar Excel | no | solo suyos | todos |
| Enviar reporte por correo masivo | no | no | si |
| Gestionar contactos (CRUD) | no | no | si |
| Gestionar destinatarios correo | no | no | si |
| Chat AI registrar pago | no | solo suyos | cualquiera |
| Chat AI eliminar pago | no | no | si |
| Chat AI consultar totales | no | solo suyos | todos |
| Suscribir push | no | si | si |
| Subir comprobante a Storage | no | si (propio) | si |
| Acceder endpoint /deploy | no | no | si + token |

## Helpers implementados

### `es_admin()` — determinar rol

```python
def es_admin():
    email = session.get("email", "")
    return email in ADMIN_USUARIOS
```

Retorna `True` si email en lista admin.

### `cargar_pagos_visibles()` — filtrar por rol

```python
def cargar_pagos_visibles():
    """Admin ve todo. Destinatario ve solo pagos cuyo contacto.email = su email."""
    pagos = cargar_pagos()
    if es_admin():
        return pagos
    email_actual = session.get("email", "")
    if not email_actual:
        return []
    client = supabase_admin if supabase_admin else supabase
    resp = client.table("contactos").select("id").eq("email", email_actual).execute()
    mis_ids = {c["id"] for c in (resp.data or [])}
    return [p for p in pagos if p.get("contacto_id") in mis_ids]
```

**Comportamiento:**
- Admin: retorna `cargar_pagos()` completo
- Destinatario autenticado: query contactos donde `email = session.email`, filtra pagos por `contacto_id` matching
- Anonimo: retorna `[]`

### Decoradores rutas

**`@login_requerido`** — requiere sesion activa:
```python
def login_requerido(f):
    @wraps(f)
    def decorador(*args, **kwargs):
        usuario, email, nombre = obtener_usuario_actual()
        if not email:
            flash("Debes iniciar sesion para acceder.", "error")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorador
```

Sin sesion -> redirect `/login` con flash.

**`@admin_requerido`** — requiere sesion + ser admin:
```python
def admin_requerido(f):
    @wraps(f)
    @login_requerido
    def decorador(*args, **kwargs):
        if not es_admin():
            flash("Solo el administrador puede acceder a esta funcion.", "error")
            return redirect(url_for("inicio"))
        return f(*args, **kwargs)
    return decorador
```

No admin -> redirect `/inicio` con flash.

## Rutas protegidas (muestra)

- `@admin_requerido`: `/eliminar/<id>`, `/contactos/*`, `/destinatarios/*`, `/deploy`
- `@login_requerido`: `/inicio`, `/agregar`, `/chat`, `/graficas`, `/descargar-excel`, `/correo`
- Publicas: `/login`, `/registro`, `/face-login`, `/manifest.json`, `/sw.js`, `/static/*`

## Reglas criticas (NO romper en refactor)

1. **Admin ve todo siempre.** Cualquier query de listado sin ese rol -> bug.
2. **Destinatario NUNCA ve pagos de otro destinatario.** Filtro por `contacto.email = session.email` obligatorio.
3. **Eliminar pago solo admin.** No expandir a destinatario aunque sea suyo.
4. **Tools chat AI respetan permisos.** `_tool_eliminar_pago_por_id` verifica `es_admin()` internamente.
5. **Endpoint `/deploy` requiere token** ademas de admin (doble check).
6. **Session.email es source of truth.** No confiar en forms, headers, query params.

## Edge cases

- **Destinatario sin contacto asociado** (email no coincide con ningun contacto): ve 0 pagos, no error.
- **Email con mayusculas/espacios**: comparacion es case-sensitive exacta. Codigo debe normalizar (TBD, actual mente no lo hace).
- **Usuario logueado pero contacto borrado**: ve 0 pagos (comportamiento actual).
- **Contacto con email duplicado**: multiples pagos pueden asociarse, destinatario ve todos (caso real cuando admin agrega contactos duplicados por error).

## Criterios aceptacion refactor

Al migrar a Clean Arch, verificar **ANTES de borrar codigo viejo**:

- [ ] Admin login, ve lista completa en `/inicio`
- [ ] Destinatario login, ve solo pagos suyos
- [ ] Destinatario NO ve pagos de otro destinatario en `/inicio`
- [ ] Destinatario NO puede acceder `/eliminar/X` (redirect + flash)
- [ ] Destinatario NO puede acceder `/contactos` (redirect + flash)
- [ ] Anonimo redirect `/login` al acceder cualquier ruta protegida
- [ ] Chat AI: destinatario pregunta "elimina pago 5" -> rechazado con mensaje
- [ ] Chat AI: destinatario pregunta "cuanto pague en marzo" -> muestra solo suyo
- [ ] Excel descarga: destinatario recibe solo sus pagos
- [ ] Graficas: destinatario ve solo suyas

## Estado actual codigo

- `ADMIN_USUARIOS`: `web_pagos_supabase.py:74`
- `es_admin()`: `web_pagos_supabase.py:367`
- `login_requerido`: `web_pagos_supabase.py:373`
- `admin_requerido`: `web_pagos_supabase.py:385`
- `cargar_pagos_visibles()`: `web_pagos_supabase.py:122`
- Tools chat con check admin: `_tool_eliminar_pago_por_id` (L1463)
