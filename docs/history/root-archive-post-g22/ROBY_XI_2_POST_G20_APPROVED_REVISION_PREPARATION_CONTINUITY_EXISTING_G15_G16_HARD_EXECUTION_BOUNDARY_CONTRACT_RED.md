# ROBY XI.2 — POST-G20 — APPROVED REVISION PREPARATION CONTINUITY — CONTRACT RED

## Estado

**CONTRACT RED — PRE-GREEN — NO PRODUCTIVE CHANGE**

Base certificada de partida:

- INTEL-G20 — SURGICAL GREEN — CERTIFIED / CLOSED
- 14.172 PASS
- Ruff clean
- 0 regresiones

Este contrato demuestra si existe realmente un seam productivo faltante después de G20. No asigna todavía el nombre permanente `INTEL-G21`.

## Scope exacto

```text
exact G20 ApprovedKnowledgeRevisionEvidence
+ explicit Memory owner
→ existing ProductiveGovernedLearningWiring
→ existing G15 GovernedKnowledgeRevisionApplicationProposalFoundation.propose(...)
→ existing G16 GovernedKnowledgeRevisionRequestFoundation.certify(...)
→ GovernedKnowledgeRevisionRequest
→ STOP
```

## Frontera congelada

```text
G14 APPROVAL
!= G15 APPLICATION PROPOSAL
!= G16 CERTIFIED REQUEST
!= G17 EXECUTION
!= DURABLE MEMORY MUTATION
```

La aprobación humana G14 permite preparar y certificar artefactos inertes G15/G16. Este contrato **no** autoriza la mutación durable.

## Autoridad productiva

Debe reutilizarse el `ProductiveGovernedLearningWiring` existente como único coordinador productivo. G15 y G16 siguen siendo foundations inertes y no adquieren autoridad de Memory.

Debe reutilizarse:

- existing G14 evidence;
- existing G15 foundation;
- existing G16 foundation;
- existing `GovernedKnowledgeRevisionRequest`;
- existing canonical Memory authority boundary.

## Seam requerido

El wiring debe exponer un seam equivalente a:

```python
prepare_approved_knowledge_revision(
    approved_revision,
    *,
    owner,
) -> GovernedKnowledgeRevisionRequest | None
```

El nombre queda provisional durante CONTRACT RED; el ownership y la semántica quedan congelados.

## Input exacto

Requiere:

1. exact `ApprovedKnowledgeRevisionEvidence` ya producida por G14;
2. owner explícito y no vacío.

`SESSION ID != MEMORY OWNER`.

No puede reconstruir G13 ni reevaluar G14.

## Delegación G15

Debe llamar la foundation G15 existente con la evidencia exacta y el owner explícito. Debe preservar approval id, revision proposal id, target memory id, current/replacement content, evidence ids y fingerprints.

## Delegación G16

El proposal G15 exacto debe pasar directamente a la foundation G16 existente. El resultado debe ser el `GovernedKnowledgeRevisionRequest` existente, preservando lineage completo.

## STOP obligatorio

El nuevo seam termina inmediatamente después de producir G16.

Quedan fuera de scope y prohibidos:

- `execute_certified_revision_request(...)`;
- `apply_governed_knowledge_revision(...)`;
- G17;
- ejecución G18;
- durable Memory writes;
- replacement persistence;
- supersession;
- archive;
- cualquier segunda autoridad o manager de revisión.

## CONTRACT RED esperado

La base G20 certificada debe fallar exclusivamente porque todavía no existe la continuidad productiva G14→G15→G16.

Pruebas focales:

1. seam de preparación ausente;
2. reutilización productiva G15/G16 ausente;
3. producción exacta de G16 desde evidencia G14 ausente;
4. STOP productivo demostrable sólo cuando exista el seam;
5. anti-duplication ya debe permanecer GREEN.

Resultado RED esperado inicial:

**4 FAIL intencionales + 1 PASS anti-duplication**.

## No scope expansion

No modificar producción durante CONTRACT RED.

No modificar G14, G15, G16, G17, G18, G19 ni G20.

No reanclar snapshots en esta fase salvo que un cambio futuro legítimo de producción lo haga necesario y exista justificación documental explícita.

## Decisión posterior

Si este contrato produce el RED exacto esperado, queda probado que el seam es real. Recién entonces puede decidirse formalmente si se registra como **INTEL-G21 — continuity gate**, nunca como nueva autoridad cognitiva.
