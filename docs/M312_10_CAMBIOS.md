# M312.10 — Contexto personal seguro

- Agrega `SafePersonalContextService` y `SafePersonalContext`.
- Filtra memorias por la identidad activa resuelta.
- Carlos recibe contexto de Carlos y del perfil compartido Familia.
- Cristina recibe contexto de Cristina y del perfil compartido Familia.
- Identidades desconocidas o en conflicto reciben solo contexto compartido.
- Una consulta por `subject` no puede eludir el aislamiento de identidad.
- La composición de identidad expone el servicio sin conectarlo al runtime normal.
- No agrega biometría, aprendizaje, escrituras ni personalización visible.

Validación interna: 7037 pruebas aprobadas.
