from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256

from core.governed_reasoning.contextual_semantic_grounding import (
    ContextualSemanticGroundingStatus,
    GovernedBoundedSemanticRoleRelationGrounder,
    GovernedContextualSemanticGroundingCandidate,
)
from core.governed_reasoning.relational_abstraction import (
    GovernedRelationalAbstractionCandidate,
    GovernedRelationalAbstractionInducer,
    RelationalAbstractionExample,
    RelationalAbstractionStatus,
)

_SCHEMA_VERSION = "cap-07-productive-abstraction-admission-v1"
_R1_FAMILY_ID = "productive_abstraction:r1_required_for_blocked"
_R1_RELATION = "required_for"
_R1_OUTCOME = "blocked_when_unavailable"
_R2_FAMILY_ID = "productive_abstraction:r2_prerequisite_unavailable_block"
_R2_RELATION = "required_for"
_R2_OUTCOME = "blocked_when_prerequisite_unavailable"


class ProductiveAbstractionAdmissionStatus(StrEnum):
    NOT_APPLICABLE = "not_applicable"
    ADMITTED = "admitted"
    DUPLICATE = "duplicate"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    ABSTRACTION_AVAILABLE = "abstraction_available"
    CONTESTED = "contested"
    ABSTAIN = "abstain"


@dataclass(frozen=True)
class GovernedProductiveAbstractionEvidence:
    example: RelationalAbstractionExample
    grounding_fingerprint: str
    family_id: str
    normalization_family_id: str
    counterexample: bool
    schema_version: str = _SCHEMA_VERSION
    canonical_authority: str = "governed_reasoning"
    read_only: bool = True
    session_local: bool = True
    persists: bool = False
    creates_memory: bool = False
    creates_learning: bool = False
    executes_transfer: bool = False
    grants_authority: bool = False

    def __post_init__(self) -> None:
        if (
            not self.grounding_fingerprint.strip()
            or not self.family_id.strip()
            or not self.normalization_family_id.strip()
        ):
            raise ValueError("productive abstraction evidence requires provenance")
        if self.canonical_authority != "governed_reasoning":
            raise ValueError(
                "productive abstraction evidence must preserve reasoning authority"
            )
        if any(
            (
                not self.read_only,
                not self.session_local,
                self.persists,
                self.creates_memory,
                self.creates_learning,
                self.executes_transfer,
                self.grants_authority,
            )
        ):
            raise ValueError("productive abstraction evidence violates governed limits")


@dataclass(frozen=True)
class CanonicalProductiveAbstractionEpisode:
    episode_id: str
    session_id: str
    turn_id: str
    scope_reference: str
    admitted_evidence_fingerprints: tuple[str, ...]
    abstraction_candidate: GovernedRelationalAbstractionCandidate
    source_fingerprint: str
    schema_version: str = _SCHEMA_VERSION
    canonical_authority: str = "governed_reasoning"
    read_only: bool = True
    session_local: bool = True
    persists: bool = False
    creates_memory: bool = False
    creates_learning: bool = False
    executes_transfer: bool = False
    grants_authority: bool = False

    def __post_init__(self) -> None:
        values = (
            self.episode_id,
            self.session_id,
            self.turn_id,
            self.scope_reference,
            self.source_fingerprint,
        )
        if any(not value.strip() for value in values):
            raise ValueError("productive abstraction episode requires exact lineage")
        if not self.admitted_evidence_fingerprints:
            raise ValueError(
                "productive abstraction episode requires admitted evidence"
            )
        if self.canonical_authority != "governed_reasoning":
            raise ValueError(
                "productive abstraction episode must preserve reasoning authority"
            )
        if self.abstraction_candidate.scope_reference != self.scope_reference:
            raise ValueError("productive abstraction episode scope mismatch")
        if any(
            (
                not self.read_only,
                not self.session_local,
                self.persists,
                self.creates_memory,
                self.creates_learning,
                self.executes_transfer,
                self.grants_authority,
            )
        ):
            raise ValueError("productive abstraction episode violates governed limits")


