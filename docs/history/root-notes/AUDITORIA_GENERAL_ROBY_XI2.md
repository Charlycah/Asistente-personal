# Auditoría general de ROBY XI.2 — RP.23.1

## Alcance

Auditoría estática y funcional de la base RP.22.18, validada con 6792 pruebas.
El repositorio contiene más de mil módulos Python y más de cuatrocientos archivos
de pruebas. La arquitectura está organizada en capas de dominio, aplicación,
infraestructura, interfaces y un núcleo cognitivo extensivo.

## Capacidades verificadas

- Conversación contextual, continuidad, reparación y adaptación.
- Identidad estable de ROBY y contexto del hogar.
- Memoria cognitiva, recuperación, sanitización e integración.
- Planificación, arbitraje, explicación y registro de decisiones.
- Registro y selección declarativa de capacidades y herramientas.
- Observabilidad, métricas, diagnóstico y trazabilidad local.
- Detección, priorización, consolidación y ciclo de vida de anomalías.
- Comparación, evaluación y orientación operativa no ejecutable.
- Integración de escritorio, dispositivos, voz y contexto ambiental.
- Recordatorios, calendario, correo, archivos, web y clima mediante adaptadores.
- Resiliencia, recuperación de fallos y validación de arquitectura.

## Hallazgos

1. La cobertura automatizada es amplia y la suite se mantiene sin regresiones.
2. La separación por módulos reduce el acoplamiento, aunque aumenta el costo de
   navegación y exige mantener catálogos y documentación actualizados.
3. La identidad de Carlos y Cristina ya aparecía en `core.identity`, pero estaba
   fijada en código y no era editable como configuración privada.
4. Las credenciales están conceptualmente separadas. Los nombres personales no
   deben almacenarse como API keys ni mezclarse con secretos.
5. Existen capacidades declarativas que requieren adaptadores, permisos y
   configuración externa para operar en un equipo real.

## Resultado RP.23.1

Se añadió un perfil TOML local, atómico y editable, separado de credenciales:

- Windows: `%APPDATA%\\ROBY\\profile.toml`
- Linux/macOS: `~/.config/roby/profile.toml`
- Override: variable `ROBY_PROFILE_PATH`

La entrega incluye un perfil inicial con `CARLOS` y `CRISTI`, más operaciones de
lectura, actualización y borrado. El perfil no concede permisos ni autentica
servicios.

## Riesgos y recomendaciones

- No publicar perfiles personales ni archivos de credenciales.
- Mantener confirmación humana para acciones externas o destructivas.
- Ejecutar `ruff check .` y `pytest -q` antes de cada entrega.
- Mantener un catálogo de capacidades con estado real: disponible, limitada,
  interna o pendiente de integración.
