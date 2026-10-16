# ROBY XI.2 — P7-C2-LOCAL-S2B-A — CONTRACTUAL RED

## Contract

**R-C2-LOCAL-S2B-A — EXPLICIT AUTHORIZED PREPARED PLACE/BUSINESS QUERY → EXISTING GOVERNED SOURCE EXECUTION → EXISTING M400 INFORMATION-SOURCE ENVELOPE.**

This RED freezes only the first S2B seam. It must consume an already-PREPARED S1 result, require explicit external-access authorization, execute only through the existing OfficialConversationGateway / canonical GovernedSourceQueryExecutor surface, construct the existing ExternalIntelligenceRequest with INFORMATION_SOURCE and matching target identity, preserve explicit network-use provenance, and enter M400 only through GovernedExternalInformationSourceIntegration.

## Required STOP

The seam stops at the M400 envelope. It must not construct M401 lineage/admission, publish conversational output, call P7-C2-S1, persist location, write Memory/Learning, enter Planning/Execution, reserve/book/navigate, enable global retrieval, or create a new executor/orchestrator/authority.

## Protected surfaces

`app/official_conversation_gateway.py` remains byte-identical with SHA-256 `05626c7376b1ebe36b82b6c7c4503b88f6a101e2ba585947493044c8238d36f8`.

S1 remains STOP-before-retrieval. RC1 remains closed. S2B-B is not opened by this RED.

## Expected RED

Existing-authority and protection tests pass. Tests requiring `app.governed_place_business_external_execution_composition.GovernedPlaceBusinessExternalExecutionComposition` fail because productive S2B-A composition is intentionally absent before GREEN.

No productive code is modified by this RED.
