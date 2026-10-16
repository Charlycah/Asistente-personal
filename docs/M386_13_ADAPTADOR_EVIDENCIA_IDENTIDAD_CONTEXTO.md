# M386.13 — Adaptador de evidencia de identidad y contexto

## Propósito

M386.13 observa si el turno productivo resolvió cuatro condiciones del nodo
`identity_and_context` sin conservar los valores privados utilizados:

1. copropiedad conjunta canónica;
2. sesión delimitada;
3. historial contextual acotado;
4. interlocutor actual identificado.

## Hallazgo real

El runtime oficial construye una solicitud con propietario técnico, sesión e
historial reciente limitado. Sin embargo, actualmente no existe una resolución
canónica por turno que determine si habla Carlos o Cristina.

También subsisten configuraciones históricas cuyo owner es `Carlos`. Esas
configuraciones no demuestran por sí solas la copropiedad conjunta. Sólo el
valor canónico efectivo `Carlos y Cristina` satisface esa comprobación.

## Estado actual

Con owner conjunto, el registro productivo contiene:

- evidencia `identity_context:joint_coownership`;
- evidencia `identity_context:session_scoped`;
- evidencia `identity_context:bounded_history`;
- motivo `interlocutor:not_resolved`.

Por lo tanto, el nodo se declara `degraded`, no `participated`.

Si además el owner no es conjunto, se agrega
`coownership:not_canonical`. Si ninguna condición pudiera demostrarse, el nodo
quedaría `blocked`.

## Conexión

El gateway abre una ventana de observación sólo mientras el runtime procesa el
turno. El runtime emite cuatro valores booleanos después de construir la
solicitud validada y antes de entrar al pipeline.

No transmite owner, sesión, historial, mensaje ni interlocutor. El adaptador
convierte únicamente esos resultados booleanos en códigos técnicos M386.9.

La ventana se cierra tanto ante éxito como ante excepción. Fuera del gateway,
el adaptador no registra nada.

## Cobertura honesta

En el estado productivo actual:

- `conversation_ingress`: participado;
- `unified_coordination`: participado cuando interviene `UnifiedBrain`;
- `identity_and_context`: degradado;
- otros quince nodos: no registrados.

El resultado global del expediente es `degraded`, aunque la conversación pueda
responder normalmente. El expediente describe cobertura cognitiva, no sustituye
el resultado funcional del turno.

## Privacidad y autoridad

La evidencia no contiene nombres, identificadores de sesión, texto, historial
ni respuesta. El adaptador no resuelve identidades, no autentica personas y no
puede consultar memoria, decidir, ejecutar o ampliar autonomía.

M386.13 hace visible una brecha existente. No la corrige ni finge que ya está
resuelta.
