# ROBY XI.2 — RF-H Object-Aware / Relational Role Binding v1

## Estado del contrato

Implementation v1 extiende el contrato existente de instanciación contextual sin crear una nueva authority, un nuevo modelo de claim ni un repositorio relacional paralelo.

## Gap cerrado

Los templates contextuales podían ligar el sujeto a un `ContextualRuleRoleBinding`, pero su objeto sólo podía ser un literal. Esto impedía representar de forma abstracta una relación cuyo objeto fuera otra entidad ligada a un role del mismo caso.

## Implementación mínima

`ContextualRuleConditionTemplate` y `ContextualRuleConclusionTemplate` admiten ahora exactamente una de dos fuentes de objeto:

- `object_value`: literal legado;
- `object_role_id`: referencia explícita a otro role declarado en el mismo `ContextualRuleInstantiationSpec`.

`GovernedContextualRuleInstantiator` resuelve `object_role_id` exclusivamente mediante el mapa existente de `ContextualRuleRoleBinding` y proyecta el `entity_reference` resultante al `object_value` concreto. No hay reinterpretación por LLM ni una segunda vía de binding.

## Fail-closed

- un `object_role_id` no declarado invalida el spec;
- un role requerido sin binding produce `INSUFFICIENT_BINDINGS` sin regla parcial;
- bindings duplicados siguen produciendo `AMBIGUOUS_BINDINGS`;
- literal y role-object simultáneos son inválidos;
- ausencia de ambas fuentes de objeto es inválida.

## Invariantes preservados

- authority canónica: `governed_reasoning`;
- `Claim.subject/predicate/object_value` no cambia;
- no persistence;
- no Memory;
- no Learning;
- no world-model mutation;
- no action execution;
- no authority gain;
- session-local, read-only e inmutable;
- compatibilidad con templates literales existentes.

## Fuera de alcance

Esta implementación no introduce grounding semántico de Velar, propagación multi-hop, forward chaining general, grafos persistentes ni wiring adicional del runtime. Es exclusivamente la primitive de representabilidad/binding necesaria para que un objeto relacional pueda provenir de otro role explícitamente ligado.
