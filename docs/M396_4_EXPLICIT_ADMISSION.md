# M396.4 — Explicit Admission

## Estado

Incremento de endurecimiento arquitectónico de M396 dedicado al invariante
**M396-I04 — Explicit Admission**.

M396.4 convierte la regla `detected != admitted` en un contrato ejecutable del dominio
Residence sin introducir descubrimiento, red, pairing, autenticación ni una nueva
autoridad productiva.

## Línea base

Parte de M396.3 certificada con Ruff limpio, baseline M361 sincronizada,
10.370 tests aprobados y cero regresiones.

## Principio protegido

> Ningún dispositivo, proceso, endpoint o recurso observado puede convertirse por sí
> mismo en residencia extendida de ROBY.

La observación produce como máximo un `ResidenceCandidate`. Una residencia con rol
`EXTENDED` exige proveniencia explícita mediante `admission_id`. La decisión puede
quedar representada de forma inmutable en `ResidenceAdmissionRecord` como `ADMITTED`
o `REJECTED`.

## Contratos

- `ResidenceCandidate`: descripción inmutable de algo observado. No es una residencia.
- `ResidenceAdmissionDecision`: `ADMITTED` o `REJECTED`.
- `ResidenceAdmissionRecord`: evidencia declarativa de una decisión explícita, con
  identificador, candidato, `ResidenceId`, origen de la decisión, fecha y razón.
- `ResidenceDescriptor.admission_id`: proveniencia obligatoria para `EXTENDED`.
- `PRIMARY_HOME`: conserva la excepción constitucional de bootstrap y no requiere un
  `admission_id` para representar el hogar canónico ya existente.

## Barreras

M396.4 no añade métodos que admitan candidatos, no modifica
`ExternalResourceRegistryAuthority`, no altera `OfficialDeviceGateway`, no cablea
Residence en `runtime_root_factory` y no realiza descubrimiento automático.

No incorpora Wi-Fi, LAN, mDNS, Bluetooth, HTTP, sockets, tokens, credenciales,
pairing, autenticación ni aprobación remota.

## Flujo semántico futuro

```text
observed resource
      |
      v
ResidenceCandidate
      |
      | explicit governed decision outside Residence Domain
      v
ResidenceAdmissionRecord
      |
      | admitted provenance
      v
ResidenceDescriptor(role=EXTENDED)
```

El dominio representa el resultado y su proveniencia; no posee la autoridad para tomar
la decisión.

## Criterio de cierre

M396.4 queda apto para certificación cuando:

1. un candidato nunca sea una residencia por identidad o descubrimiento;
2. toda residencia `EXTENDED` requiera proveniencia explícita de admisión;
3. `PRIMARY_HOME` preserve su continuidad de bootstrap;
4. una decisión rechazada no produzca residencia por efecto automático;
5. Residence continúe sin authority/manager/gateway/orchestrator productivo;
6. Ruff quede limpio;
7. baseline M361 sea reproducible;
8. la suite completa finalice sin regresiones.
