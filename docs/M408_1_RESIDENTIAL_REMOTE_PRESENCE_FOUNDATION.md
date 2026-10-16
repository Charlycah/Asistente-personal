# M408.1 — Residential Remote Presence Foundation

**Baseline de partida:** M407.3 certificada · 11.232 tests · Ruff limpio · M361 sincronizada.

## Objetivo

Materializar la primera capability de presencia residencial remota sin abrir UI, Internet,
VPN, streaming ni deployment físico: una petición explícita desde Primary Home puede pedir
una única imagen fija actual de una fuente M404 autorizada y recibirla como media transitoria
`SENSITIVE` sobre el carrier M398 ya establecido.

## Contrato de petición y admisión

`ResidentialObservationRequest` sólo admite `STILL_IMAGE` y exige captura fresca. La
pre-admission compone facts existentes y no crea authority nueva:

- sesión/readiness M397 actual;
- requester/target ResidenceId coherentes;
- binding/capability M404 coherentes;
- resource authorization M394;
- permiso/consentimiento `camera.capture` M61/M63.

Una limitación en cualquiera de estas fronteras bloquea antes de activar físicamente la
cámara.

## Captura M404 única

M408.1 conserva `ResidentialPhysicalObservation` como metadata/provenance-only. Los bytes
raw nunca entran en su payload.

`GovernedLocalCameraMediaCapture` ejecuta `camera.capture` por Tool Gateway una sola vez y
entrega el mismo resultado al nuevo seam público `admit_capture_result()` de M404. De este
modo `CameraFrame.frame_id` y `ResidentialPhysicalObservation.acquisition_reference`
permanecen correlacionados sin una segunda captura.

La entrega de media sólo se habilita si la observation M404 queda `ADMITTED`.

## Media transitoria sensible

Toda imagen residencial de la foundation se clasifica con la taxonomía canónica M405 como
`InformationClassification.SENSITIVE`.

`TransientMediaReference` contiene únicamente metadata opaca y de vida corta:

- media id;
- content type (`image/jpeg` o `image/png`);
- byte length;
- digest SHA-256;
- clasificación;
- timestamps de creación/expiración.

No contiene path, URL, endpoint, credential ni bytes. No se añade persistencia en disco,
cache histórica ni replay.

## Entrega binaria bounded

M398 permanece hash-cerrado e intacto. M408.1 no añade archivos ni API a
`core/physical_transport`.

`BoundedMediaFrameCodec`, propiedad de la capability Remote Presence, consume solamente un
`TcpCarrierConnection` M398 ya establecido. El framing no conoce cámara, M404 ni M405.

Límites foundation:

- `MAX_STILL_IMAGE_BYTES = 8 MiB`;
- `MAX_MEDIA_CHUNK_BYTES = 64 KiB`;
- `MAX_MEDIA_CHUNKS = 128`;
- una transferencia corresponde a `(session_id, request_id, media_id)`;
- orden de chunks estricto;
- digest final obligatorio;
- EOF, session mismatch, request/media mismatch, orden incorrecto o digest inválido abortan.

No se implementa resume tras reconnect. Una nueva session requiere una nueva request y una
nueva captura.

## Ownership preservado

- M394: resource registration/authorization.
- M396: residence identity/admission context.
- M397: peer authentication, session y communication readiness.
- M398: carrier físico TCP y recovery; sin cambios.
- M404: physical observation identity/provenance/admission.
- M405: clasificación canónica.
- M61/M63: tool execution permission/consent.
- M408.1: request composition + transient media delivery solamente.

## Fuera de alcance

No incluye M403 media sync, M406, conversación, streaming/video, audio, PTZ, recording,
history, autonomous capture, alerts, second socket/port, public HTTP, VPN, cloud relay,
Internet exposure, mini-PC ni service/autostart del SO.

## Criterio de terminación

M408.1 queda software-completo cuando una request autorizada produce exactamente una
captura M404, genera una referencia `SENSITIVE` transitoria, entrega los bytes bounded por
un carrier M398 existente y verifica igualdad/digest en recepción, mientras cualquier
fallo de session/permission/resource/admission impide captura o entrega según corresponda.
