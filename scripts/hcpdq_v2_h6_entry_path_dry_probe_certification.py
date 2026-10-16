from __future__ import annotations

import json
from hashlib import sha256

from app.official_conversation_gateway import OfficialConversationGateway
from core.explicit_complex_decision_intake_envelope import (
    ExplicitComplexDecisionIntakeEnvelopeFoundationV1,
)
from scripts.hcpdq_v2_h6_entry_path_equivalent_freeze_contract import (
    freeze_h6_independent_construction_contract,
)

DRY_PROBES = (
    (
        "DP-H6-01",
        "Decisión:\n¿Atlas o Boreal?\n"
        "Criterios:\nLos criterios son seguridad, reversibilidad y costo.\n"
        "Evidencia:\nAtlas cumple seguridad. Atlas cumple reversibilidad. "
        "Boreal cumple costo. Boreal no cumple seguridad.",
    ),
    (
        "DP-H6-02",
        "Decisión:\n¿Ruta Norte o Ruta Sur?\n"
        "Criterios:\nLos criterios son confiabilidad, recuperación y "
        "complejidad. Confiabilidad es obligatoria.\n"
        "Evidencia:\nRuta Norte cumple confiabilidad. Ruta Norte cumple "
        "recuperación. Ruta Sur cumple complejidad. Ruta Sur no cumple "
        "confiabilidad.",
    ),
    (
        "DP-H6-03",
        "Decisión:\n¿Lumen o Delta?\n"
        "Criterios:\nLos criterios son impacto, incertidumbre y recursos. "
        "Impacto es más importante que recursos.\n"
        "Evidencia:\nLumen cumple impacto. Lumen cumple recursos. "
        "Delta cumple incertidumbre. Delta no cumple impacto.",
    ),
)


class _FailClosedRuntime:
    bootstrap = object()
    history: tuple[object, ...] = ()
    traces: tuple[object, ...] = ()

    def converse(self, text: str, **kwargs: object):
        del text, kwargs
        raise AssertionError("dry probe reached runtime fallback")


def certify_h6_entry_path_dry_probes() -> dict[str, object]:
    contract = freeze_h6_independent_construction_contract()
    parser = ExplicitComplexDecisionIntakeEnvelopeFoundationV1()
    records: list[dict[str, object]] = []

    for probe_id, prompt in DRY_PROBES:
        intake = parser.analyze(prompt)
        gateway = OfficialConversationGateway(_FailClosedRuntime())
        fallback_reached = False
        response_text = ""
        try:
            turn = gateway.converse(prompt)
            response_text = turn.response_text
        except AssertionError:
            fallback_reached = True

        records.append(
            {
                "probe_id": probe_id,
                "held_out": False,
                "prompt_fingerprint": sha256(
                    prompt.encode("utf-8")
                ).hexdigest(),
                "intake_status": intake.status.value,
                "deliberation_status": (
                    intake.deliberation_evidence.status.value
                    if intake.deliberation_evidence is not None
                    else None
                ),
                "criteria_status": (
                    intake.criteria_evidence.status.value
                    if intake.criteria_evidence is not None
                    else None
                ),
                "option_criterion_status": (
                    intake.option_criterion_evidence.status.value
                    if intake.option_criterion_evidence is not None
                    else None
                ),
                "runtime_fallback_reached": fallback_reached,
                "productive_response_captured": bool(response_text),
            }
        )

    all_certified = all(
        record["intake_status"] == "complete"
        and record["deliberation_status"] == "explicit"
        and record["criteria_status"] == "explicit"
        and record["option_criterion_status"] == "explicit"
        and record["runtime_fallback_reached"] is False
        and record["productive_response_captured"] is True
        for record in records
    )
    preconditions = bool(
        contract["construction_contract_frozen"] is True
        and contract["construction_authorized"] is False
        and all_certified
    )

    payload: dict[str, object] = {
        "schema_version": "hcpdq-v2-h6-entry-path-dry-probe-certification-v1",
        "status": (
            "DRY_PROBES_CERTIFIED_CONSTRUCTION_AUTHORIZED"
            if preconditions
            else "NO_GO_DRY_PROBE_CERTIFICATION_FAILED"
        ),
        "baseline": "12969-pass-0-fail-ruff-clean",
        "family": "H6",
        "dry_probe_count": len(records),
        "dry_probes_are_held_out": False,
        "dry_probe_records": records,
        "entry_path_certified": all_certified,
        "construction_authorized": preconditions,
        "ground_truth_construction_authorized": preconditions,
        "held_out_exposure_authorized": False,
        "roby_held_out_execution_authorized": False,
        "primary_execution_authorized": False,
        "production_change_authorized": False,
        "benchmark_translation_authorized": False,
        "benchmark_router_authorized": False,
        "dry_probe_reuse_as_held_out_authorized": False,
        "old_consumed_case_reuse_authorized": False,
        "architectural_determination": (
            "Three synthetic non-held-out probes independently satisfy the "
            "exact existing structured H6 intake and complete through the "
            "productive conversation path while a fail-closed runtime fallback "
            "is armed. This certifies entry-path reachability only; it does not "
            "score H6 cognition. Construction of a new independent corpus and "
            "ground truth is authorized under the frozen contract, but held-out "
            "exposure and execution remain prohibited."
        ),
        "next_gate": (
            "HCPDQ-v2 H6 Entry-Path Equivalent Corpus — "
            "Independent Construction / Ground-Truth Freeze"
        ),
    }
    canonical = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    payload["certification_fingerprint"] = sha256(
        canonical.encode("utf-8")
    ).hexdigest()
    return payload


if __name__ == "__main__":
    print(
        json.dumps(
            certify_h6_entry_path_dry_probes(),
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    )
