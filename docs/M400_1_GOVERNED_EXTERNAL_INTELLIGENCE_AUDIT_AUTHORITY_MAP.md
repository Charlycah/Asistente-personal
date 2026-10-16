# M400.1 — Governed External Intelligence Audit & Authority Map

## Alcance

M400.1 es una auditoría de sólo lectura sobre la baseline oficial M399.8.
No introduce providers, routers, fuentes, llamadas de red ni capacidades
productivas nuevas. Su objetivo es determinar qué existe, qué ruta es oficial,
qué permanece por compatibilidad y dónde están las fronteras de autoridad antes
de modificar M400.

Regla constitucional de M400:

**capacidad/evidencia externa ≠ autoridad cognitiva**

También:

**local o remoto ≠ autoridad**

Un provider puede ser local (Ollama) o remoto (Gemini/Mistral); una fuente puede
ser institucional (NASA) o de otra clase. Ninguno se convierte por ello en el
cerebro, criterio ejecutivo o autoridad de ROBY.

## Mapa real encontrado

### 1. Contrato neutral de inferencia

`core/llm_provider.py` define `LLMProvider`, `LLMRequest` y `LLMResponse`.
El contrato abstrae inferencia y no contiene memoria, planificación, decisión
ejecutiva ni autoridad cognitiva.

### 2. Compatibilidad histórica

`core/provider_router.py` (`ProviderRouter`) y `core/llm_service.py`
(`LLMService`) permanecen como capas históricas de compatibilidad. La
documentación RP.20.1 ya establece que no son el punto de entrada certificado
de ROBY. M400.1 no las elimina ni las promueve a autoridad.

### 3. Ruta gobernada de providers

La composición oficial construye una única secuencia:

`RuntimeCompositionRoot`
→ `ProviderHealthEvaluator`
→ `LocalFirstProviderPolicy`
→ `GovernedProviderRouter`
→ `GovernedProviderExecutionAdapter`
→ `OperationalResponseAssembler`.

`GovernedProviderRouter` declara una ruta; el adapter de ejecución exige esa
ruta antes de invocar un `LLMProvider`. El router no ejecuta inferencia.

La configuración actual prioriza Ollama como provider local y Gemini/Mistral
como providers remotos. Esta preferencia es routing, no autoridad cognitiva.

### 4. Ollama

Ollama sigue siendo una capacidad local vigente en la política local-first y
en las preferencias del routing gobernado. M400.1 no encuentra fundamento para
eliminarlo. Debe conservarse hasta una eventual migración explícita y validada.

### 5. Política de conocimiento externo

`KnowledgeSourcePolicy` decide si una necesidad requiere conocimiento externo,
verificación o puede resolverse internamente/localmente. Declara necesidad y
fuentes preferidas; no ejecuta providers ni absorbe la decisión cognitiva.

### 6. Fuentes gobernadas y NASA

`GovernedInformationSources` clasifica fuentes y mantiene sus declaraciones
inactivas respecto de red/fetch automático.

NASA tiene además `NasaGovernedSourceAdapter`, un adapter ejecutable bajo
`OfficialConversationGateway`. Su snapshot declara `network_enabled=True` pero
`automatic_fetch_enabled=False`: la consulta es explícita/on-demand. El adapter
no se autohabilita como autoridad y sólo acepta queries de `source_id="nasa"`.

Por tanto deben distinguirse tres niveles:

1. fuente declarada/clasificada;
2. adapter capaz de consultar una fuente;
3. autoridad/ruta que habilita una consulta explícita.

La existencia del nivel 2 no implica autonomía del nivel 3.

## Fronteras de autoridad para M400

M400 no debe crear un segundo cerebro ni un `ExternalIntelligenceManager`
paralelo. Antes de cualquier integración productiva se preservan:

- ROBY decide la necesidad cognitiva;
- políticas gobernadas declaran necesidad/ruta;
- routers seleccionan capacidad, no propósito cognitivo;
- adapters ejecutan sólo solicitudes gobernadas;
- fuentes/providers devuelven evidencia o inferencia;
- ROBY conserva evaluación, integración y decisión final;
- M397/M398 conservan sus autoridades de conectividad/transporte;
- M399 conserva diagnóstico/revisión y no se convierte en executor externo.

## Discontinuidades y deuda detectadas

- Coexisten `ProviderRouter`/`LLMService` históricos con la ruta gobernada
  moderna. Están documentados como compatibilidad; no deben eliminarse sin una
  auditoría de dependencias específica.
- El nombre histórico `GovernedProviderExecutionAdapter` conserva modelos con
  nombres `LocalProviderExecution*` aunque ya admite ruta local y remota. Es
  deuda nominal, no evidencia de una segunda autoridad.
- El registro declarativo de fuentes y los adapters ejecutables pertenecen a
  generaciones distintas; M400 deberá aclarar su relación sin fusionar
  clasificación, selección y transporte en una sola clase.
- NASA es una fuente de información, no un LLM provider. M400 no debe mezclar
  ambos conceptos sólo porque ambos puedan usar red.

## Resultado M400.1

La baseline ya contiene infraestructura multiprovider y fuentes externas
gobernadas. El problema de M400 no es "agregar Internet al cerebro", sino
fortalecer una frontera única donde capacidades externas subordinadas puedan
ser seleccionadas, ejecutadas, trazadas y verificadas sin adquirir autoridad.

M400.1 no modifica código productivo. El siguiente incremento sólo debe
diseñarse después de aceptar este mapa como baseline arquitectónica.
