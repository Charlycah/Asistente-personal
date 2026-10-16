# ADR-076 — Personal Knowledge Base

## Estado

Aceptado para M74.

## Contexto

M72 incorporó memoria doméstica operativa y M73 incorporó documentos gobernados. ROBY necesita distinguir entre conservar información cotidiana, almacenar fuentes documentales y mantener conocimiento conceptual reutilizable.

## Decisión

Se incorpora `PersonalKnowledgeBaseManager` como subsistema de dominio independiente. El conocimiento se representa mediante elementos inmutables con tipo, propietario, fuente, confianza, estado y referencia de procedencia. La incorporación se realiza mediante candidatos que pueden requerir revisión humana.

Las relaciones entre elementos se almacenan explícitamente y permiten expresar derivación, soporte, contradicción, expansión y reemplazo. El repositorio se define mediante un contrato `Protocol` para mantener aislada la infraestructura.

## Reglas

- Todo elemento conserva su fuente y nivel de confianza.
- El conocimiento generado por el sistema requiere revisión humana.
- El conocimiento de baja confianza no se activa automáticamente.
- Scope Guard continúa siendo la autoridad de alcance.
- Los documentos son fuentes; no se confunden con el conocimiento derivado.
- El reemplazo no elimina la historia: el elemento anterior queda `SUPERSEDED`.
- M74 no incorpora embeddings, inferencia autónoma permanente ni base vectorial.

## Consecuencias

ROBY puede organizar conocimiento personal y relacionarlo sin mezclarlo con Household Memory o Document Inbox. La persistencia real, la búsqueda semántica y los extractores inteligentes pueden añadirse posteriormente sin modificar el contrato central.
