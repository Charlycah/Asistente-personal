# Post-M409.1 — Partial Organization Snapshot + Exact Linkage Foundation v1

## Estado

Implementation candidate. Esta Foundation se mantiene aislada del runtime productivo hasta un Go/No-Go de wiring posterior.

## Alcance

El incremento añade tres piezas read-only y subordinadas:

- `ExplicitOrganizationReferenceAcquirer`: preserva referencias organizacionales estructuradas aportadas por caller/UI y las vincula a `option_id` mediante los bindings certificados del Adapter v1.
- `PartialCanonicalOrganizationSnapshotBuilder`: adquiere Goals, Projects y Reminders mediante ports read-only inyectados, reutiliza una única vez `ProductiveOrganizationEvidenceProjection` y genera una tuple canónica de `PersonalOrganizationItem` con lineage/fingerprint determinista.
- `OrganizationDecisionExactIdentityLinker`: verifica únicamente `organization_item_id` o `source_reference` exactos y deriva nuevas `GovernedDecisionOption` sin mutar las originales.

## Disponibilidad de fuentes v1

- Goals: `AVAILABLE`, `EMPTY` o `UNAVAILABLE` según el port inyectado.
- Projects: `AVAILABLE`, `EMPTY` o `UNAVAILABLE`.
- Reminders: `AVAILABLE`, `EMPTY` o `UNAVAILABLE`.
- Tasks: siempre `UNAVAILABLE` en v1. La productivización persistente de Task Intelligence permanece diferida a FASE IV.

`EMPTY` significa lectura válida con cero items. `UNAVAILABLE` significa que no existe una fuente productiva canónica utilizable en esa adquisición. Los dos estados forman parte del fingerprint y no son equivalentes.

## Identidad y linkage

V1 acepta sólo identidad explícita:

- `EXPLICIT_ITEM_ID`;
- `EXPLICIT_SOURCE_REFERENCE` con namespaces `goal:`, `project:`, `reminder:` y `task:`.

No existe title matching, matching case-insensitive, fuzzy/semantic matching, embeddings ni LLM. `task:` produce `SOURCE_UNAVAILABLE` mientras Tasks permanezca fuera del source set productivo.

Un mismo organization item no puede enriquecer automáticamente dos alternativas dentro del mismo option set: ambas quedan `AMBIGUOUS_REFERENCE`. El orden de alternativas nunca actúa como desempate.

## Invariantes

- una única projection mediante Foundation v1 existente;
- una lectura como máximo por port en cada `build()`;
- snapshot inmutable y transitorio;
- fingerprint SHA-256 derivado de disponibilidad + evidence proyectada;
- item IDs y `source_reference` únicos dentro del snapshot;
- options originales permanecen intactas;
- `option_id`, title, `explicit_preference`, scenario y causal linkage se preservan;
- Organization evidence no se convierte en preferencia humana;
- no persistence, no action, no runtime, no Gateway, no M391.5 y no M391.6;
- no nueva authority.

## Frontera final

```text
structured references
→ acquisition
→ partial canonical organization snapshot
→ exact identity linkage
→ linked options + bindings
→ STOP
```

El siguiente trabajo, después del closure audit, será un Go/No-Go separado para conectar esta Foundation a las fuentes productivas existentes y posteriormente a M391.5/M391.6.
