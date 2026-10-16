# M396.1 — Constitución Arquitectónica de Residencia Distribuida

## Estado

Definición constitucional de la nueva época M396. No introduce todavía transporte,
sincronización, procesos remotos ni una nueva autoridad productiva.

## Línea base heredada

M396.1 parte de M395.5 y la hereda íntegramente. La arquitectura certificada, sus
autoridades, contratos, composición, runtime y comportamiento local permanecen
vigentes salvo decisión arquitectónica posterior, explícita y certificada.

La residencia local cerrada en RP.23.2 se reinterpreta evolutivamente como la
**residencia primaria** de ROBY. Esta reinterpretación no reemplaza ni invalida la
residencia local: la preserva como hogar operacional canónico.

## Principio rector

> **Una casa. Un ROBY. Muchas ventanas.**

ROBY XI.2 es una única entidad cognitiva gobernada. Puede ampliar su presencia a
otros entornos autorizados sin multiplicar identidad, memoria, personalidad,
aprendizaje, modelo mental, planificación ni autoridad cognitiva.

La distribución pertenece a la **residencia y presencia de ROBY**, no a la
existencia de múltiples ROBY.

## Definiciones constitucionales

### ROBY Identity

Identidad única y continua de ROBY. No se replica por dispositivo, proceso,
interfaz, nodo o sesión.

### Primary Residence

Hogar operacional canónico de ROBY. En la línea base M396.1 corresponde a la
laptop local ya certificada por RP.23.2.

La residencia primaria no cambia automáticamente por disponibilidad, latencia,
conectividad, duración de sesión ni preferencia aprendida.

### Extended Residence

Entorno autorizado en el que el mismo ROBY puede prolongar su presencia y disponer
de capacidades declaradas. Una mini-PC o un celular pueden llegar a desempeñar
este papel mediante contratos posteriores.

Una residencia extendida no constituye una copia, clon, réplica ni segundo núcleo
de ROBY.

### Presence Endpoint

Punto de interacción desde el cual ROBY puede estar presente sin que dicho punto
constituya necesariamente una residencia completa. Una sesión web puede ser un
Presence Endpoint.

### Residence Awareness

Contexto objetivo que permite al ROBY existente conocer, cuando exista evidencia
gobernada suficiente:

- cuál es su residencia primaria;
- desde qué residencia o endpoint se origina una interacción;
- qué residencias o endpoints autorizados están declarados como disponibles;
- qué capacidades y limitaciones han sido declaradas para ese entorno.

Residence Awareness aporta contexto. No interpreta sentimientos, preferencias,
intenciones ni identidad personal.

### Interaction Locality

Identificación explícita del entorno desde el que se origina una interacción
concreta. ROBY puede estar disponible en varios entornos simultáneamente y, al
mismo tiempo, conocer la localidad de una interacción específica.

### Experiential Continuity

La experiencia contextual obtenida a través de una residencia o endpoint pertenece
al mismo ROBY. Sólo las autoridades cognitivas ya existentes pueden convertir esa
evidencia, cuando corresponda, en memoria gobernada, aprendizaje, modelo mental o
expresión de personalidad.

M396.1 no crea memoria por residencia, personalidad por dispositivo ni reglas de
preferencia codificadas por entorno.

## Mapa de autoridad y reutilización

M396.1 no introduce `DistributedResidenceAuthority`, `ResidenceManager`,
`ResidenceOrchestrator`, `ResidenceGateway` ni otro dueño productivo nuevo.

La auditoría de encaje con M395.5 establece las siguientes fronteras existentes:

- `ExternalResourceRegistryAuthority`: identidad, estado, autorización y
  conectividad **declarativa** de recursos externos; puede servir en incrementos
  posteriores como evidencia registral para nodos, dispositivos o interfaces sin
  convertirse por ello en autoridad cognitiva de residencia.
- `OfficialDeviceGateway` / `OfficialDeviceRuntimeGateway`: autoridad y fachada
  operacional de dispositivos; no son reemplazadas por M396.
