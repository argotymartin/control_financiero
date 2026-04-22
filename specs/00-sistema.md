# 00 - Sistema

## Objetivo

App web para registrar pagos (entradas/salidas) entre admin y destinatarios,
con notificaciones multi-canal, OCR automatico de comprobantes y chat IA.

Uso: personal/familiar pequeño grupo (admin + ~1-5 destinatarios).

## Usuarios

- **Admin** (1-2 personas): ve/crea/elimina todo. Definido en env `ADMIN_USUARIOS`.
- **Destinatario** (N personas): ve y crea solo pagos dirigidos a si mismo.

Autenticacion: Supabase Auth (email + clave) O reconocimiento facial (webcam).

## Stack actual

| Capa | Tecnologia |
|------|------------|
| Backend | Flask 3.x (Python 3.13) |
| DB | Supabase (PostgreSQL managed) |
| Auth | Supabase Auth + face_recognition |
| Storage | Supabase Storage (bucket `comprobantes`) |
| AI | Google Gemini API (modelo `gemini-2.5-flash`) |
| Notif WhatsApp | Meta Cloud API v21.0 |
| Notif Push | Web Push API + pywebpush |
| Correo | smtplib Gmail (SMTP 587) |
| Frontend | Jinja2 + vanilla JS + Web APIs |
| PWA | Service Worker |
| Hosting | PythonAnywhere (free tier) |

## Limites tecnicos

- Gemini free tier: 20 requests/dia (RPD)
- WhatsApp: numero Meta test `+1 555-006-8499`, max 5 destinatarios autorizados
- PythonAnywhere: 1 web app, sin env vars UI (se setean en wsgi `/var/www/...`)
- Supabase: plan free, limite storage 1GB

## Reglas globales

- **Monto**: COP (pesos colombianos), entero sin decimales
- **Timezone**: America/Bogota (UTC-5)
- **Telefono**: formato internacional sin `+` (ej: `573213892071`)
- **Fechas**: ISO `YYYY-MM-DD`
- **Permisos**: siempre verificar server-side, nunca confiar en frontend
- **RLS Supabase**: activado pero bypasseado via `service_role` key (codigo filtra por rol)

## Features implementadas (estado 2026-04-21)

- [x] Registro pagos via formulario web
- [x] Registro pagos via chat AI (function calling Gemini)
- [x] Registro pagos via voz (Web Speech API)
- [x] OCR comprobantes con Gemini
- [x] Login email + clave (Supabase Auth)
- [x] Login facial (face_recognition)
- [x] Permisos admin vs destinatario
- [x] WhatsApp via template `notificacion_pago` (es_CO)
- [x] Notificaciones push Web
- [x] GPS captura al registrar pago
- [x] Envio de reporte Excel por correo
- [x] PWA instalable
- [x] Dashboard graficas (Chart.js)

## Features pendientes

- [ ] Optimizacion mobile-first (Tailwind + DaisyUI)
- [ ] Chat entre usuarios tiempo real
- [ ] Clasificacion automatica gastos
- [ ] Login huella dactilar (WebAuthn)
- [ ] Codigo QR pagos
- [ ] Notificaciones Telegram
- [ ] Predicciones gasto
- [ ] Refactor Clean Architecture

## Repo y prod

- Repo: https://github.com/argotymartin/control_financiero (publico)
- Prod: https://margoty.pythonanywhere.com
- Supabase project: `zsbbyvqcxqwhmydztbax`
- Meta app: ID `601271564844056` (Mensajeria)
