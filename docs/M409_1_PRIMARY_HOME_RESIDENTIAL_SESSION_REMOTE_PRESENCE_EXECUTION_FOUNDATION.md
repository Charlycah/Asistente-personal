# ROBY XI.2 — M409.1 Primary Home Residential Session & Remote Presence Execution Foundation

## Estado

Implementación mínima de la frontera Primary Home previa a la selección de red privada.

## Objetivo

Cerrar el handoff productivo entre el carrier M398 aceptado por Primary Home, la sesión M397 corriente y el `ResidentialRemotePresenceExecutionPort` consumido por M408.2, sin crear otro transporte, otra autoridad ni un segundo socket.

## Cadena

Residential Node M407 dial/reconnect → M398 `LocalTcpListener.accept()` en Primary Home → M397 authentication/admission/session → `PrimaryHomeResidentialSessionHost` → single-reader CONTROL/MEDIA dispatch → `PrimaryHomeRemotePresenceExecutionAdapter` → M408.2.

## Componentes añadidos

- `PrimaryHomeResidentialSessionConfig`
- `PrimaryHomeResidentialSessionHost`
- `PrimaryHomeResidentialSessionSnapshot`
- `ResidenceChannelDispatcher`
- `ResidenceInboundFrame`
- `PrimaryHomeRemotePresenceExecutionAdapter`
- `PrimaryHomeRemotePresenceExecutionConfig`

## Invariantes

- aceptar TCP no implica sesión ROBY lista;
- M397 sigue siendo owner de authentication/admission/session/readiness;
- M398 sigue siendo owner de listener/carrier/channel;
- una sola sesión/carrier corriente por residencia en esta foundation;
- estado de sesión sólo en memoria;
- un único owner ejecuta `recv()` sobre el carrier compartido;
- M408.2 continúa dependiendo sólo de `ResidentialRemotePresenceExecutionPort`;
- request, response y media se correlacionan por sesión/request/media;
- request y response usan el mismo carrier bidireccional;
- ningún segundo socket Primary → Residential es creado;
- Primary Home no adquiere autoridad de cámara;
- pérdida de carrier invalida la sesión corriente y falla cerrado;
- reconexión sigue perteneciendo al Residential Node / M407;
- no hay VPN, exposición Internet, mini-PC físico, streaming ni persistencia de media en M409.1.

## Alcance de validación

Los tests M409.1 prueban fail-closed antes de M397, autenticación/admisión, sesión corriente, mismo carrier bidireccional, ejecución sin sesión, shutdown, single-reader ownership, preservación de M408.2 y ausencia de persistencia de sesión.

## Límite físico pendiente

M409.1 no selecciona ni instala una red privada. Una vez certificado, el siguiente paso es comparar tecnologías que proporcionen reachability privada y cifrada entre laptop y futuro Residential Node sin modificar esta arquitectura ROBY.
