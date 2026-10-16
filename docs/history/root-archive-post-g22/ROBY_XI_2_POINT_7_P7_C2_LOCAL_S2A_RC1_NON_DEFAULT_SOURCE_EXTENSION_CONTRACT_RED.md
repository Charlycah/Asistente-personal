# ROBY XI.2 — POINT 7 / P7-C2-LOCAL-S2A-RC1
# CORRECTED RED CONTRACTUAL — NON-DEFAULT GOVERNED SOURCE EXTENSION

## Status

**CORRECTED RED BUILT / NO PRODUCTIVE IMPLEMENTATION / OWNER CERTIFICATION PENDING / STOP**

This corrected RED supersedes only the two placement assumptions invalidated by the failed S2A GREEN. It preserves the remaining Owner-certified S2A provider/credential contract.

## Certified invariants preserved

- `app/official_conversation_gateway.py` must remain byte-identical at SHA-256 `05626c7376b1ebe36b82b6c7c4503b88f6a101e2ba585947493044c8238d36f8`.
- `DEFAULT_GOVERNED_INFORMATION_SOURCES` remains exactly six sources.
- A fresh bare `GovernedInformationSources()` remains exactly six sources and does not contain `foursquare_places`.
- The existing gateway public `register_governed_source_query_adapter(source_id, adapter)` surface is reused unchanged.
- The existing `GovernedSourceQueryExecutor` remains the single adapter execution/registration authority.
- The existing `GovernedSourceQueryContract` remains the canonical query validation contract.

## Corrected residual

**R-C2-LOCAL-S2A-RC1 — EXPLICIT NON-DEFAULT GOVERNED SOURCE DECLARATION ADMISSION THROUGH EXISTING SOURCE-QUERY EXECUTOR REGISTRATION.**

Required chain:

`M343.5 DEFAULT SIX UNCHANGED`
+
`CREDENTIAL-GATED PROVIDER ADAPTER`
+
`IMMUTABLE INACTIVE NON-DEFAULT SOURCE DECLARATION`
→ existing protected gateway registration surface
→ existing executor registration
→ **missing generic declaration validation + instance-local registry admission**
→ existing query contract recognizes the source
→ existing executor holds the adapter
→ explicit execution remains separate
→ STOP.

## Contractual RED expectations

The corrected test requires:

1. protected gateway byte identity;
2. six-source default registry preservation;
3. explicit executor registration of an adapter carrying an inactive non-default source declaration admits that declaration into the same runtime registry instance;
4. a fresh default registry remains unchanged after instance-local admission;
5. the existing query contract can prepare a query for the explicitly admitted source;
6. an unknown source without a declaration fails closed at registration;
7. declaration identity must match registration identity;
8. bounded Foursquare adapter exists under the existing adapter protocol;
9. credential is mandatory and blank credential fails closed;
10. secret is absent from snapshot representation;
11. environment wiring reuses `SecretsLoader` and `environment_flag`;
12. S1 cannot enable/register/execute or read secrets;
13. no implicit IP geolocation fallback;
14. injected transport supports deterministic no-live-network tests;
15. no parallel authority or execution-scope expansion.

## Removed invalid assumptions

The corrected RED intentionally removes these disproven requirements:

- Foursquare must be inserted into `DEFAULT_GOVERNED_INFORMATION_SOURCES`;
- `OfficialConversationGateway` must gain `enable_foursquare_governed_source(...)`.

Removing them restores compatibility with stronger pre-existing certified invariants; it does not weaken governance.

## Out of scope

No productive implementation, no gateway surgery, no default-registry expansion, no historical hash updates, no live Foursquare call, no real credential, no global retrieval enablement, no implicit location acquisition/persistence, no reservation/navigation, no Memory/Learning/Planning/Execution, no second registry/selector/query contract/executor.

## Local focal RED evidence

On the unchanged Owner-certified RED production baseline, the corrected focal suite yields:

**4 PASS / 12 expected RED FAIL.**

The passing assertions prove protected gateway identity, six-source default preservation, reuse of existing authorities, and S1 separation. The failures correspond to the missing generic extension seam and still-missing bounded provider/configuration implementation.

Full Owner certification remains mandatory.
