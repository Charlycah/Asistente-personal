# ROBY XI.2 — Governed Model/Backend Canonical Action-Specific Authorization
## RED contractual — reconciliación de alcance y readiness

**Estado:** RECONCILIACIÓN DOCUMENTAL / CONDITIONAL HOLD — NO RED EJECUTABLE AUTORIZADO.
**Baseline de entrada:** ZIP `ROBY_XI_2_GOVERNED_MODEL_BACKEND_CANONICAL_AUTHORIZATION_TO_EXECUTION_SURGICAL_RECONCILIATION(1).zip`; diseño posterior `ROBY_XI_2_GOVERNED_MODEL_BACKEND_ACTION_SPECIFIC_AUTHORIZATION_EXTENSION_CONTRACT_DESIGN.zip`, sujeto a certificación Owner. Registro Owner aportado: Ruff limpio, 13.650 PASS, sin atribuirlo a este documento nuevo.

## Autoridades existentes y frontera

- `GovernedMultiStepInvestigationAuthorizationReentryV1`: Authorization A2 específica de investigación; **no** concede `MODEL_ACQUISITION`.
- `GovernedLevel2ReadOnlyExecutionGatewayV1` → `OfficialRuntimeCapabilityRegistry` → `OfficialCapabilityGateway`: ejecución Level 2 de solo lectura; **no** descarga modelos.
- `ExternalResourceRegistryAuthority`: declaraciones de recursos; no permiso de red/OS.
- `GovernedIndependenceAuthorizationBoundaryV1`: elegibilidad consultiva; `execution_authorized=False`.
- `core/cognitive_memory_neural_acquisition_authorization_contract.py`: predicado preflight puro; elegibilidad positiva no equivale a autorización ejecutable.
- Owner identity, attestation, revocation, replay y canonical execution-grant para `MODEL_ACQUISITION`: **UNMAPPED** según documentación examinada.

## Matriz de contratos RED propuestos, condicionados a mapeo y certificación

| Caso | Entrada negativa | Resultado contractual esperado |
|---|---|---|
| R01 | Ausencia de capability/action mapping canónico | DENY, cero efectos |
| R02 | Evidencia Owner sintética/no autenticada | DENY, cero efectos |
| R03 | Digest de request, acción, revisión o artefactos no coincidente | DENY, cero efectos |
| R04 | Aprobación expirada, prematura o revocada | DENY, cero efectos |
| R05 | Fuente de revocación inaccesible o desactualizada | DENY, cero efectos |
| R06 | Nonce/invocación repetida o consumo no atómico | DENY, cero efectos |
| R07 | Redirect, origen o artefacto fuera de allowlist | DENY, cero efectos |
| R08 | Symlink/path escape o caché implícita no autorizada | DENY, cero efectos |
| R09 | Violación de privacidad, límites de bytes/tiempo/red | DENY, cero efectos |
| R10 | Auditoría requerida ausente o fallida | DENY, cero efectos |
| R11 | Intento de heredar permiso para instalación/ONNX/inferencia/benchmark/admisión | DENY, cero efectos |
| R12 | Preflight elegible sin aprobación ejecutable exacta | DENY, cero efectos |

**Condición de tests:** fixtures deterministas, offline, sin efectos externos, y anclados a la autoridad canónica **verificada**. Esta matriz es especificación para futuro RED; **no se han incorporado tests nuevos**.

## Bloqueos previos al RED ejecutable

1. Certificación Owner del diseño Action-Specific Authorization.
2. Mapeo explícito del capability ID, autoridad Authorization existente y seam Execution oficial aptos para efectos de `MODEL_ACQUISITION`.
3. Identificación de autoridades ya gobernadas para identidad Owner, evidencia auténtica, revocación, reloj y ledger antirreplay; no inventar un AuthorizationManager.
4. Aprobación Owner del alcance inmutable, hashes y procedencia verificados, aislamiento, límites y auditoría.
5. Autorización Owner **separada** para crear RED offline; ninguna autorización de adquisición.

## Dictamen

**RED READINESS: CONDITIONAL HOLD.** No avanzar a RED ejecutable, GREEN ni adquisición hasta satisfacer los bloqueos. Preservar la arquitectura, imports ordenados, Ruff, baseline M361 y documentación sincronizada. Ningún cambio de código, test, dependencia, runtime o registro de capacidades fue realizado por este documento.

**STOP: MODEL_ACQUISITION NO-GO.** Sin descarga, instalación, exportación ONNX, inferencia, benchmark ejecutado, admisión o integración productiva.
