# M386.2 — Hecho, inferencia, hipótesis y desconocimiento

## Propósito

M386.2 establece cómo debe describirse el grado de conocimiento de ROBY sin
crear otra memoria, otro registro de afirmaciones ni otro motor de inferencia.

La clasificación reutiliza los contratos de razonamiento gobernado M77–M84:
evidencia, `Claim`, inferencia, conflictos, confianza y revisión.

## Niveles

### Hecho (`fact`)

Afirmación factual u observacional respaldada por evidencia y cuyo estado es
`supported` o `corroborated`.

Forma pública recomendada: `Según la evidencia disponible, ...`

Una afirmación que se llama a sí misma hecho, pero todavía está `proposed`, no
puede presentarse como hecho.

### Inferencia (`inference`)

Resultado derivado mediante una regla gobernada. Conserva referencia a la regla
y nunca se transforma automáticamente en hecho.

Forma pública recomendada: `A partir de la evidencia, infiero que ...`

### Hipótesis (`hypothesis`)

Posibilidad, supuesto o explicación pendiente de confirmación.

Forma pública recomendada: `Es posible que ...`

Una confianza de `1.0` no promociona una hipótesis. Confianza y categoría
epistemológica son dimensiones diferentes.

### Desconocimiento (`unknown`)

Ausencia de evidencia suficiente, conflicto, afirmación no respaldada o material
disputado, refutado, vencido, reemplazado o pendiente de revisión.

Forma pública recomendada:
`No tengo evidencia suficiente para afirmar que ...`

Desconocimiento no significa falsedad. Significa que ROBY no está autorizado a
presentar una conclusión como establecida.

## Precedencia conservadora

Los estados `disputed`, `refuted`, `stale`, `superseded` y `review_required`
prevalecen sobre el tipo original de una afirmación y producen `unknown`.

Después se aplica este orden:

1. hecho u observación respaldados → `fact`;
2. resultado de regla gobernada → `inference`;
3. supuesto o hipótesis → `hypothesis`;
4. ausencia, conflicto o base insuficiente → `unknown`.

## Límites

- No modifica `Claim`, evidencia, memoria, reglas ni confianza.
- No persiste contenido ni duplica textos de afirmaciones.
- No promueve afirmaciones.
- No ejecuta acciones.
- No autoriza decisiones sensibles.
- No convierte inferencias psicológicas en hechos personales.
- No utiliza emoción simulada como evidencia.
- No confunde falta de evidencia con evidencia de ausencia.

## Integración futura

M386.2 permanece aislado hasta que una etapa posterior conecte explícitamente la
clasificación con respuestas, análisis, memoria y diagnósticos. Esa integración
deberá conservar el identificador del `Claim`, su procedencia y la etiqueta
epistemológica sin exponer razonamiento interno privado.
