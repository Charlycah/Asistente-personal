# M400.5 — Governed External Intelligence Provenance & Verification

## Propósito

M400.5 agrega verificación común para los envelopes externos producidos por
M400.3 y M400.4. Verifica linaje, identidad, procedencia y estado de admisión;
no ejecuta providers ni fuentes y no decide si el contenido es verdadero.

**procedencia verificable ≠ verdad certificada**

También permanecen:

**predicción ≠ certeza**

**capacidad/evidencia externa ≠ autoridad cognitiva**

## Verificación

`GovernedExternalIntelligenceVerifier` comprueba:

- identidad consistente del envelope;
- coincidencia de capability entre request y provenance;
- coincidencia del actor con provider/source;
- timestamp timezone-aware;
- trace IDs únicos;
- ausencia de autoridad cognitiva externa;
- linaje de provider cuando M400.3 aporta `route_id` y `execution_id`.

La verificación produce un digest SHA-256 de procedencia y un
`verification_id` determinista.

## Estados

`verified` significa que la procedencia disponible satisface los contratos.

`limited` significa que el envelope es admisible pero falta trazabilidad
relevante. Actualmente las fuentes M400.4 no aportan todavía un execution trace
propio, por lo que esa limitación queda explícita en vez de inventarse.

`rejected` conserva un resultado que ya fue rechazado en la frontera. Verificar
su procedencia no transforma un fallo externo en evidencia aceptada.

## Límite epistemológico

M400.5 nunca marca `truth_certified=True`. Un provider puede producir una
respuesta perfectamente trazable y equivocada; una fuente puede ser auténtica
pero devolver información incompleta o desactualizada.

La verificación de procedencia es condición de confianza técnica, no prueba de
verdad semántica.

## Autoridad

El verifier expone `verifier_id`, no `authority_id`. No routea, selecciona,
consulta, ejecuta, recuerda, planifica ni modifica ROBY.
