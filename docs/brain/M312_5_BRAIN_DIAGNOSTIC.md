# M312.5 — Diagnóstico controlado del BRAIN

M312.5 agrega una fachada y una herramienta de línea de comandos para observar,
en modo de solo lectura, los recuerdos que el BRAIN puede recuperar desde su
repositorio local y desde la memoria oficial histórica.

## Uso

```powershell
python scripts/brain_diagnostic.py --owner Carlos --query clima
```

También puede indicarse otra raíz del proyecto y un límite:

```powershell
python scripts/brain_diagnostic.py `
  --owner Carlos `
  --query preferencias `
  --limit 10 `
  --project-root C:\Users\CAHCA\Desktop\HAL
```

La salida es JSON e informa:

- consulta aplicada;
- cantidad total;
- cantidad local;
- cantidad proveniente de memoria oficial;
- origen, tipo, sujeto y contenido de cada resultado;
- marca `read_only` para recuerdos históricos oficiales.

## Límites de seguridad

- no se conecta a `main.py`;
- no modifica `runtime_root_factory.py`;
- no escribe en la memoria oficial;
- no llama a `BrainService.remember`, `update`, `forget` ni `expire`;
- crea la integración histórica con aprendizaje deshabilitado;
- no modifica las respuestas visibles de ROBY.
