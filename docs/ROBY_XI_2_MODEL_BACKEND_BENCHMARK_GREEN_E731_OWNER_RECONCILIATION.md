# MODEL/BACKEND BENCHMARK SURGICAL GREEN — OWNER E731 RECONCILIATION

Owner evidence: full suite 13,642 PASS / 0 FAIL, Ruff E731 at the new
model/backend benchmark contract module, `reference_parity` ranking helper.

Surgical delta: replace assignment of `lambda` to `rank` with a local
`def rank(values)` retaining exactly the existing sorted key
`(-values[index], index)` and tie-breaking behavior. No other functional
or architectural change is authorized by this reconciliation.

The model/backend benchmark contract remains model-free, runtime-free,
offline, non-authoritative and evaluation-only. No model acquisition,
ONNX export, runtime installation, private corpus or productive admission.

Status: LOCAL RECONCILIATION COMPLETE; OWNER RECERTIFICATION PENDING.
Owner must rerun cache cleaning, M361 regeneration, Ruff and full pytest.
