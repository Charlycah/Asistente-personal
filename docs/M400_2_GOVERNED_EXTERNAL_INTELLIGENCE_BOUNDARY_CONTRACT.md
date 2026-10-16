# M400.2 — Governed External Intelligence Boundary & Contract

## Propósito

M400.2 establece una frontera contractual única para admitir resultados de
capacidades externas sin convertirlas en cerebro, criterio ejecutivo ni
autoridad cognitiva de ROBY.

Regla constitucional:

**capacidad/evidencia externa ≠ autoridad cognitiva**

Y también:

**local o remoto ≠ autoridad**

La frontera no selecciona ni ejecuta providers, no consulta fuentes, no abre
red, no sustituye routing, policies, gateways ni M397/M398. Su única función es
normalizar una solicitud externa explícita y el resultado/procedencia que vuelve
a ROBY.

## Dos familias, un límite común

### Inference Provider

Incluye capacidades como Ollama, Gemini o Mistral. Un provider puede producir
texto/inferencia, informar modelo, aceptación o error, pero su salida ingresa
como evidencia subordinada. El provider no decide propósito, memoria,
planificación, verdad ni acción final.

### Information Source

Incluye fuentes como NASA y otras fuentes gobernadas. Una fuente devuelve items
de información con procedencia explícita. No se representa como LLM provider y
no adquiere autoridad por ser institucional u oficial.

M400.2 unifica la frontera de admisión, no los contratos internos de estas dos
familias.

## Contrato

`ExternalIntelligenceRequest` exige:

- `request_id`;
- owner explícito;
- tipo de capacidad;
- propósito explícito;
- target opcional;
- declaración de que el acceso externo fue solicitado.

`ExternalIntelligenceProvenance` conserva:

- actor/provider/source;
- tipo de capacidad;
- scope local o remoto;
- si se utilizó red;
- timestamp timezone-aware;
- trace ids explícitos.

`ExternalIntelligenceEnvelope` mantiene separadas
`ExternalInferenceEvidence` y `ExternalInformationEvidence`, genera identidad
reproducible y expone permanentemente:

`cognitive_authority_granted = False`.

## Relación con la arquitectura existente

M400.2 no reemplaza:

- `ProviderHealthEvaluator`;
- `LocalFirstProviderPolicy`;
- `GovernedProviderRouter`;
- `GovernedProviderExecutionAdapter`;
- `KnowledgeSourcePolicy`;
- `OfficialConversationGateway`;
- adapters de fuentes como NASA;
- M397/M398 para conectividad/transporte.

Esas capas siguen seleccionando, gobernando o ejecutando según sus contratos.
La nueva frontera sólo normaliza el ingreso del resultado externo a ROBY.

## Ollama

Ollama permanece como provider local válido. Que su transporte pueda utilizar
localhost/red local no lo convierte en provider remoto ni en autoridad. M400.2
registra por separado `execution_scope` y `network_used` para no confundir esas
dimensiones.

## Límites permanentes

- ningún provider o source adquiere `authority_id` cognitivo;
- la frontera usa `boundary_id`, no se declara cerebro ni engine ejecutivo;
- no contiene routing, selección, inference execution, HTTP ni registro de
  adapters/providers;
- una respuesta aceptada por un provider no equivale a verdad;
- una fuente oficial no equivale a verdad absoluta;
- ROBY conserva interpretación, contraste, memoria, planificación y decisión;
- M400.2 no añade automatización silenciosa ni modifica plataforma.

## Resultado

M400.2 crea el idioma contractual común que permitirá integrar capacidades
externas existentes bajo una sola frontera gobernada, manteniendo separadas
inferencia y recuperación de información y preservando todas las autoridades
preexistentes.
