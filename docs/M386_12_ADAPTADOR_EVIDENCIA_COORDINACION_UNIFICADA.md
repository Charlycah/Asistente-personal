# M386.12 — Adaptador de evidencia de coordinación unificada

## Propósito

M386.12 demuestra el segundo nodo real del grafo objetivo:
`unified_coordination`. La evidencia aparece únicamente cuando un turno pasa por
`UnifiedBrain` y éste delega a `OfficialConversationGateway`.

Una llamada directa al gateway continúa demostrando sólo `conversation_ingress`.

## Evidencia

Durante la delegación, el adaptador produce:

- nodo: `unified_coordination`;
- estado: `participated`;
- evidencia: `unified_brain:delegated`.

La evidencia no significa que `UnifiedBrain` razonó, decidió o utilizó memoria.
Significa exclusivamente que ejerció su función de coordinador transparente.

## Ventana contextual

El contrato M386.9 se sella dentro del gateway. Agregar evidencia después de la
respuesta violaría la regla de no reescritura de M386.10.

Por eso `UnifiedBrain` abre una ventana contextual sólo mientras llama al
gateway. La frontera consulta esa señal después de crear el ciclo y antes de
delegar al runtime. La ventana se cierra siempre, tanto en éxito como ante una
excepción.

La señal es local al contexto de ejecución y admite anidamiento. No modifica la
firma pública de `submit()` y conserva compatibilidad con gateways históricos.

## Cobertura resultante

Un turno llamado mediante `UnifiedBrain` registra:

1. `conversation_ingress`: `gateway:accepted`;
2. `unified_coordination`: `unified_brain:delegated`;
3. otros dieciséis nodos: `not_recorded`.

El resultado sigue siendo `partial`.

## Fallo posterior

Si el runtime falla después de la delegación, ambos hechos permanecen válidos:
el coordinador delegó y la entrada aceptó. No se inventa participación de los
componentes posteriores y la excepción original continúa propagándose.

## Privacidad y autoridad

La señal no contiene mensaje, respuesta, sesión, interlocutor ni excepción. El
adaptador no puede:

- alterar la conversación;
- consultar memoria;
- razonar, planificar o decidir;
- ejecutar acciones;
- persistir información;
- ampliar la autonomía;
- declarar participación de otro nodo.

M386.12 observa coordinación real sin convertir `UnifiedBrain` en autoridad de
dominio.
