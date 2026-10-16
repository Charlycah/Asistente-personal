# RP.18.5 — Ruta de capacidades única

`OfficialCapabilityGateway` es la frontera canónica de ejecución de toda
capacidad registrada en `OfficialRuntimeCapabilityRegistry`.

El registro conserva descubrimiento, descriptores y orden. El gateway concentra
la invocación efectiva y registra capacidad, origen y resultado. Los
coordinadores internos solicitan ejecución al registro y no acceden directamente
al interceptor.