@dataclass(frozen=True)
class GovernedProductiveAbstractionAdmissionResult:
    status: ProductiveAbstractionAdmissionStatus
    session_id: str
    turn_id: str
    scope_reference: str
    admitted_support: int
    admitted_counterexamples: int
    rationale_codes: tuple[str, ...]
    source_fingerprint: str
    episode: CanonicalProductiveAbstractionEpisode | None = None
    schema_version: str = _SCHEMA_VERSION
    canonical_authority: str = "governed_reasoning"
    read_only: bool = True
    session_local: bool = True
    persists: bool = False
    creates_memory: bool = False
    creates_learning: bool = False
    executes_transfer: bool = False
    grants_authority: bool = False

    def __post_init__(self) -> None:
        if not self.session_id.strip() or not self.turn_id.strip():
            raise ValueError(
                "productive abstraction admission requires session and turn"
            )
        if not self.scope_reference.strip() or not self.source_fingerprint.strip():
            raise ValueError(
                "productive abstraction admission requires scope and provenance"
            )
        if not self.rationale_codes:
            raise ValueError("productive abstraction admission requires rationale")
        if self.admitted_support < 0 or self.admitted_counterexamples < 0:
            raise ValueError("productive abstraction admission counts are invalid")
        if self.canonical_authority != "governed_reasoning":
            raise ValueError(
                "productive abstraction admission must preserve reasoning authority"
            )
        if any(
            (
                not self.read_only,
                not self.session_local,
                self.persists,
                self.creates_memory,
                self.creates_learning,
                self.executes_transfer,
                self.grants_authority,
            )
        ):
            raise ValueError(
                "productive abstraction admission violates governed limits"
            )
        if self.status in {
            ProductiveAbstractionAdmissionStatus.ABSTRACTION_AVAILABLE,
            ProductiveAbstractionAdmissionStatus.CONTESTED,
        }:
            if self.episode is None:
                raise ValueError("available productive abstraction requires episode")
        elif self.episode is not None:
            raise ValueError("non-available admission cannot expose an episode")


