from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256


class RelationalAbstractionStatus(StrEnum):
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    NO_ABSTRACTION = "no_abstraction"
    REVIEW_REQUIRED = "review_required"
    CONTESTED = "contested"
    ABSTAIN = "abstain"


@dataclass(frozen=True)
class RelationalAbstractionExample:
    example_id: str
    scope_reference: str
    relation: str
    outcome: str
    source_fingerprint: str

    def __post_init__(self) -> None:
        values = (
            self.example_id,
            self.scope_reference,
            self.relation,
            self.outcome,
            self.source_fingerprint,
        )
        if any(not value.strip() for value in values):
            raise ValueError("relational abstraction example requires provenance")


@dataclass(frozen=True)
class GovernedRelationalAbstractionCandidate:
    status: RelationalAbstractionStatus
    scope_reference: str
    invariant_relation: str | None
    invariant_outcome: str | None
    supporting_example_ids: tuple[str, ...]
    counterexample_ids: tuple[str, ...]
    confidence: float
    rationale_codes: tuple[str, ...]
    source_fingerprint: str
    schema_version: str = "hce-governed-relational-abstraction-v1"
    canonical_authority: str = "governed_reasoning"
    read_only: bool = True
    session_local: bool = True
    persists_results: bool = False
    creates_memory: bool = False
    modifies_memory: bool = False
    creates_learning_candidate: bool = False
    modifies_learning: bool = False
    establishes_truth: bool = False
    authorizes_inference: bool = False
    registers_rule: bool = False
    executes_actions: bool = False
    grants_authority: bool = False

    def __post_init__(self) -> None:
        if not self.scope_reference.strip() or not self.source_fingerprint.strip():
            raise ValueError("relational abstraction requires scope and provenance")
        if not self.rationale_codes:
            raise ValueError("relational abstraction requires rationale")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("relational abstraction confidence is invalid")
        if self.canonical_authority != "governed_reasoning":
            raise ValueError("relational abstraction must preserve reasoning authority")
        if any(
            (
                not self.read_only,
                not self.session_local,
                self.persists_results,
                self.creates_memory,
                self.modifies_memory,
                self.creates_learning_candidate,
                self.modifies_learning,
                self.establishes_truth,
                self.authorizes_inference,
                self.registers_rule,
                self.executes_actions,
                self.grants_authority,
            )
        ):
            raise ValueError("relational abstraction violates governed limits")
        if self.status in {
            RelationalAbstractionStatus.REVIEW_REQUIRED,
            RelationalAbstractionStatus.CONTESTED,
        }:
            if not self.invariant_relation or not self.invariant_outcome:
                raise ValueError("reviewable abstraction requires an invariant")
            if len(self.supporting_example_ids) < 2:
                raise ValueError("abstraction requires multiple supporting examples")
        elif self.invariant_relation is not None or self.invariant_outcome is not None:
            raise ValueError("non-abstraction cannot expose a partial invariant")


class GovernedRelationalAbstractionInducer:
    """Induce one review-only relational invariant from explicit evidence."""

    MINIMUM_SUPPORT = 2

    def induce(
        self,
        *,
        examples: tuple[RelationalAbstractionExample, ...],
        counterexamples: tuple[RelationalAbstractionExample, ...],
        scope_reference: str,
    ) -> GovernedRelationalAbstractionCandidate:
        if not scope_reference.strip():
            raise ValueError("relational abstraction requires scope")
        all_items = (*examples, *counterexamples)
        ids = tuple(item.example_id for item in all_items)
        if len(ids) != len(set(ids)):
            raise ValueError("relational abstraction example ids must be unique")

        ordered_examples = tuple(sorted(examples, key=lambda item: item.example_id))
        ordered_counterexamples = tuple(
            sorted(counterexamples, key=lambda item: item.example_id)
        )
        if any(item.scope_reference != scope_reference for item in all_items):
            return self._result(
                scope_reference=scope_reference,
                status=RelationalAbstractionStatus.ABSTAIN,
                examples=(),
                counterexamples=(),
                rationale_codes=("abstraction:scope_mismatch",),
            )
        if len(ordered_examples) < self.MINIMUM_SUPPORT:
            return self._result(
                scope_reference=scope_reference,
                status=RelationalAbstractionStatus.INSUFFICIENT_EVIDENCE,
                examples=ordered_examples,
                counterexamples=ordered_counterexamples,
                rationale_codes=("abstraction:multiple_examples_required",),
            )

        relations = {item.relation for item in ordered_examples}
        if len(relations) != 1:
            return self._result(
                scope_reference=scope_reference,
                status=RelationalAbstractionStatus.NO_ABSTRACTION,
                examples=ordered_examples,
                counterexamples=ordered_counterexamples,
                rationale_codes=("abstraction:no_shared_relation",),
            )
        outcomes = {item.outcome for item in ordered_examples}
        if len(outcomes) != 1:
            return self._result(
                scope_reference=scope_reference,
                status=RelationalAbstractionStatus.NO_ABSTRACTION,
                examples=ordered_examples,
                counterexamples=ordered_counterexamples,
                rationale_codes=("abstraction:no_shared_outcome",),
            )

        relation = next(iter(relations))
        outcome = next(iter(outcomes))
        contradicting = tuple(
            item
            for item in ordered_counterexamples
            if item.relation == relation and item.outcome != outcome
        )
        status = (
            RelationalAbstractionStatus.CONTESTED
            if contradicting
            else RelationalAbstractionStatus.REVIEW_REQUIRED
        )
        confidence = round(
            len(ordered_examples)
            / (len(ordered_examples) + len(contradicting)),
            6,
        )
        rationale = (
            (
                "abstraction:shared_relational_invariant",
                "abstraction:counterexample_present",
            )
            if contradicting
            else (
                "abstraction:shared_relational_invariant",
                "abstraction:human_review_required",
            )
        )
        return self._result(
            scope_reference=scope_reference,
            status=status,
            examples=ordered_examples,
            counterexamples=contradicting,
            invariant_relation=relation,
            invariant_outcome=outcome,
            confidence=confidence,
            rationale_codes=rationale,
        )

    @staticmethod
    def _result(
        *,
        scope_reference: str,
        status: RelationalAbstractionStatus,
        examples: tuple[RelationalAbstractionExample, ...],
        counterexamples: tuple[RelationalAbstractionExample, ...],
        rationale_codes: tuple[str, ...],
        invariant_relation: str | None = None,
        invariant_outcome: str | None = None,
        confidence: float = 0.0,
    ) -> GovernedRelationalAbstractionCandidate:
        supporting_ids = (
            tuple(item.example_id for item in examples)
            if invariant_relation is not None
            else ()
        )
        counter_ids = tuple(item.example_id for item in counterexamples)
        payload = repr(
            (
                scope_reference,
                status.value,
                invariant_relation,
                invariant_outcome,
                tuple(
                    (item.example_id, item.source_fingerprint)
                    for item in examples
                ),
                tuple(
                    (item.example_id, item.source_fingerprint)
                    for item in counterexamples
                ),
                rationale_codes,
            )
        )
        return GovernedRelationalAbstractionCandidate(
            status=status,
            scope_reference=scope_reference,
            invariant_relation=invariant_relation,
            invariant_outcome=invariant_outcome,
            supporting_example_ids=supporting_ids,
            counterexample_ids=counter_ids,
            confidence=confidence,
            rationale_codes=rationale_codes,
            source_fingerprint=sha256(payload.encode("utf-8")).hexdigest(),
        )
