# ADR-074: Household Memory como memoria doméstica estructurada

## Estado

Aceptado para M72.

## Contexto

ROBY necesita recordar información cotidiana de Carlos, su señora y el hogar sin
mezclarla con memoria conversacional, identidad, bancos, pagos o compras.

## Decisión

Se incorpora `core.household_memory` con entradas inmutables, categorías,
propietario lógico, vencimientos, estados y un repositorio definido por
protocolo. Toda escritura pasa por `ScopeGuardManager` y rechaza dominios fuera
de alcance o sujetos a revisión humana.

## Consecuencias

- La memoria doméstica queda separada de la memoria cognitiva general.
- Carlos, su señora y el hogar compartido poseen ámbitos explícitos.
- La implementación inicial es determinista y usa un repositorio en memoria.
- La persistencia SQLite podrá añadirse detrás del mismo contrato.
- M72 organiza información; no ejecuta acciones externas ni sensibles.
