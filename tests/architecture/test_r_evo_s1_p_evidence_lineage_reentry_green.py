from __future__ import annotations

from dataclasses import dataclass

from app.explicit_multisource_evidence_lineage_reentry_adapter import (
    ExplicitMultisourceEvidenceLineageReentryAdapterV1,
)
from app.explicit_multisource_productive_continuity_adapter import (
    ExplicitMultisourceProductiveContinuityV1,
)


@dataclass
class _Consumer:
    calls: list[dict[str, object]]
    result: object

    def bind_productive_explanatory_model_revision(self, **kwargs: object) -> object:
        self.calls.append(kwargs)
        return self.result


def test_s1_p_preserves_exact_lineage_and_existing_revision_artifacts():
    reasoning_result = object()
    continuity = ExplicitMultisourceProductiveContinuityV1(
        owner="owner",
        session_id="session",
        turn_id="turn",
        result=reasoning_result,
    )
    reentry = object()
    revised_report = object()
    revision = object()
    consumer = _Consumer(calls=[], result=revision)

    returned = ExplicitMultisourceEvidenceLineageReentryAdapterV1().deliver(
        continuity=continuity,
        source_turn_id="source-turn",
        reentry=reentry,
        revised_report=revised_report,
        consumer=consumer,
    )

    assert returned is revision
    assert len(consumer.calls) == 1
    call = consumer.calls[0]
    assert call["owner"] == continuity.owner
    assert call["session_id"] == continuity.session_id
    assert call["turn_id"] == continuity.turn_id
    assert call["source_turn_id"] == "source-turn"
    assert call["reentry"] is reentry
    assert call["revised_report"] is revised_report
    assert continuity.result is reasoning_result
