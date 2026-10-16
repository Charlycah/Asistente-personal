# M312.11 — Diagnóstico de contexto personal

Se añadió una herramienta manual y de solo lectura para inspeccionar el contexto
seguro que recibiría una identidad activa antes de conectar el BRAIN al runtime.

## Componentes

- `PersonalContextDiagnostic`
- `PersonalContextDiagnosticReport`
- `PersonalContextDiagnosticEntry`
- `scripts/personal_context_diagnostic.py`

## Garantías

- No modifica `main.py` ni `runtime_root_factory.py`.
- No escribe recuerdos ni perfiles.
- Expone identidad, evidencia, sujetos permitidos y contexto visible.
- Una identidad desconocida o conflictiva no recibe contexto privado.
- El script abre la memoria histórica con aprendizaje deshabilitado.
