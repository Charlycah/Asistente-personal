# ROBY XI.2 — INTEL-G2.1 — “WHAT DID YOU LEARN?” — SURGICAL GREEN

Baseline de partida: 14.068 PASS · Ruff clean · 0 FAIL, certificada por el usuario.

Cambio quirúrgico:

- proyecta `household.timezone` como `ROBY_HOUSEHOLD_TIMEZONE`;
- inyecta explícitamente ese timezone en `OfficialMemoryGateway` desde la composición oficial;
- reconoce únicamente intents explícitos de aprendizaje durable para `hoy` y `ayer`;
- resuelve días civiles en el timezone household y los convierte a intervalos UTC half-open;
- consume exclusivamente `governed_learning_temporal_introspection` de INTEL-G2;
- produce una respuesta conversacional bounded y honesta, incluida la ausencia de aprendizajes;
- no abre Analysis Mode, Biblioteca, Internet, Reasoning, Learning admission ni nuevas autoridades.

El test contractual RED certificado permanece integrado sin modificación semántica.

Validación disponible en el entorno de preparación:

- contrato INTEL-G2.1 dirigido: 5 PASS;
- regresión focalizada Memory/Config/Runtime/Learning: PASS;
- compilación sintáctica: PASS;
- Ruff no disponible en el entorno de preparación;
- suite completa no ejecutada aquí; certificación final corresponde al entorno local del usuario.
