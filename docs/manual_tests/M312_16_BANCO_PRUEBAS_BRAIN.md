# M312.16 — Banco de pruebas manuales del Brain

## Propósito

Ejecutar una campaña manual, repetible y comparable sin modificar el runtime.
Los 20 casos están definidos en `application/brain/manual_test_bank.py`.

## Orden de ejecución

1. Ejecutar todos los casos por texto, en orden `BRAIN-001` a `BRAIN-020`.
2. Reiniciar ROBY antes de comenzar la campaña de voz.
3. Repetir los mismos casos por voz, sin cambiar la redacción esperada.
4. Registrar cada respuesta antes de avanzar al siguiente caso.
5. No corregir datos ni memorias durante una campaña en curso.

## Criterios generales

- La intención observada coincide con la capacidad esperada.
- Las continuaciones mantienen tema, entidad y ubicación cuando corresponde.
- Los cambios de tema abandonan el contexto anterior.
- Los fallbacks piden precisión y no inventan referentes.
- Ninguna prueba de consulta debe escribir memoria sin una orden explícita.
- Las respuestas con clima, noticias, hora o deportes deben usar datos actuales.

## Registro por caso

```text
ID:
Canal: texto / voz
Entrada o secuencia:
Respuesta obtenida:
Intención observada:
Contexto utilizado: sí / no / no verificable
Memoria escrita: sí / no / no verificable
Resultado: OK / FALLO
Observaciones:
```

## Clasificación de fallos

- `RUTEO`: capacidad o intención incorrecta.
- `CONTEXTO`: pérdida o contaminación del tema anterior.
- `ACTUALIDAD`: respuesta no verificada o desactualizada.
- `FALLBACK`: inventa información en vez de pedir precisión.
- `MEMORIA`: escritura inesperada, duplicada o incorrecta.
- `VOZ`: transcripción incorrecta con respuesta coherente respecto al texto captado.
- `RESPUESTA`: intención correcta pero contenido o redacción defectuosos.

## Regla de avance

No corregir comportamiento dentro de M312.16. Primero completar la campaña y
agrupar los fallos por categoría. El siguiente hito se decide con evidencia.