class GovernedProductiveAbstractionAdmission:
    """Admit bounded grounded evidence into the existing abstraction inducer."""

    MAX_ITEMS_PER_SCOPE = 8
    MAX_SCOPES_PER_SESSION = 4

    def __init__(
        self,
        inducer: GovernedRelationalAbstractionInducer | None = None,
    ) -> None:
        self._inducer = inducer or GovernedRelationalAbstractionInducer()
        self._evidence: dict[
            str,
            dict[
                str,
                dict[str, dict[str, GovernedProductiveAbstractionEvidence]],
            ],
        ] = {}

    def observe(
        self,
        grounding: GovernedContextualSemanticGroundingCandidate,
        *,
        session_id: str,
        turn_id: str,
        scope_reference: str,
        counterexample: bool = False,
    ) -> GovernedProductiveAbstractionAdmissionResult:
        self._validate_lineage(session_id, turn_id, scope_reference)
        normalized = self.normalize_grounding(
            grounding,
            scope_reference=scope_reference,
            counterexample=counterexample,
        )
        if normalized is None:
            return self._result(
                ProductiveAbstractionAdmissionStatus.NOT_APPLICABLE,
                session_id=session_id,
                turn_id=turn_id,
                scope_reference=scope_reference,
                supports=(),
                counterexamples=(),
                rationale_codes=(
                    "abstraction_admission:not_certified_grounded_evidence",
                ),
                source_fingerprint=grounding.source_fingerprint,
            )

        family_bucket = self._family_bucket(
            session_id,
            scope_reference,
            normalized.normalization_family_id,
        )
        if family_bucket is None:
            return self._result(
                ProductiveAbstractionAdmissionStatus.ABSTAIN,
                session_id=session_id,
                turn_id=turn_id,
                scope_reference=scope_reference,
                supports=(),
                counterexamples=(),
                rationale_codes=("abstraction_admission:session_scope_bound_reached",),
                source_fingerprint=normalized.grounding_fingerprint,
            )
        if normalized.grounding_fingerprint in family_bucket:
            supports, counterexamples = self._partition(family_bucket)
            return self._result(
                ProductiveAbstractionAdmissionStatus.DUPLICATE,
                session_id=session_id,
                turn_id=turn_id,
                scope_reference=scope_reference,
                supports=supports,
                counterexamples=counterexamples,
                rationale_codes=("abstraction_admission:duplicate_evidence",),
                source_fingerprint=normalized.grounding_fingerprint,
            )
        if (
            self._scope_item_count(session_id, scope_reference)
            >= self.MAX_ITEMS_PER_SCOPE
        ):
            supports, counterexamples = self._partition(family_bucket)
            return self._result(
                ProductiveAbstractionAdmissionStatus.ABSTAIN,
                session_id=session_id,
                turn_id=turn_id,
                scope_reference=scope_reference,
                supports=supports,
                counterexamples=counterexamples,
                rationale_codes=("abstraction_admission:scope_item_bound_reached",),
                source_fingerprint=normalized.grounding_fingerprint,
            )

        family_bucket[normalized.grounding_fingerprint] = normalized
        supports, counterexamples = self._partition(family_bucket)
        if len(supports) < self._inducer.MINIMUM_SUPPORT:
            return self._result(
                ProductiveAbstractionAdmissionStatus.INSUFFICIENT_EVIDENCE,
                session_id=session_id,
                turn_id=turn_id,
                scope_reference=scope_reference,
                supports=supports,
                counterexamples=counterexamples,
                rationale_codes=("abstraction_admission:multiple_examples_required",),
                source_fingerprint=normalized.grounding_fingerprint,
            )

        candidate = self._inducer.induce(
            examples=tuple(item.example for item in supports),
            counterexamples=tuple(item.example for item in counterexamples),
            scope_reference=scope_reference,
        )
        status = self._admission_status(candidate)
        if status not in {
            ProductiveAbstractionAdmissionStatus.ABSTRACTION_AVAILABLE,
            ProductiveAbstractionAdmissionStatus.CONTESTED,
        }:
            return self._result(
                status,
                session_id=session_id,
                turn_id=turn_id,
                scope_reference=scope_reference,
                supports=supports,
                counterexamples=counterexamples,
                rationale_codes=(
                    "abstraction_admission:existing_inducer_result",
                    *candidate.rationale_codes,
                ),
                source_fingerprint=candidate.source_fingerprint,
            )

        episode = self._episode(
            session_id=session_id,
            turn_id=turn_id,
            scope_reference=scope_reference,
            supports=supports,
            counterexamples=counterexamples,
            candidate=candidate,
        )
        return self._result(
            status,
            session_id=session_id,
            turn_id=turn_id,
            scope_reference=scope_reference,
            supports=supports,
            counterexamples=counterexamples,
            rationale_codes=(
                "abstraction_admission:existing_inducer_reused",
                "abstraction_admission:read_only_episode",
                *candidate.rationale_codes,
            ),
            source_fingerprint=episode.source_fingerprint,
            episode=episode,
        )

    @staticmethod
    def normalize_grounding(
        grounding: GovernedContextualSemanticGroundingCandidate,
        *,
        scope_reference: str,
        counterexample: bool = False,
    ) -> GovernedProductiveAbstractionEvidence | None:
        if not scope_reference.strip():
            raise ValueError("productive abstraction normalization requires scope")
        if grounding.scope_reference != scope_reference:
            raise ValueError("productive abstraction grounding scope mismatch")
        if (
            grounding.normalized_status
            is not ContextualSemanticGroundingStatus.GROUNDED
        ):
            return None

        if (
            grounding.family_id
            == GovernedBoundedSemanticRoleRelationGrounder.FAMILY_ID
        ):
            if not GovernedProductiveAbstractionAdmission._is_r1_shape(grounding):
                return None
            relation = _R1_RELATION
            outcome = _R1_OUTCOME
            normalization_family_id = _R1_FAMILY_ID
        elif (
            grounding.family_id
            == GovernedBoundedSemanticRoleRelationGrounder.VELAR_FAMILY_ID
        ):
            if not GovernedProductiveAbstractionAdmission._is_r2_shape(grounding):
                return None
            relation = _R2_RELATION
            outcome = _R2_OUTCOME
            normalization_family_id = _R2_FAMILY_ID
        else:
            return None

        example_id = "relational-example:" + grounding.source_fingerprint[:24]
        example = RelationalAbstractionExample(
            example_id=example_id,
            scope_reference=scope_reference,
            relation=relation,
            outcome=outcome,
            source_fingerprint=grounding.source_fingerprint,
        )
        return GovernedProductiveAbstractionEvidence(
            example=example,
            grounding_fingerprint=grounding.source_fingerprint,
            family_id=grounding.family_id,
            normalization_family_id=normalization_family_id,
            counterexample=counterexample,
        )

    @staticmethod
    def _is_r1_shape(
        grounding: GovernedContextualSemanticGroundingCandidate,
    ) -> bool:
        expected = {
            ("dependent", "dependency", "exclusive"),
            ("resource", "availability", "unavailable"),
            ("dependent", "alternative", "absent"),
            ("dependent", "capability", "unavailable"),
        }
        return GovernedProductiveAbstractionAdmission._slot_shape(grounding) == expected

    @staticmethod
    def _is_r2_shape(
        grounding: GovernedContextualSemanticGroundingCandidate,
    ) -> bool:
        expected = {
            ("prerequisite", "required_for", "dependent"),
            ("prerequisite", "availability", "unavailable"),
            ("dependent", "capability", "unavailable"),
        }
        return GovernedProductiveAbstractionAdmission._slot_shape(grounding) == expected

    @staticmethod
    def _slot_shape(
        grounding: GovernedContextualSemanticGroundingCandidate,
    ) -> set[tuple[str, str, str]]:
        return {
            (
                str(slot.role_id),
                str(slot.relation),
                slot.value,
            )
            for slot in grounding.semantic_slots
        }

    @staticmethod
    def _validate_lineage(session_id: str, turn_id: str, scope_reference: str) -> None:
        if not session_id.strip() or not turn_id.strip() or not scope_reference.strip():
            raise ValueError("productive abstraction admission requires exact lineage")

    def _family_bucket(
        self,
        session_id: str,
        scope_reference: str,
        normalization_family_id: str,
    ) -> dict[str, GovernedProductiveAbstractionEvidence] | None:
        session = self._evidence.setdefault(session_id, {})
        if (
            scope_reference not in session
            and len(session) >= self.MAX_SCOPES_PER_SESSION
        ):
            return None
        scope = session.setdefault(scope_reference, {})
        return scope.setdefault(normalization_family_id, {})

    def _scope_item_count(self, session_id: str, scope_reference: str) -> int:
        session = self._evidence.get(session_id, {})
        scope = session.get(scope_reference, {})
        return sum(len(bucket) for bucket in scope.values())

    @staticmethod
    def _partition(
        scope_bucket: dict[str, GovernedProductiveAbstractionEvidence],
    ) -> tuple[
        tuple[GovernedProductiveAbstractionEvidence, ...],
        tuple[GovernedProductiveAbstractionEvidence, ...],
    ]:
        ordered = tuple(
            sorted(scope_bucket.values(), key=lambda item: item.grounding_fingerprint)
        )
        supports = tuple(item for item in ordered if not item.counterexample)
        counterexamples = tuple(item for item in ordered if item.counterexample)
        return supports, counterexamples

    @staticmethod
    def _admission_status(
        candidate: GovernedRelationalAbstractionCandidate,
    ) -> ProductiveAbstractionAdmissionStatus:
        if candidate.status is RelationalAbstractionStatus.REVIEW_REQUIRED:
            return ProductiveAbstractionAdmissionStatus.ABSTRACTION_AVAILABLE
        if candidate.status is RelationalAbstractionStatus.CONTESTED:
            return ProductiveAbstractionAdmissionStatus.CONTESTED
        if candidate.status is RelationalAbstractionStatus.INSUFFICIENT_EVIDENCE:
            return ProductiveAbstractionAdmissionStatus.INSUFFICIENT_EVIDENCE
        if candidate.status is RelationalAbstractionStatus.ABSTAIN:
            return ProductiveAbstractionAdmissionStatus.ABSTAIN
        return ProductiveAbstractionAdmissionStatus.NOT_APPLICABLE

    @staticmethod
    def _episode(
        *,
        session_id: str,
        turn_id: str,
        scope_reference: str,
        supports: tuple[GovernedProductiveAbstractionEvidence, ...],
        counterexamples: tuple[GovernedProductiveAbstractionEvidence, ...],
        candidate: GovernedRelationalAbstractionCandidate,
    ) -> CanonicalProductiveAbstractionEpisode:
        evidence_fingerprints = tuple(
            sorted(
                item.grounding_fingerprint
                for item in (*supports, *counterexamples)
            )
        )
        payload = repr(
            (
                _SCHEMA_VERSION,
                session_id,
                scope_reference,
                evidence_fingerprints,
                candidate.source_fingerprint,
            )
        )
        fingerprint = sha256(payload.encode("utf-8")).hexdigest()
        return CanonicalProductiveAbstractionEpisode(
            episode_id=f"productive-abstraction:{fingerprint[:24]}",
            session_id=session_id,
            turn_id=turn_id,
            scope_reference=scope_reference,
            admitted_evidence_fingerprints=evidence_fingerprints,
            abstraction_candidate=candidate,
            source_fingerprint=fingerprint,
        )

    @staticmethod
    def _result(
        status: ProductiveAbstractionAdmissionStatus,
        *,
        session_id: str,
        turn_id: str,
        scope_reference: str,
        supports: tuple[GovernedProductiveAbstractionEvidence, ...],
        counterexamples: tuple[GovernedProductiveAbstractionEvidence, ...],
        rationale_codes: tuple[str, ...],
        source_fingerprint: str,
        episode: CanonicalProductiveAbstractionEpisode | None = None,
    ) -> GovernedProductiveAbstractionAdmissionResult:
        payload = repr(
            (
                _SCHEMA_VERSION,
                status.value,
                session_id,
                turn_id,
                scope_reference,
                tuple(item.grounding_fingerprint for item in supports),
                tuple(item.grounding_fingerprint for item in counterexamples),
                rationale_codes,
                source_fingerprint,
            )
        )
        return GovernedProductiveAbstractionAdmissionResult(
            status=status,
            session_id=session_id,
            turn_id=turn_id,
            scope_reference=scope_reference,
            admitted_support=len(supports),
            admitted_counterexamples=len(counterexamples),
            rationale_codes=rationale_codes,
            source_fingerprint=sha256(payload.encode("utf-8")).hexdigest(),
            episode=episode,
        )
