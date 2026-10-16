# M386.7 — Arquitectura cognitiva objetivo

## Propósito

M386.7 define el grafo canónico de un turno cognitivo futuro. No modifica el
runtime, no conecta componentes y no otorga autoridad nueva.

El diseño reutiliza el `UnifiedBrain`, la conversación oficial, las fachadas
canónicas y las autoridades existentes. El cerebro unificado coordina; no se
convierte en memoria, planificador, decisor, servicio de permisos o ejecutor.

## Grafo objetivo

```text
Entrada conversacional
        ↓
UnifiedBrain — coordinación sin autoridad de dominio
        ↓
Identidad y contexto ───────── Percepción y evidencia
        ↓                              ↓
Memoria y conocimiento ───── Clasificación epistemológica
        ↓                              ↓
Estado cognitivo y contexto relacional/afectivo
        ↓
Intención y razonamiento
        ↓
Planificación
        ↓
Seguridad, alcance y permisos
        ↓
Decisión
      ↙   ↘
Respuesta  Compuerta de acción
      ↘   ↙
Reflexión posterior
        ↓
Candidato de aprendizaje
        ↓
Diagnóstico unificado
```

El grafo representa un turno y es acíclico. Un aprendizaje aprobado podrá
afectar turnos futuros mediante su autoridad, pero no retroalimenta ni reescribe
el turno actual.

## Autoridades canónicas preservadas

| Dominio | Autoridad objetivo |
|---|---|
| Entrada | `OfficialConversationGateway` |
| Coordinación | `UnifiedBrain` |
| Memoria | `CanonicalMemoryFacade` |
| Estado cognitivo | `CanonicalCognitiveStateFacade` |
| Razonamiento | `GovernedReasoningManager` |
| Planificación | `CanonicalPlanningFacade` |
| Decisión | `CanonicalDecisionFacade` |
| Respuesta | `OperationalResponseAssembler` |
| Acción | compuerta de autonomía y `ToolGateway` |
| Reflexión | `CanonicalReflectionFacade` |
| Diagnóstico | `UnifiedBrainDiagnosticSnapshot` ampliado en el futuro |

## Estado real frente al objetivo

La arquitectura clasifica cada nodo como:

- `operational`: existe una autoridad productiva reconocida;
- `partial`: existen piezas reales, pero falta convergencia o cobertura completa;
- `contract_only`: el contrato existe pero todavía no influye en el runtime.

Línea base de M386.7:

- 10 nodos operativos;
- 7 nodos parciales;
- 1 nodo contractual: clasificación epistemológica M386.2.

`Operational` no significa nivel cognitivo alto. Solo indica que la autoridad ya
participa productivamente en algún alcance certificado.

## Invariantes

1. Existe una sola entrada conversacional.
2. Existe un solo coordinador cerebral.
3. El coordinador no absorbe autoridades de dominio.
4. La evidencia y su nivel epistemológico preceden al razonamiento.
5. Seguridad y permisos preceden a decisión, respuesta y acción.
6. Solo la compuerta oficial puede producir efectos externos.
7. Responder no implica actuar.
8. Reflexión y aprendizaje ocurren después del resultado.
9. El aprendizaje solo genera candidatos revisables.
10. El diagnóstico no expone contenido sensible ni concede autoridad.

## Rama de acción

La respuesta y la acción son ramas diferentes de una decisión. Una respuesta
puede entregarse sin ejecutar nada. La acción necesita además matriz M386.4,
nivel M386.5, límites M386.6, permiso, riesgo, reversibilidad y gateway.

M386.7 marca la compuerta de acción como parcial: existen las autoridades, pero
el grafo objetivo no activa una ruta autónoma nueva.

## Próxima convergencia

Las integraciones futuras deberán avanzar nodo por nodo, mediante adaptadores y
tests de no omisión. Un nodo no cambiará de `contract_only` o `partial` a
`operational` hasta demostrar participación real, diagnóstico y degradación
segura.

## Límites

El contrato vive en `core.cognitive_maturity.target_architecture`. M386.7:

- no cambia `UnifiedBrain`;
- no modifica el pipeline;
- no ejecuta herramientas;
- no persiste estado;
- no escribe memoria;
- no activa aprendizaje;
- no amplía autonomía;
- no crea un cerebro paralelo.
