# M23 — UI Adapter

## Objetivo

Introducir una capa de adaptación entre cualquier interfaz de usuario futura y `ROBY`, sin crear todavía una UI concreta.

La regla arquitectónica es:

```text
UI concreta -> ROBYUIAdapter -> ROBY.process()
```

`ROBY` sigue recibiendo texto y devolviendo `UserResponse`. La interfaz no debe conocer el flujo interno de ROBY.

## Componentes agregados

### `ROBYClient`

Protocolo mínimo que representa cualquier objeto capaz de procesar texto como ROBY:

```python
process(text: str, session_id: str | None = None) -> UserResponse
```

Esto permite testear el adaptador con dobles sin instanciar todo ROBY.

### `UIResponse`

Modelo de presentación estable para futuras interfaces:

- `text`
- `status`
- `session_id`
- `needs_input`

### `ROBYUIAdapter`

Adaptador de entrada/salida textual:

- normaliza el texto de entrada;
- rechaza mensajes vacíos sin llamar a ROBY;
- llama a `ROBY.process()` con `session_id`;
- transforma `UserResponse` en `UIResponse`;
- convierte errores inesperados en una respuesta de fallo presentable.

## Fuera de alcance

M23 no implementa:

- interfaz gráfica;
- interfaz web;
- voz;
- streaming;
- eventos visuales;
- persistencia de conversaciones en UI.

Es solo el contrato entre ROBY y futuras superficies de interacción.

## Contratos verificados

- El adaptador envía texto y `session_id` a ROBY.
- El adaptador devuelve una respuesta presentable.
- `NEEDS_INFORMATION` se traduce a `needs_input=True`.
- Texto vacío no llama a ROBY.
- Errores inesperados de ROBY se convierten en `failure` presentable.

## Estado

Completo.
