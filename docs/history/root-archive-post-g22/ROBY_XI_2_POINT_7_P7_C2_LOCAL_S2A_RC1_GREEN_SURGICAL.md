# ROBY XI.2 — P7-C2-LOCAL-S2A-RC1 — GREEN QUIRÚRGICO

## Status

GREEN quirúrgico construido desde el CORRECTED RED Owner-certified.
Owner certification pending.

## Implementación mínima

- `GovernedInformationSources.admit_non_default(...)` admite una declaración
  explícita sólo en la instancia runtime existente; no modifica
  `DEFAULT_GOVERNED_INFORMATION_SOURCES`.
- `GovernedSourceQueryContract` expone delegación mínima hacia su registry ya
  poseído; no crea registry paralelo.
- `GovernedSourceQueryExecutor.register(...)` conserva la autoridad única de
  registro, valida identidad declaración/registro, falla cerrado ante fuente
  desconocida sin declaración y admite metadata inmutable antes del adapter.
- `FoursquareGovernedSourceAdapter` porta su declaración inactiva, mantiene
  credencial obligatoria, transporte inyectable y ejecución explícita.
- `runtime_environment_wiring` agrega construcción credential-gated mediante
  `SecretsLoader` + `environment_flag`.

## Invariantes

- `OfficialConversationGateway` permanece byte-identical:
  `05626c7376b1ebe36b82b6c7c4503b88f6a101e2ba585947493044c8238d36f8`.
- Default M343.5 permanece en seis fuentes.
- No segundo registry/query contract/executor.
- Registro ≠ ejecución de red.
- No IP fallback implícito.
- No Memory/Learning/Planning/Execution.
- No reserva/booking/navegación.

## Verificación local disponible

- contrato focal RC1: 16 PASS / 0 FAIL;
- M343.5 + M344.0 + M344.1: 25 PASS / 0 FAIL;
- `py_compile`: PASS;
- M361 regenerado;
- líneas modificadas <= 88 caracteres;
- Ruff no está instalado en este entorno, por lo que la certificación final
  corresponde al Owner gate completo.

## STOP

GREEN BUILT → OWNER CERTIFICATION PENDING → STOP.
