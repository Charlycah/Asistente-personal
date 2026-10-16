# M395.3 — Alineación Cognitiva

## Propósito

Alinear el contrato cognitivo canónico con las rutas reales del runtime sin crear nuevas autoridades, planners, coordinators, gateways ni capacidades.

## Cambios

### 1. Autoridad residente de reflexión

`CognitiveCoreRuntime` continúa siendo `cognitive_core_resident` y ahora expone `reflect(...)` delegando exclusivamente al `reflection_engine` que ya posee el residente.

No agenda trabajo, no inicia background adicional y no crea una segunda autoridad.

### 2. CanonicalCognitiveCore

El snapshot declara explícitamente para cada dominio:

- `observational=True`
- `execution_authority=False`

Un facade puede estar enlazado y seguir sin convertir al core canónico en executor.

### 3. Planning / Decision / Reflection

Se certifica que los primarios de las fachadas coinciden con `CognitiveAuthorityMap`:

- planning → `executive_planning`
- decision → `unified_cognitive_coordination`
- reflection → `cognitive_core_resident`

### 4. Cognitive maturity

Se añadió `core.cognitive_maturity.contracts` con vistas estructurales neutrales para:

- Executive report/finding.
- Periodic reflection.

Esto elimina dependencias concretas de tipos que mantenían un SCC de 12 módulos. El grafo de imports internos de `core.cognitive_maturity` queda acíclico sin mover lógica ni fusionar autoridades.

### 5. Compatibilidad M395.2

`OFFICIAL_RUNTIME_FACTORY` se conserva como reexport explícito en `runtime_root_factory`, de modo compatible con Ruff y con las invariantes M395.2.

## Invariantes

1. `CanonicalCognitiveCore` observa; no ejecuta.
2. `CognitiveCoreRuntime` sigue siendo la única autoridad residente declarada para reflexión.
3. Reflection runtime contributors permanecen subordinados y no adquieren autoridad primaria.
4. Planning y Decision conservan sus autoridades canónicas.
5. `core.cognitive_maturity` no puede reintroducir ciclos de imports internos.
6. No hay nueva capacidad funcional en M395.3.
