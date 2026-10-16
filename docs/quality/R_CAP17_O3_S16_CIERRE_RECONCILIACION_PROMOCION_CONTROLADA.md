# ROBY XI.2 — R-CAP17-O3-S16 — Closing reconciliation and controlled baseline promotion

**Classification:** documentary-only candidate; no production/test change; no baseline promotion yet.
**Input:** full S14 ZIP corrected for Ruff E501. **Owner evidence:** Windows focal Ruff PASS; 7 S13 + 20 S11/original + 49 EPUB/selection/handoff PASS (76 focal tests); S15 real-library diagnostic PASS.

## Reconciliation
- S10 contractual RED → S11 direct nested lookup GREEN, Windows 8+12 PASS.
- S12 pre-RED reconciliation → S13 conversational RED, Windows 5 intentional FAIL + 2 PASS.
- S14 canonical conversational GREEN, Windows Ruff PASS and 76 focal PASS.
- S15 read-only real EPUB validation: status completed; 0 catalogue scans; path/provenance OK; 60,045 chars; 1 Unified Runtime evaluation; 0.77 ms direct lookup; 133.79 ms instrumented conversation; PASS.
- No new catalogue/selector/retriever/agent/index/cache, no library write, no changes to protected UI adapter.

## Documentary authorities
- Root `ROBY_XI_2_CURRENT_TRUTH.md`: operative bounded status and explicit non-promotion gate.
- Root `ROBY_XI_2_MASTER_CAPABILITY_REGISTRY.md`: CAP-17 owner map, contracts, residual.
- Root `ROBY_XI_2_COGNITIVE_INVENTORY_RECONCILIATION_MASTER_GUIDE.md`: reuse proof and open residual.
- This document is a gate record, not an alternative master authority. Historical counts remain untouched.

## Baseline promotion conditions — STOP
1. Run `ruff check .` on Windows from the S16 candidate tree.
2. Run `python scripts/generate_quality_baseline.py` and its prescribed verification (inspect generated changes before retaining).
3. Run `pytest -q` and reconcile M377 S1–S4's 47 intentional RED versus unexpected failures. Do not call the entire suite GREEN while intentional RED remain.
4. Compare full results against the last Owner-certified O2 gate and audit changed files; do not replace O2 or overwrite it until these checks are reviewed.
5. Preserve E1-B frozen, MODEL_ACQUISITION UNMAPPED/DENY/NO-GO, and `app/runtime_ui_adapter.py` protected.

**Verdict:** O3 objective bounded closure CERTIFIED FOCAL + REAL DIAGNOSTIC; S16 documentary integration materialized; GLOBAL BASELINE PROMOTION PENDING OWNER GATE; STOP.


## Reconciliación posterior a pytest integral Windows — gate no promovido

Owner reportó 13.715 PASS y 53 FAILED. De los 53, 47 son M377 RED intencionales bajo HOLD; cinco son incumplimientos de límite de 400 líneas de Current Truth provocados por el apéndice S16 (406 líneas); y uno es guardrail de SHA-256 de Master Capability Registry. Esta variante restaura Current Truth byte-identical a S14 (397 líneas) y conserva la evidencia O3 en este documento de calidad. El fallo de SHA-256 NO fue introducido por S16: el archivo de registry es byte-identical entre S13, S14 y S16; el test fija un hash diferente al presente en esas bases. No se altera el registry ni se modifica el test. La discrepancia requiere reconciliación contractual independiente antes de promoción. Ruff integral y M361 no quedan certificados por la salida recibida. STOP.

## S16-CLOSE — Owner Windows integral gate and bounded promotion (2026-10-12)

**Evidence:** Windows `pytest -q` final summary: **13,724 passed / 47 failed / 323.80 s**. The 47 failures are the known **M377 S1–S4 intentional RED/HOLD**; the exact failure identifiers were checked against the provided owner log: **47/47 in nine `test_m377_*` architecture files, 0 unexpected failures**. This is an exception-qualified gate, **not** a global zero-failure GREEN certification.

**Prior local gate:** G2 GREEN focal: **16 passed / 0 failed / 1.70 s**, across G2 evolvable guardrail, historical R-DOC-S1 and R-DOC-ROOT-1. Ruff: `All checks passed!`. `scripts/generate_quality_baseline.py` generated `docs/quality/M361_QUALITY_BASELINE.json`; the generated artifact is not separately attested as unchanged. Windows focal RED before GREEN: 2 passed / 1 intentional failure, Ruff PASS.

**Failure identity distribution (M377 only):**
- `tests/architecture/test_m377_causal_productive_visual_concurrency_s4_contract_red.py`: 6
- `tests/architecture/test_m377_per_call_transport_compatibility_reentrancy_contract_red.py`: 3
- `tests/architecture/test_m377_proposal_review_concurrency_s3_contract_red.py`: 8
- `tests/architecture/test_m377_same_turn_expression_behavioral_contract_red.py`: 5
- `tests/architecture/test_m377_same_turn_expression_characterization_contract_red.py`: 2
- `tests/architecture/test_m377_turn_bound_carrier_identity_compatibility_contract_red.py`: 2
- `tests/architecture/test_m377_wrapper_chain_behavioral_preservation_contract_red.py`: 2
- `tests/architecture/test_m377_wrapper_chain_per_call_behavior_hash_precedence_contract_red.py`: 11
- `tests/architecture/test_m377_wrapper_chain_terminal_interceptors_s2_contract_red.py`: 8

**Disposition:** S16 / CAP-17 O3 bounded objective **CLOSED / OWNER-CERTIFIED / CONTROLLED BASELINE PROMOTED WITH M377 EXCEPTION**. Preserve prior O2 certified baseline and its historical certification; this O3/S16 snapshot is a separate successor checkpoint, not a retroactive rewrite of O2. M377 remains **RED/HOLD** and is not waived or implemented by this closure. E1-B frozen, MODEL_ACQUISITION UNMAPPED/DENY/NO-GO, protected `app/runtime_ui_adapter.py` unchanged. No new capability, owner, manager, agent, loop, scan, persistence, or general title-discovery authorization. STOP before any further productive RED or M377 GREEN without its own governed authorization.

**Evidence limitation:** The provided integral log records the pytest final summary and failure identities; it does not independently reproduce a new Ruff or M361 run from that same command invocation. Ruff PASS is evidenced by the preceding G2 Windows focal certification. This documentary packaging is pending a final Windows ZIP verification; do not infer new runtime test execution from archive construction.
