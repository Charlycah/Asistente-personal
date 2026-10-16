# RP.20.25 — Proyección trivial de colección retirada

## Objetivo

Reducir métodos públicos sin consumidores que sólo convertían una estructura interna ya visible a otra colección, sin política, transformación semántica ni compatibilidad necesaria.

## Retirado

- `CognitiveMemoryRecallResult.memories`

La propiedad sólo ejecutaba:

```python
return tuple(item.memory for item in self.items)
```

## Acceso canónico

Los consumidores consultan ahora los elementos completos del resultado:

```python
tuple(item.memory for item in result.items)
```

Esto conserva puntuación y señales coincidentes en `CognitiveMemoryRecallItem` como superficie primaria.

## Conservado

Se conservaron conversiones que añaden orden, normalización, filtrado, copia defensiva, compatibilidad de protocolo o presentación estable. También se conservaron `capability_names` y `member_names`, porque tienen consumidores funcionales en observabilidad, descripción de identidad y prompts.

## Validación

- `ruff check .` limpio
- 30 pruebas focales
- 6594 pruebas completas
