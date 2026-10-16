# M96 — Reflection Generation

## Objetivo
Construir un borrador conversacional acotado, trazable y revisable a partir de una oportunidad ya gobernada y temporalmente habilitada.

## Alcance
- Estados `generated`, `abstained` y `review_required`.
- Formas de respuesta, pregunta, observación, conexión y continuación.
- Tonos neutral, curioso, reflexivo y cálido.
- Composición determinista desde `content_hint`, razón y fuentes existentes.
- Límite configurable de longitud.
- Persistencia mediante contrato y repositorio en memoria.
- Integración estricta con decisiones M93 y M95.

## Invariantes
1. M96 no decide si hablar ni cuándo hacerlo.
2. Sin autorización M93 o ventana M95 abierta, se abstiene.
3. Revisión requerida nunca se convierte en contenido automático.
4. `wait` y `silence` nunca generan borradores.
5. Las reflexiones no explícitas requieren referencias de fuente por defecto.
6. No se inventan hechos ni se consulta un LLM.
7. M96 no envía, agenda, ejecuta herramientas ni modifica memoria.
8. El borrador conserva los identificadores de gobernanza, timing y fuentes.

## Integración

```text
M94 detecta -> M95 habilita ventana -> M93 autoriza -> M96 compone borrador
```

## Fuera de alcance
- LLM o generación abierta.
- Entrega por texto o voz.
- Selección de canal.
- Programación de intervenciones.
- Mutación de memoria o relación.
- Aprendizaje desde la reacción del usuario.

## Criterios de aceptación
- API pública desde `core.living_conversation`.
- Borradores inmutables, deterministas y persistibles.
- Abstención segura ante falta de contenido, fuentes o autorización.
- Compatibilidad completa con M1–M95.
- Ruff limpio y suite completa sin regresiones.