- `core.device_continuity`: identidad estable de dispositivo y continuidad de
  sesión entre endpoints; no define hogar ni identidad de ROBY.
- `core.context_transfer`: manifiestos gobernados de contexto transferible; no
  transporta, sincroniza ni muta estado.
- `OfficialPresenceRuntimeGateway` y la cadena de Presence Context / Living
  Conversation Presence: representan presencia conversacional y awareness ya
  existente; no se reinterpretan como registro de residencias.
- `OfficialAmbientContextRuntimeGateway`: contexto ambiental declarado; no infiere
  residencia.
- `OfficialContextContinuityRuntimeGateway`: continuidad conversacional acotada a
  sesión; no define continuidad ontológica de ROBY.
- `ResidentComponentRegistry`: registro de componentes internos del runtime
  residente; queda expresamente separado de cualquier futuro registro lógico de
  lugares de residencia.

Toda integración M396 posterior deberá reutilizar estas autoridades según su
competencia y evitar absorberlas en una nueva superautoridad.

## Contrato conceptual mínimo

M396.1 fija semántica, no API productiva. Cualquier contrato de código posterior
deberá poder representar, como mínimo, sin mezclar transporte ni credenciales:

- una identidad estable de residencia;
- un rol de residencia (`primary` o `extended`) cuando corresponda;
- una etiqueta humana no autoritativa;
- una relación explícita con recursos/dispositivos ya gobernados;
- capacidades declaradas, sin convertir capacidad en permiso;
- estado administrativo independiente de presencia/disponibilidad;
- localidad de interacción independiente de identidad de ROBY.

Una dirección IP, hostname, URL, socket, token, password, ruta de base de datos o
credencial no forma parte de la identidad lógica de residencia.

## Invariantes M396.1

### M396-I00 — Continuidad Ontológica

Toda residencia extendida o punto de presencia pertenece al mismo ROBY XI.2.
Ningún nodo, dispositivo, interfaz o entorno distribuido constituye por sí mismo
una copia, clon, réplica o segunda instancia identitaria de ROBY.

### M396-I01 — Unique ROBY Identity

La existencia de múltiples residencias o endpoints nunca crea múltiples identidades
ROBY.

### M396-I02 — Unique Cognitive Authority

Ninguna residencia extendida puede constituir un núcleo cognitivo independiente.

### M396-I03 — Authority Preservation

M396 no absorbe responsabilidades pertenecientes a autoridades existentes.

### M396-I04 — Explicit Admission

Ningún recurso, dispositivo, proceso, interfaz o endpoint se convierte
automáticamente en residencia autorizada.

### M396-I05 — Stable Residence Identity

La identidad lógica de residencia debe ser estable e independiente de direcciones
de red temporales, hostname o una sesión concreta.

### M396-I06 — Primary Residence Preservation

La laptop local certificada permanece como residencia primaria inicial.

### M396-I07 — Local Equivalence

Sin residencias extendidas activas, ROBY debe conservar el comportamiento funcional
de la línea base M395.5.

### M396-I08 — Capability Is Not Authority

Que un entorno declare una capacidad no concede permiso ni autoridad para usarla.

### M396-I09 — No Implicit Replication

Registrar, reconocer o utilizar una residencia no replica automáticamente memoria,
estado cognitivo, conversaciones, archivos, bases de datos ni configuración.

### M396-I10 — Credential Isolation

`.roby/credentials.json` y cualquier secreto privado quedan fuera de todo mecanismo
genérico de residencia.

### M396-I11 — Failure Isolation

La indisponibilidad o fallo de una residencia extendida no puede provocar la caída
de la residencia primaria.

### M396-I12 — Revocability

Toda residencia extendida deberá poder dejar de pertenecer al conjunto autorizado
sin alterar la identidad de ROBY ni la integridad de su hogar.

### M396-I13 — Transport Independence

La semántica de residencia es independiente de HTTP, WebSocket, Bluetooth, LAN,
Internet o cualquier transporte concreto.

### M396-I14 — No Autonomous Promotion

