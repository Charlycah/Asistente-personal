# M347.14 — Pruebas integrales cognitivas

## Objetivo

Consolidar la Fase 4 mediante escenarios integrales que demuestren que las
capacidades incorporadas entre M347.4 y M347.13 operan como un único pipeline
cognitivo, sin añadir comportamiento productivo nuevo.

## Alcance

La suite `tests/test_m347_14_integral_cognitive_tests.py` recorre conjuntamente:

1. clasificación cognitiva e intención interactiva;
2. planificación y selección de acción;
3. contexto conversacional y traza canónica;
4. política explícita de escritura;
5. persistencia autorizada en el store existente;
6. recuperación relevante con umbral;
7. continuidad entre sesiones mediante `RuntimeSessionProfile`;
8. aislamiento de recuerdos entre perfiles;
9. construcción segura del contexto de memoria para el prompt.

## Escenarios consolidados

- Un turno de proyecto se clasifica, planifica, traza y persiste solamente
  cuando la política de escritura lo autoriza.
- Un recuerdo persistido en una sesión se recupera en otra sesión del mismo
  perfil y se proyecta mediante `MemoryPromptContextBuilder`.
- La misma instancia de `ConversationContext` llega a estrategia, traza y
  señales de recuperación.
- Una corrección queda en revisión y no agrega una segunda verdad a la memoria.
- Un recuerdo perteneciente a otro perfil no se recupera ni se proyecta al
  contexto del prompt.
- Las decisiones serializadas contienen hechos observables, no contenido de
  memoria, prompts ni razonamiento privado.
- Desactivar aprendizaje o recall no evita la clasificación, planificación ni
  trazabilidad del turno.

## Autoridades preservadas

M347.14 no crea:

- otro analizador de intención;
- otro planificador;
- otro modelo de contexto;
- otra política de aprendizaje;
- otro store o recuperador;
- otro gestor de sesiones;
- otro constructor de prompts.

La suite utiliza exclusivamente las autoridades canónicas ya existentes.

## Resultado esperado

La Fase 4 queda consolidada cuando las pruebas integrales y la regresión completa
pasan junto con `ruff check .`, demostrando que el flujo es compatible hacia
atrás y que no existen rutas paralelas para las responsabilidades verificadas.
