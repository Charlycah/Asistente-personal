# Certificación RP.18.2B

Entrega: raíz oficial de composición y lifecycle unificado.

Validaciones esperadas en el entorno doméstico certificado:

```powershell
ruff check .
pytest
```

La entrega preserva compatibilidad, no retira código histórico y concentra el
arranque/apagado oficial en `OfficialROBYRuntime`.