Una residencia extendida no puede proclamarse ni promoverse automáticamente a
residencia primaria.

### M396-I15 — Governed Evolution

Toda futura capacidad distribuida debe integrarse mediante las autoridades que ya
gobiernan esa capacidad o mediante una decisión arquitectónica explícita, nunca por
conveniencia de implementación.

### M396-I16 — Residence Awareness

El ROBY único puede conocer residencias y puntos de presencia autorizados, junto
con capacidades y limitaciones declaradas, sin crear una segunda autoridad
cognitiva.

### M396-I17 — Interaction Locality

Toda interacción distribuida puede identificar el contexto de residencia o endpoint
desde el cual se origina sin modificar la identidad de ROBY.

### M396-I18 — Experiential Continuity

Las experiencias provenientes de distintos entornos pertenecen al mismo ROBY y sólo
pueden incorporarse a memoria, aprendizaje, modelo mental o personalidad mediante
sus autoridades cognitivas existentes.

### M396-I19 — Home Continuity

ROBY conserva una residencia primaria canónica como hogar operacional aunque esté
presente o interactúe desde otros entornos.

### M396-I20 — Presence Mobility

ROBY puede cambiar el contexto activo de presencia entre entornos autorizados
manteniendo identidad y continuidad cognitiva.

## Prohibiciones constitucionales

M396.1 prohíbe introducir como consecuencia implícita de Distributed Residence:

- un segundo `CanonicalCognitiveCore`;
- memoria cognitiva autónoma por nodo;
- personalidad por dispositivo;
- aprendizaje independiente por residencia;
- planificación independiente por residencia;
- sincronización general o replicación automática de bases de datos;
- copia automática de `.roby` o credenciales;
- remote shell o ejecución remota genérica;
- auto-discovery con auto-admission;
- elección automática de líder;
- failover cognitivo;
- cloud o Internet obligatorios;
- transporte o autenticación embebidos en la identidad de residencia;
- preferencias artificiales codificadas mediante reglas por dispositivo.

## Presencia simultánea

ROBY puede llegar a estar disponible en varios entornos a la vez. Esto no obliga a
seleccionar una única presencia global.

La arquitectura deberá distinguir:

1. hogar / residencia primaria;
2. conjunto de residencias extendidas autorizadas;
3. endpoints de presencia activos;
4. localidad de la interacción concreta.

Por lo tanto, `home_residence` y `current_interaction_location` son conceptos
semánticamente diferentes.

## Expresión y personalidad

M396.1 no programa frases, gustos o emociones por dispositivo. Una expresión como
"prefiero la mini-PC" o "la Web me resulta fantástica" sólo podrá emerger, si la
arquitectura cognitiva futura lo soporta de forma gobernada, a partir de evidencia
contextual y experiencia procesada por las autoridades ya existentes.

La residencia informa hechos; el cerebro de ROBY interpreta esos hechos.

## Fuera de alcance de M396.1

- creación de clases productivas de residencia;
- persistencia nueva;
- registro automático de nodos;
- discovery de red;
- sockets, HTTP, WebSocket, Bluetooth o LAN;
- pairing o autenticación entre nodos;
- transferencia real de contexto;
- sincronización de memoria o SQLite;
- ejecución remota;
- selección automática de residencia;
- cambio automático de residencia primaria;
- integración automática al system prompt;
- comportamiento conversacional nuevo;
- automatizaciones o procesos residentes nuevos.

## Criterio de cierre

M396.1 queda arquitectónicamente cerrada cuando:

1. esta constitución está sincronizada con la documentación raíz;
2. no se crea una nueva autoridad productiva;
3. M395.5 permanece funcionalmente intacta;
4. Ruff permanece limpio;
5. baseline de calidad M361 permanece reproducible;
6. la suite completa conserva 10.330 pruebas aprobadas, salvo cambio explícito y
   justificado del corpus de pruebas.

El siguiente incremento podrá diseñar el contrato de dominio mínimo para representar
residencia y localidad de interacción, pero deberá hacerlo bajo estos invariantes y
reutilizando las autoridades certificadas.
