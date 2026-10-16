# RP.20.2 — Eliminación definitiva de código legado

## Objetivo

Reducir la superficie ejecutable de ROBY XI.2 retirando componentes históricos sin consumidores productivos y corrigiendo nombres que ya no representaban su responsabilidad real.

## Eliminaciones físicas

- `app/bootstrap.py`: composición histórica CORE IA, fuera de los entrypoints oficiales.
- `LLMProviderLayer` y `LLMProviderSnapshot`: router preliminar duplicado por la ruta gobernada oficial.
- pruebas exclusivas de las superficies eliminadas.

## Consolidación nominal

`LocalProviderExecutionAdapter` fue renombrado físicamente a `GovernedProviderExecutionAdapter`, porque desde RP.20.1 ejecuta rutas locales y remotas bajo la misma política gobernada. No se conserva alias ni módulo con el nombre anterior.

## Inventarios

Los registros de ejecución y compatibilidad ya no enumeran `app.bootstrap:build_app`. Los inventarios certifican únicamente superficies existentes e importables.

## Invariantes

- `OfficialROBYRuntime` continúa como única autoridad operacional.
- No se introduce runtime, lifecycle, conversación, memoria, scheduler ni residente alternativo.
- Ollama, Gemini y Mistral continúan atravesando el mismo router y ejecutor gobernados.
- Los contratos neutrales `LLMRequest`, `LLMResponse` y `LLMProvider` se preservan.
