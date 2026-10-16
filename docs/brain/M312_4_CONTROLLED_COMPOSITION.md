# M312.4 — Composición controlada

La primera composición real del BRAIN se realiza únicamente por una fábrica
explícita:

```text
MemoryRuntimeIntegration
          ↓
OfficialMemoryGateway
          ↓
OfficialMemoryBrainAdapter (solo lectura)
          ↓
BrainService
```

La fábrica no es llamada por el runtime principal. Su uso queda limitado a
pruebas, herramientas de diagnóstico o futuras integraciones deliberadas.

Esto permite validar la puerta única del BRAIN con el almacenamiento oficial
real sin modificar todavía el comportamiento conversacional de ROBY.
