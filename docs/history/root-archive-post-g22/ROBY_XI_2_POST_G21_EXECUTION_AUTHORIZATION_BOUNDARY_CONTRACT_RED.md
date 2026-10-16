# ROBY XI.2 — POST-G21 — EXECUTION AUTHORIZATION BOUNDARY — CONTRACT RED

## Estado

**CONTRACT RED — NO PRODUCTIVE CHANGE — PRE-NUMERATION**

Base certificada de partida:

`ROBY_XI.2_INTEL-G21_CERTIFIED_PLUS_SAFE_CACHE_CLEANER.zip`

Baseline de partida:

**14.177 PASS · 0 FAIL · Ruff clean**

## Hipótesis RED

G21 termina correctamente en un `GovernedKnowledgeRevisionRequest` G16 inerte. G18/G17 ya contienen la ruta productiva hacia `OfficialMemoryGateway`, pero la entrada de ejecución todavía no exige una autorización humana separada, explícita y exact-linked de “aplicar ahora”.

El RED no cuestiona G17 ni reconstruye G13–G16. Sólo prueba la precondición ausente entre certificación y mutación durable.

## Contrato esperado

```text
exact G16 GovernedKnowledgeRevisionRequest
+ explicit human apply-now response
→ existing M369ExplicitHumanLearningApprovalEvidenceFoundation
→ AuthorizedKnowledgeRevisionExecutionEvidence | None
→ STOP
→ exact request + exact authorization evidence
→ existing ProductiveGovernedLearningWiring / G18
→ existing G17 / OfficialMemoryGateway
```

## Distinciones congeladas

- `G14 CONTENT APPROVAL != EXECUTION AUTHORIZATION`
- `CERTIFIED REQUEST != AUTHORIZED EXECUTION`
- `AUTHORIZED EXECUTION != SUCCESSFUL MEMORY MUTATION`
- `REQUEST PRESENT != PERMISSION TO APPLY`
- `SESSION CONTINUITY != EXECUTION PERMISSION`
- `G16 grants_authority=False` conserva su significado.

## Fallos intencionales esperados

1. Falta el tipo explícito de respuesta humana de autorización de ejecución y la evidencia inerte exact-linked.
2. Falta la operación de evaluación de ejecución en la autoridad humana existente.
3. `ProductiveGovernedLearningWiring.execute_certified_revision_request(...)` todavía no exige autorización exacta.
4. Un G16 certificado aislado todavía puede llegar al writer de Memory.
5. `OfficialConversationGateway.submit(...)` todavía no expone material explícito de autorización de ejecución.

## Pruebas que deben permanecer GREEN desde RED

- no aparece una segunda autoridad humana;
- no aparece otro productive wiring;
- no aparece otro Memory gateway;
- G18 sigue delegando al único método oficial de G17/Memory;
- no hay recertificación G16 en el seam de ejecución.

## Límites

Este CONTRACT RED no autoriza implementación productiva, no abre G22 y no modifica G17. Una numeración nueva sólo corresponde si los fallos intencionales se reproducen de forma focal y el resto de las garantías permanece verde.
