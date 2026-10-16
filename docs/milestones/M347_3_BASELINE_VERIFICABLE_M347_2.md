# M347.3 — Baseline verificable de M347.2

## Propósito

Establecer una línea base reproducible antes de continuar la serie M347.x, sin modificar comportamiento cognitivo, persistencia, red, voz, herramientas ni respuestas.

## Base auditada

- Base de entrada: `M347.2 — Cuidado Proactivo Gobernado`.
- Frontera productiva única: `app.official_conversation_gateway.OfficialConversationGateway`.
- Núcleo cognitivo único: `app.canonical_cognitive_core.CanonicalCognitiveCore`.
- Construcción productiva del núcleo: una sola, dentro de `OfficialConversationGateway`.
- Credenciales privadas canónicas: `.roby/credentials.json`, preservado sin modificaciones.

## Inventario del snapshot

Los conteos del snapshot auditado son:

- 2.284 archivos totales.
- 1.478 archivos Python.
- 600 archivos de pruebas `test_*.py`.
- 744 archivos dentro de `docs/`.

Los conteos son descriptivos del snapshot M347.2 recibido y no constituyen una meta arquitectónica.

## Mapa ejecutivo de autoridades

- Conversación y composición: `OfficialConversationGateway`.
- Núcleo coordinador: `CanonicalCognitiveCore`.
- Memoria: fachada canónica sobre `OfficialMemoryGateway`.
- Planificación: fachada canónica sobre `ExecutiveConversationPlanner`.
- Decisión: fachada canónica con autoridad operativa primaria existente.
- Estado cognitivo: fachada canónica sobre `CognitiveStateManager`.
- Reflexión: autoridad residente existente, integrada al núcleo.
- Juicio cognitivo M347.1: consultivo, sin autorización ni ejecución.
- Cuidado proactivo M347.2: consultivo, sin monitoreo, persistencia, autorización ni ejecución autónomos.

## Invariantes protegidos

1. Existe un único núcleo cognitivo productivo.
2. `OfficialConversationGateway` sigue siendo el único punto de composición.
3. No se introduce memoria, planificador, gateway o ejecutor paralelo.
4. `.roby/credentials.json` permanece como fuente privada canónica.
5. ROBY continúa siendo un proyecto personal de Carlos y Cristina, no comercial ni distribuible.
6. Toda capacidad futura deberá quedar integrada, probada y documentada.
7. El contexto de la Chevrolet Tracker Automática Turbo 2.0 es información privada útil, no una dependencia rígida del núcleo.

## Cambios de M347.3

- Se actualizó el README raíz para reflejar la versión y filosofía actuales.
- Se formalizaron las reglas permanentes del proyecto.
- Se documentó el mapa ejecutivo de autoridades de la base M347.2.
- Se incorporaron pruebas estáticas de baseline y protección arquitectónica.
- No se modificó código productivo.

## Validación requerida

```bash
ruff check .
pytest -q
```

La versión solo puede declararse base canónica después de completar ambas validaciones y la revisión manual del contenido del ZIP.

## Resultado de validación en el entorno de preparación

- Pruebas focalizadas M347.3: **5 aprobadas**.
- Compilación Python (`compileall`) de código y pruebas: **correcta**.
- Suite completa: alcanzó el **100 % sin fallos visibles**, pero el proceso no entregó el resumen final antes del límite del entorno; debe confirmarse localmente.
- Ruff: no disponible en el entorno de preparación; debe ejecutarse localmente antes de declarar M347.3 como base canónica definitiva.
