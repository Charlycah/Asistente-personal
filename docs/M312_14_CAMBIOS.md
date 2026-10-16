# M312.14 — Composición controlada del diagnóstico conversacional

## Objetivo

Incorporar el diagnóstico de M312.13 a la composición de identidad sin conectarlo
al runtime visible ni alterar la preparación del paquete conversacional.

## Incorporado

- `IdentityMemoryBrainComposition.conversation_context_diagnostic`
- una única instancia compuesta sobre el preparador oficial de M312.12
- reutilización desde `scripts/conversation_context_diagnostic.py`
- pruebas de composición, identidad de dependencias y operación de solo lectura

## Garantías

- no se conecta a `main.py`
- no se conecta a `runtime_root_factory.py`
- no modifica respuestas visibles
- no escribe memorias, perfiles ni sesiones
- conserva el preparador y el diagnóstico existentes
- cambio reversible eliminando un único campo de composición

## Validación requerida

```text
ruff check .
pytest -q
```
