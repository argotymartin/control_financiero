# Specs - Control Financiero

Spec-Driven Development (SDD). Specs son source of truth del comportamiento
esperado. Codigo implementa specs. Tests validan specs.

## Indice

### Fundacionales
- [00-sistema.md](00-sistema.md) - Vision, stack, reglas globales
- [01-dominio.md](01-dominio.md) - Entidades: Pago, Usuario, Contacto
- [07-permisos.md](07-permisos.md) - Reglas admin vs destinatario

### Features (escribir cuando se toquen)
- 02-auth.md - Login email + facial (pendiente)
- 03-pagos-crud.md - Registrar/listar/eliminar pagos (pendiente)
- 04-notificaciones.md - WhatsApp + push + email (pendiente)
- 05-ocr-comprobantes.md - Gemini OCR (pendiente)
- 06-chat-ai.md - Function calling Gemini (pendiente)

### Arquitectura
- arquitectura/clean-arch-target.md - Estructura objetivo refactor (pendiente)
- arquitectura/strangler-plan.md - Orden migracion (pendiente)

## Convenciones

Cada spec sigue estructura:
1. **Objetivo** - que logra la feature en una frase
2. **Actores** - quien la usa y con que rol
3. **Reglas** - invariantes, validaciones, edge cases
4. **Flujo** - pasos del happy path
5. **Errores** - que puede fallar y como se maneja
6. **Criterios aceptacion** - checklist testeable
7. **Estado actual** - referencia al codigo existente

## Como usar con IA (Claude)

Al pedir implementacion o refactor:

    "Implementa X siguiendo specs/03-pagos-crud.md y specs/07-permisos.md"

La IA lee specs, produce codigo que cumple specs, menos back-and-forth.

## Mantenimiento

- Cambio feature -> update spec ANTES de codear
- Bug critico -> actualizar spec si revela regla nueva
- Refactor -> spec de comportamiento actual + spec de target, migrar sin cambiar spec comportamiento
