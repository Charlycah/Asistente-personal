# M388.5.5.a — Cierre Ruff y recertificación M361

## Alcance

Corrección exclusivamente formal de la suite M388.5.5 y sincronización del
snapshot estático M361 con los nuevos archivos de certificación.

## Cambios

- Se dividieron líneas superiores a 88 caracteres.
- Se normalizaron los imports de la matriz de evidencia.
- Se regeneró `docs/quality/M361_QUALITY_BASELINE.json` mediante
  `scripts/generate_quality_baseline.py`.

## Justificación del baseline

La variación no afecta producción. Corresponde a la incorporación legítima de
siete módulos de prueba M388.5.5:

- módulos de test: 766 → 773;
- funciones de test: 10351 → 10385;
- clases de test: 538 → 542;
- líneas no vacías de tests: 98220 → 98493.

También se recalcularon automáticamente las relaciones estadísticas y la lista
de raíces más importadas.

## Validaciones realizadas

- Suite M388.5.5: 29 aprobadas.
- Tests de arquitectura: 595 aprobados.
- Línea base M361: 5 aprobados.
- Compilación Python de los siete archivos nuevos: aprobada.
- Verificación manual de longitud: ninguna línea superior a 88 caracteres.

La validación final de Ruff y de la suite completa corresponde a Carlos en el
entorno local oficial.

## Garantías

- No se modificó código de producción.
- No se modificó ni incluyó `.roby/credentials.json`.
- No se usó Git.
- No se concedieron nuevas autoridades, autonomía ni acciones externas.
- `CanonicalCognitiveCore(` permanece en la línea 52 de
  `app/official_conversation_gateway.py`.
