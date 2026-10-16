# Certificación RP.20.1

## Alcance certificado

- auditoría general de componentes no unificados;
- integración oficial de Gemini y Mistral;
- selección automática o explícita de proveedor;
- ejecución remota gobernada;
- trazabilidad de acceso de red;
- compatibilidad con Ollama/local y contratos históricos;
- documentación y plantilla de configuración.

## Pruebas nuevas

Se agregan seis pruebas para:

1. payload REST estructurado de Gemini;
2. registro ambiental Gemini + Mistral directo;
3. compatibilidad opcional de Mistral mediante OpenRouter;
4. ejecución remota sólo con autorización explícita;
5. propagación de trazabilidad de red;
6. modos de selección `auto/local/gemini/mistral`.

## Resultado

- Ruff: limpio.
- Pytest: 6537 pruebas aprobadas.
- Baseline anterior: 6531.
- Incremento: 6 pruebas.
