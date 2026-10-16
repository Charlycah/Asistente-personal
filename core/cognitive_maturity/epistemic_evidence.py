from __future__ import annotations

from collections.abc import Callable, Iterator, Sequence
from contextlib import contextmanager
from contextvars import ContextVar, Token

from core.governed_reasoning.claims import Claim

from .cycle_contract import CognitiveCycleNodeRecord, CognitiveCycleNodeState
from .epistemic import EpistemicAssessment, EpistemicClassifier, EpistemicLevel

EvidenceSink = Callable[[CognitiveCycleNodeRecord], None]

_EVIDENCE_SINK: ContextVar[EvidenceSink | None] = ContextVar(
    "roby_epistemic_evidence_sink",
    default=None,
)


class EpistemicEvidenceAdapter:
    """Classify governed claims without exposing their private contents."""

    NODE_ID = "epistemic_classification"

    def __init__(self, classifier: EpistemicClassifier | None = None) -> None:
        self.classifier = classifier or EpistemicClassifier()

    @contextmanager
    def capture(self, sink: EvidenceSink) -> Iterator[None]:
        if not callable(sink):
            raise TypeError("epistemic evidence sink must be callable")
        token: Token[EvidenceSink | None] = _EVIDENCE_SINK.set(sink)
        try:
            yield
        finally:
            _EVIDENCE_SINK.reset(token)

    def observe_claims(
        self,
        claims: Sequence[Claim],
    ) -> tuple[EpistemicAssessment, ...]:
        sink = _EVIDENCE_SINK.get()
        if sink is None:
            return ()
        if not claims:
            sink(
                CognitiveCycleNodeRecord(
                    node_id=self.NODE_ID,
                    state=CognitiveCycleNodeState.OMITTED,
                    reason_codes=("epistemic:no_claims_available",),
                )
            )
            return ()

        assessments = tuple(self.classifier.classify(claim) for claim in claims)
        levels = {assessment.level for assessment in assessments}
        evidence_codes = tuple(
            f"epistemic:{level.value}" for level in EpistemicLevel if level in levels
        )
        unknown_present = EpistemicLevel.UNKNOWN in levels
        record = CognitiveCycleNodeRecord(
            node_id=self.NODE_ID,
            state=(
                CognitiveCycleNodeState.DEGRADED
                if unknown_present
                else CognitiveCycleNodeState.PARTICIPATED
            ),
            evidence_codes=evidence_codes,
            reason_codes=(
                ("epistemic:uncertainty_present",) if unknown_present else ()
            ),
        )
        sink(record)
        return assessments
