# M363 — Windows Workspace Foundation

**Estado:** Vigente  
**Predecesor canónico:** M362 — Governed Vision Gateway  
**Naturaleza:** Fundación de aplicación y gobierno; sin automatización destructiva

## Propósito

M363 establece una única frontera gobernada para observar y preparar operaciones
sobre el workspace de Windows. No reemplaza la UI de escritorio ni el runtime
conversacional existentes. Tampoco introduce macros, control remoto o ejecución
automática de teclado y ratón.

## Autoridad canónica

`OfficialWindowsWorkspaceGateway` es el único punto de entrada de aplicación para
las capacidades del workspace. Los proveedores de plataforma quedan detrás del
contrato `WindowsWorkspaceProvider`.

La fundación distingue tres niveles:

- `READ_ONLY`: ventana activa, ventanas, procesos y captura de pantalla.
- `REVERSIBLE`: abrir una aplicación o una ruta.
- `SENSITIVE`: cerrar aplicaciones, terminar procesos, mover o borrar rutas y
  automatizar entrada.

## Regla de ejecución

M363 sólo observa y prepara acciones. Todo `WorkspaceActionPlan` declara
`executable=False`. Las mutaciones reales deberán atravesar en un milestone
posterior el `ToolGateway`, sus políticas, consentimiento, confirmación y
trazabilidad.

Una acción sensible requiere simultáneamente:

- solicitud explícita del usuario;
- consentimiento explícito;
- confirmación independiente.

## Integración con Vision

El gateway puede solicitar una captura al proveedor y entregarla al
`GovernedVisionGateway`. El almacenamiento sigue bajo las reglas de M362: una
captura no se conserva por defecto y la persistencia requiere solicitud y
consentimiento explícitos.

```text
WindowsWorkspaceProvider
        │
        ▼
OfficialWindowsWorkspaceGateway
        │
        ▼
GovernedVisionGateway
        │
        ▼
ImageRepository
```

## Límites

M363 no incorpora:

- ejecución de aplicaciones o comandos del sistema;
- cierre o terminación de procesos;
- movimiento o borrado de archivos;
- entrada automática de teclado o ratón;
- acceso remoto;
- nuevas dependencias obligatorias de Windows;
- almacenamiento silencioso de capturas.

## Quality gates

- Ruff limpio.
- Suite completa en verde.
- Un único gateway oficial del workspace.
- Proveedores detrás de protocolos.
- Ninguna mutación ejecutable en M363.
- Consentimiento visual heredado de M362.
- Documentación y changelogs alineados.
