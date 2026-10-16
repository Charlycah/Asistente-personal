# M396.5 — Stable Residence Identity

## Estado

Incremento de endurecimiento arquitectónico de M396 dedicado al invariante
**M396-I05 — Stable Residence Identity**.

M396.5 refuerza la identidad lógica de residencia sin introducir descubrimiento,
autenticación, transporte, persistencia ni una nueva autoridad productiva.

## Línea base

Parte de M396.4 certificada con Ruff limpio, baseline M361 sincronizada,
10.392 tests aprobados y cero regresiones.

## Principio protegido

> La identidad lógica de una residencia permanece estable aunque cambien atributos
> temporales del entorno o de la conectividad.

`ResidenceId` continúa siendo la identidad canónica del lugar de residencia. No se
deriva de IP, hostname, puerto, URL, MAC, SSID, sesión, nombre visible, capacidad,
estado de presencia o recurso temporal asociado.

## Contrato nuevo

`ResidenceIdentityAnchor` representa de forma inmutable la proveniencia de una
`ResidenceId` estable. El origen puede ser:

- `PRIMARY_HOME_BOOTSTRAP`: continuidad constitucional del hogar canónico;
- `EXPLICIT_ADMISSION`: identidad establecida a partir de una admisión explícita y
  trazable de M396-I04.

Para `EXPLICIT_ADMISSION`, `origin_reference` identifica la evidencia de admisión. El
hogar primario no usa una referencia de admisión.

El anchor no contiene datos de red, conectividad, hardware o sesión y no ejecuta
ninguna operación.

## Separación identidad / entorno

Los cambios siguientes no alteran por sí mismos una `ResidenceId`:

```text
label
resource_ids
capabilities
limitations
presence_state
observed_at
network/session details managed outside Residence identity
```

Por ejemplo, una mini-PC puede cambiar de red, IP, nombre visible o recursos
observados y continuar siendo la misma residencia lógica de ROBY.

## Barreras

M396.5 no:

- genera identidad desde IP, hostname, MAC o datos de red;
- descubre hardware;
- autentica dispositivos;
- realiza fingerprinting físico;
- crea pairing;
- abre conexiones;
- persiste identidades;
- modifica autoridades M394/M395;
- cablea Residence en `runtime_root_factory`;
- crea authority, manager, gateway u orchestrator.

## Relación con I04

I04 responde: **¿esta residencia fue admitida explícitamente?**

I05 responde: **una vez establecida su identidad, ¿sigue siendo la misma residencia
cuando cambia su entorno?**

La respuesta constitucional es sí mientras la `ResidenceId` gobernada permanezca
vigente. Los atributos externos describen el entorno; no redefinen la identidad.

## Criterio de cierre

M396.5 queda apto para certificación cuando:

1. `ResidenceId` permanezca mínima y opaca;
2. exista proveniencia inmutable para identidad estable;
3. identidad no incorpore locators transitorios;
4. cambios de label, recursos, capacidades o presencia no cambien `ResidenceId`;
5. I03 e I04 permanezcan intactos;
6. Ruff quede limpio;
7. baseline M361 sea reproducible;
8. la suite completa finalice sin regresiones.
