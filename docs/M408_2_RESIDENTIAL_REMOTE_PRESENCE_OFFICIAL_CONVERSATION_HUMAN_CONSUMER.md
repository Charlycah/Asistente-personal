# M408.2 — Residential Remote Presence — Official Conversation Human Consumer

## Estado

Implementación mínima del consumer conversacional humano sobre M408.1. No reabre la
foundation física ni introduce otra autoridad de cámara, transporte o autorización.

## Ruta oficial

La petición visual explícita entra por `OfficialConversationGateway`, es seleccionada por
`OfficialRuntimeCapabilityRegistry`, ejecutada mediante `OfficialCapabilityGateway` y
entregada al `ResidentialRemotePresenceConversationInterceptor`.

Descriptor canónico: `residential.remote_presence`, `CAMERA`, `HIGH`, `DEVICE`, sin segunda
confirmación conversacional. Los triggers son frases visuales completas; preguntas ambiguas
sobre la casa o la cámara no son triggers de captura.

## Execution port

El consumer depende de `ResidentialRemotePresenceExecutionPort`. No construye `CameraProvider`,
M397, M398 ni M404. La implementación física/productiva se provisionará desde la composición
residencial; si no existe execution port la capability no se registra. Si se habilita
explícitamente Remote Presence sin provisionar el port, el runtime falla cerrado.

## Presentación transitoria

`TransientMediaPresentationPort` es memory-only, bounded y consume-once. La imagen mantiene
`InformationClassification.SENSITIVE`, TTL inicial de 30 segundos y máximo una presentación
pendiente por sesión. No existe history, latest-image, filesystem, JSONL ni database.

Los bytes no entran en `LocalConversationTurn`, `OperationalResponse`, journal, traces,
recent context ni cognitive memory. El `repr` del objeto de presentación tampoco expone los
bytes.

## Observabilidad

`GovernedOperationalInterception` puede declarar `network_access_performed`, con `False` por
defecto para preservar todos los interceptors históricos. La pipeline propaga esa lineage
hacia `OperationalResponse` y `GovernedConversationPipelineResult` mediante una evidencia de
network externa explícita. `platform_mutation_performed` permanece siempre `False`.

## Fuera de alcance

M406, Internet/VPN, mini-PC físico, public remote access, streaming/video, visual
interpretation, alertas, recording, history, autonomous capture y persistencia de media.

## Criterio de terminación

Una solicitud visual explícita selecciona una única capability oficial, M408.1 produce una
imagen validada, el sidecar la presenta una sola vez y el turno conversacional sólo conserva
texto seguro. Ningún artifact persistente puede reconstruir la imagen.
