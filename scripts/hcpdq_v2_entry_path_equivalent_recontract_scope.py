from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from hashlib import sha256

from app.official_conversation_gateway import OfficialConversationGateway
from core.explicit_complex_decision_intake_envelope import (
    ExplicitComplexDecisionIntakeEnvelopeFoundationV1,
)
from scripts.hcpdq_v2_evaluation_entry_path_equivalence_contract import (
    evaluate_entry_path_equivalence,
)


@dataclass(frozen=True)
class FamilyRecontractScope:
    family: str
    status: str
    allowed_entry_form: str | None
    existing_authority: str
    measurable_now: bool
    independent_freeze_authorized: bool
    reason: str


class _RuntimeStub:
    bootstrap = object()
    history: tuple[object, ...] = ()
    traces: tuple[object, ...] = ()

    def converse(self, text: str, **kwargs: object):
        del text, kwargs
        return type(
            "_Turn",
            (),
            {
                "response_text": "fallback",
                "status": "completed",
                "session_id": "scope-audit",
            },
        )()


def freeze_recontract_scope() -> dict[str, object]:
    contract = evaluate_entry_path_equivalence()
    parser = ExplicitComplexDecisionIntakeEnvelopeFoundationV1()
    h6_probe = parser.analyze(
        "Decisión: elegir A o B\n"
        "Criterios:\n- seguridad\n"
        "Evidencia:\n- A cumple seguridad"
    )
    gateway = OfficialConversationGateway(_RuntimeStub())

    h6_entry_available = h6_probe.status.value != "not_envelope"
    h7_conversation_entry_available = gateway._canonical_planning.bound

    scopes = (
        FamilyRecontractScope(
            family="H6",
            status="IN_SCOPE_ENTRY_FORM_FROZEN",
            allowed_entry_form=(
                "existing explicit Decisión/Criterios/Evidencia intake grammar"
            ),
            existing_authority=(
                "official conversation gateway -> productive GCDR intake"
            ),
            measurable_now=h6_entry_available,
            independent_freeze_authorized=h6_entry_available,
            reason=(
                "The existing productive H6 intake accepts this structured form "
                "without benchmark-specific translation or production changes."
            ),
        ),
        FamilyRecontractScope(
            family="H7",
            status="OUT_OF_SCOPE_PENDING_REAL_USER_ENTRY_PATH",
            allowed_entry_form=None,
            existing_authority="planning_foundation",
            measurable_now=h7_conversation_entry_available,
            independent_freeze_authorized=False,
            reason=(
                "No equivalent user/conversation entry path to the certified "
                "planning authority is currently bound. Internal re-entry is "
                "not sufficient under the entry-path equivalence contract."
            ),
        ),
    )

    h6 = scopes[0]
    h7 = scopes[1]
    payload: dict[str, object] = {
        "schema_version": "hcpdq-v2-entry-path-recontract-scope-v1",
        "status": "SCOPE_FROZEN_H6_GO_H7_NO_GO",
        "baseline": "12959-pass-0-fail-ruff-clean",
        "prior_contract_status": contract["status"],
        "families": {scope.family: asdict(scope) for scope in scopes},
        "new_corpus_constructed": False,
        "new_ground_truth_constructed": False,
        "held_out_exposure_occurred": False,
        "h6_new_independent_freeze_scope_authorized": (
            h6.independent_freeze_authorized
        ),
        "h7_new_independent_freeze_scope_authorized": (
            h7.independent_freeze_authorized
        ),
        "h7_production_work_authorized": False,
        "benchmark_specific_translation_authorized": False,
        "benchmark_specific_router_authorized": False,
        "old_consumed_freeze_reusable": False,
        "old_held_out_retry_authorized": False,
        "independence_requirements": [
            "new case identifiers and new case content",
            "no reuse or semantic rewrite of consumed held-out cases",
            "ground truth frozen independently before ROBY exposure",
            "entry-path equivalence certified before held-out exposure",
            "no benchmark-specific translation or routing",
            "no production change made for benchmark performance",
        ],
        "architectural_determination": (
            "The recontracted evaluation scope can legitimately proceed for H6 "
            "using only the already productive structured decision intake. H7 "
            "cannot enter a new independent freeze yet because no equivalent "
            "user-entry path to planning_foundation is currently certified. "
            "This gate freezes scope only and creates no cases or ground truth."
        ),
        "next_gate": (
            "HCPDQ-v2 H6 Entry-Path Equivalent Corpus — "
            "Independent Construction / Ground-Truth Freeze Contract"
        ),
    }
    canonical = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    payload["scope_fingerprint"] = sha256(
        canonical.encode("utf-8")
    ).hexdigest()
    return payload


if __name__ == "__main__":
    print(
        json.dumps(
            freeze_recontract_scope(),
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    )
