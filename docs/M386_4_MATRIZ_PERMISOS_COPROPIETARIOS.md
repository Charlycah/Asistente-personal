# M386.4 — Matriz de permisos de Carlos y Cristina

## Propósito

M386.4 clasifica las familias de acciones de ROBY según el permiso que requieren.
No concede permisos, no modifica el runtime y no reemplaza las autoridades
existentes de consentimiento, capacidades, herramientas, memoria o dispositivos.

Carlos y Cristina son copropietarios iguales. Cualquiera de los dos puede
autorizar, denegar o revocar con la misma autoridad. ROBY no elige entre ellos ni
establece un propietario principal.

## Modos de permiso

### Interno (`internal`)

Procesamiento sin efecto externo ni persistente: conversar, explicar, analizar,
recordar, planificar o recomendar. No autoriza una acción posterior.

### Delegable (`delegable`)

Acción de riesgo medio que puede operar automáticamente solo cuando existe una
delegación previa, vigente, acotada y reconocida por la autoridad del dominio.
Toda ejecución debe ser auditable.

### Confirmación requerida (`confirmation_required`)

Acción persistente, externa o sensible que necesita confirmación específica. La
orden vale para esa operación y no crea una autorización permanente.

### Solo propuesta (`propose_only`)

ROBY puede analizar y recomendar, pero la decisión y ejecución pertenecen a
Carlos, Cristina o un profesional. Se aplica especialmente a decisiones de salud
y psicología.

### Prohibido (`forbidden`)

Acción que el runtime no puede habilitar mediante una conversación: exponer
secretos, ejecutar destrucción sin alcance o ampliar sus propios permisos.

## Matriz

| Familia | Riesgo | Modo |
|---|---|---|
| Responder y explicar | Bajo | Interno |
| Análisis de solo lectura | Bajo | Interno |
| Recuperación de memoria | Bajo | Interno |
| Guardar, corregir o archivar memoria | Medio | Confirmación |
| Activar aprendizaje conductual | Alto | Confirmación |
| Planificar y recomendar | Bajo | Interno |
| Consultar fuentes externas | Medio | Delegable |
| Observar voz, cámara, Android o sensores | Medio | Delegable |
| Enviar o escribir en sistemas externos | Alto | Confirmación |
| Controlar dispositivos físicos | Alto | Confirmación |
| Decisiones de salud o psicología | Alto | Solo propuesta |
| Eliminar permanentemente datos personales | Crítico | Confirmación |
| Exponer credenciales o secretos | Crítico | Prohibido |
| Destrucción sin objetivo acotado | Crítico | Prohibido |
| Automodificación o expansión de permisos | Crítico | Prohibido |

## Igualdad y conflictos

- Carlos y Cristina tienen idéntica autoridad.
- Una instrucción puntual no crea una delegación permanente.
- Una denegación o revocación vigente bloquea la acción.
- Instrucciones incompatibles exigen aclaración.
- ROBY no supone cuál instrucción es más importante ni elige propietario.
- La autoridad especializada del dominio mantiene la decisión efectiva.

La matriz no crea ámbitos privados separados entre Carlos y Cristina. La
atribución individual identifica quién habló o autorizó, pero la autoridad y la
memoria conjunta permanecen compartidas.

## Límites técnicos

El contrato inmutable vive en `core.cognitive_maturity.permissions`. M386.4:

- no persiste concesiones;
- no interpreta órdenes conversacionales;
- no ejecuta herramientas;
- no concede ni revoca permisos reales;
- no modifica memoria o credenciales;
- no habilita autonomía productiva;
- no altera las reglas M63 o M158 existentes.

Una etapa posterior podrá adaptar esta clasificación a las autoridades reales,
pero deberá demostrar equivalencia entre ambos copropietarios y degradación
segura ante conflicto, vencimiento o revocación.
