# M361 — Quality Baseline

## 1. Propósito

M361 establece una línea base objetiva, reproducible y no funcional para medir la evolución de ROBY XI.2 a partir de la base canónica M360.0.e, validada con Ruff limpio y 8677 pruebas aprobadas.

No introduce comportamiento productivo, no modifica APIs y no refactoriza módulos. Su función es fijar métricas, criticidad, deuda técnica y puertas de calidad antes de comenzar M362.

## 2. Artefactos canónicos

- `scripts/generate_quality_baseline.py`: generador determinista basado únicamente en la biblioteca estándar.
- `docs/quality/M361_QUALITY_BASELINE.json`: snapshot reproducible de métricas estáticas.
- `docs/M361_QUALITY_BASELINE.md`: interpretación, criticidad y reglas de uso.
- `tests/test_m361_quality_baseline.py`: contratos de existencia, reproducibilidad y gobierno.

El JSON es la fuente cuantitativa. Este documento es la interpretación arquitectónica y operativa.

## 3. Alcance de medición

La medición productiva incluye `app`, `application`, `core`, `domain`, `engines`, `handlers`, `infrastructure`, `interfaces` y las familias `m3` a `m7`.

La medición de pruebas incluye `tests/`. Se excluyen entornos virtuales, cachés, archivos compilados y metadatos de control de versiones.

Las líneas contabilizadas son líneas no vacías. Las funciones, clases, imports y manejadores de excepciones se obtienen mediante AST. Estas cifras no equivalen a cobertura de ejecución ni a complejidad ciclomática.

## 4. Snapshot M361

| Métrica | Valor |
|---|---:|
| Módulos productivos Python | 911 |
| Líneas productivas no vacías | 138969 |
| Funciones productivas | 7161 |
| Clases productivas | 3006 |
| Módulos de pruebas Python | 650 |
| Líneas de pruebas no vacías | 86633 |
| Relación líneas de pruebas / producción | 0.6234 |
| Relación módulos de pruebas / producción | 0.7135 |
| `except Exception` productivos | 124 |
| `except:` desnudos productivos | 0 |
| Errores de sintaxis detectados | 0 |

Los valores exactos y los rankings completos se conservan en el snapshot JSON.

## 5. Concentración de complejidad

Los principales puntos de revisión por longitud de función son:

1. `app/desktop_ui.py::run`
2. `app/runtime_root_factory.py::build_runtime_root`
3. `core/runtime_composition_root/root.py::compose`
4. `core/cognitive_pipeline.py::process_turn`
5. `core/cognitive_planning/diagnostics.py::run`

La longitud no prueba por sí sola un defecto. Estos puntos quedan marcados para caracterización y extracción incremental, nunca para reescritura masiva.

## 6. Matriz de criticidad

### Crítica

- runtime oficial y composition roots;
- gateway conversacional;
- Tool Gateway y ejecución gobernada;
- memoria cognitiva y continuidad;
- planificación y pipeline cognitivo;
- permisos, consentimiento y trazabilidad.

### Alta

- Vision Core y futuras fuentes visuales;
- audio, voz y diagnósticos;
- Gmail y Calendar;
- acciones documentales;
- configuración, credenciales y almacenamiento canónico.

### Media

- Desktop y futura integración Windows;
- clima, noticias y mapas;
- diagnósticos no críticos;
- capacidades de dispositivos aún no operativas.

### Baja

- utilidades internas sin efectos externos;
- herramientas documentales auxiliares;
- material histórico y ejemplos no ejecutables.

La criticidad determina el nivel de pruebas y revisión, no la importancia funcional percibida por el usuario.

## 7. Mapa inicial de deuda técnica

### P0 — Control inmediato

- Preservar cero manejadores `except:` desnudos.
- Evitar nuevas autoridades paralelas de runtime, planificación o ejecución.
- Mantener toda acción externa detrás de `ToolGatewayManager`.
- Conservar la suite completa y Ruff como puertas obligatorias.

### P1 — Caracterización antes de refactorizar

- Funciones superiores a 100 líneas.
- Clases superiores a 300 líneas.
- Módulos superiores a 500 líneas no vacías.
- Capturas amplias de `Exception` en rutas críticas.
- Composition roots con múltiples responsabilidades.

### P2 — Consolidación progresiva

- Adaptadores históricos y fachadas compatibles.
- Duplicación documental o de diagnósticos.
- Dependencias opcionales con activación poco visible.
- Ausencia de métricas formales de cobertura y complejidad ciclomática.

## 8. Quality gates desde M361

Toda entrega posterior deberá cumplir:

1. `ruff check .` sin errores.
2. Suite completa de pytest en verde.
3. Snapshot M361 regenerable sin diferencias inesperadas.
4. Cero nuevos `except:` desnudos.
5. Nuevas capturas amplias justificadas o caracterizadas.
6. Sin nuevas autoridades cognitivas o de ejecución paralelas.
7. pruebas unitarias, negativas, de composición y degradación cuando corresponda.
8. Documentación raíz y changelogs alineados con la base vigente.
9. Permisos, consentimiento, trazabilidad y desactivación para capacidades externas.
10. Cambios pequeños, compatibles y reversibles.

M361 no fija todavía un porcentaje mínimo de cobertura. Primero establece una medición reproducible; una futura puerta de cobertura deberá adoptarse con evidencia y sin bloquear módulos opcionales por razones artificiales.

## 9. Política de comparación

El snapshot M361 es una línea base, no una meta de maximización. Una métrica puede aumentar legítimamente si una nueva capacidad exige código y pruebas. La revisión debe explicar variaciones relevantes, especialmente:

- crecimiento de módulos críticos;
- nuevas funciones o clases por encima de los umbrales;
- aumento de excepciones amplias;
- caída material de la relación entre pruebas y producción;
- aparición de errores de sintaxis o archivos vacíos residuales.

No se aceptarán refactorizaciones cuya única justificación sea mejorar una cifra sin mejorar comprensión, seguridad o mantenibilidad.

## 10. Cierre

M361 deja una referencia cuantitativa y de gobierno antes de M362 — Governed Vision Gateway. La base permanece funcionalmente equivalente a M360.0.e y conserva como referencia validada 8677 pruebas aprobadas.
