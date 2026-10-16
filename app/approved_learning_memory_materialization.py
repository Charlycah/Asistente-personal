from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from hashlib import sha256

from app.curiosity_m369_learning_evaluation import (
    CuriosityLearningKind,
    CuriosityM369EvaluationOutcome,
    CuriosityM369LearningEvaluationReport,
)
from app.memory_consolidation_foundation import MemoryConsolidationFoundation
from core.cognitive_memory import LearningCategory
from core.governed_reasoning.contextual_rule_grounding_compilation import (
    ContextualRuleGroundingCompilationStatus,
    GovernedContextualRuleGroundingCompiler,
)
from core.governed_reasoning.contextual_rule_interpretation import (
    ContextualRuleCandidateStatus,
    GovernedContextualRuleInterpretationProducer,
)
from core.governed_reasoning.contextual_semantic_grounding import (
    ContextualSemanticGroundingStatus,
    GovernedBoundedSemanticRoleRelationGrounder,
)
from core.memory_consolidation_foundation import (
    ConsolidationAssessment,
    ConsolidationCandidate,
    ConsolidationDisposition,
    ConsolidationTarget,
)


class ApprovedLearningScope(StrEnum):
    SESSION = "session"
    PROJECT = "project"
    CONTEXT = "context"
    PERSONAL = "personal"
    HOUSEHOLD = "household"
    GENERAL = "general"
    UNSPECIFIED = "unspecified"


class LearningMemoryMaterializationOutcome(StrEnum):
    PROPOSAL_READY = "proposal_ready"
    REVIEW_REQUIRED = "review_required"



@dataclass(frozen=True)
class StructuralEligibilityEvidence:
    """Read-only proof that existing governed Reasoning found bounded structure."""

    learned_content_fingerprint: str
    evaluation_fingerprint: str
    learning_candidate_id: str
    scope_reference: str
    interpretation_fingerprint: str
    grounding_fingerprint: str
    compilation_fingerprint: str
    source_fingerprint: str
    supported: bool
    rationale_codes: tuple[str, ...]
    canonical_authority: str = "governed_reasoning"
    read_only: bool = True
    persists_results: bool = False
    creates_memory: bool = False
    modifies_memory: bool = False
    establishes_truth: bool = False
    executes_actions: bool = False
    grants_authority: bool = False

    def __post_init__(self) -> None:
        required = (
            self.learned_content_fingerprint,
            self.evaluation_fingerprint,
            self.learning_candidate_id,
            self.scope_reference,
            self.interpretation_fingerprint,
            self.grounding_fingerprint,
            self.compilation_fingerprint,
            self.source_fingerprint,
        )
        if any(not value.strip() for value in required):
            raise ValueError("structural eligibility requires complete lineage")
        if not self.rationale_codes:
            raise ValueError("structural eligibility requires rationale")
        if self.canonical_authority != "governed_reasoning":
            raise ValueError("structural eligibility must preserve reasoning authority")
        if any(
            (
                not self.read_only,
                self.persists_results,
                self.creates_memory,
                self.modifies_memory,
                self.establishes_truth,
                self.executes_actions,
                self.grants_authority,
            )
        ):
            raise ValueError("structural eligibility violates governed limits")
        if self.source_fingerprint != self.recompute_fingerprint():
            raise ValueError("structural eligibility fingerprint mismatch")

    def recompute_fingerprint(self) -> str:
        return sha256(
            repr(
                (
                    self.learned_content_fingerprint,
                    self.evaluation_fingerprint,
                    self.learning_candidate_id,
                    self.scope_reference,
                    self.interpretation_fingerprint,
                    self.grounding_fingerprint,
                    self.compilation_fingerprint,
                    self.supported,
                    self.rationale_codes,
                    self.canonical_authority,
                )
            ).encode("utf-8")
        ).hexdigest()


@dataclass(frozen=True)
class ApprovedLearningEvidence:
    """Already-approved learning evidence; approval extraction is out of scope."""

    approval_id: str
    evaluation_report_id: str
    learning_candidate_id: str
    preference_candidate_id: str
    human_response_reference: str
    approver: str
    scope: ApprovedLearningScope
    source_fingerprint: str
    approved: bool = True
    learning_kind: CuriosityLearningKind = CuriosityLearningKind.PREFERENCE
    structural_evidence_fingerprint: str = field(default="")
    structural_eligibility: StructuralEligibilityEvidence | None = None

    def __post_init__(self) -> None:
        required = (
            self.approval_id,
            self.evaluation_report_id,
            self.learning_candidate_id,
            self.preference_candidate_id,
            self.human_response_reference,
            self.approver,
            self.source_fingerprint,
        )
        if any(not value.strip() for value in required):
            raise ValueError("approved learning evidence requires complete provenance")
        if not self.approved:
            raise ValueError(
                "materialization input must already be explicitly approved"
            )


@dataclass(frozen=True)
class GovernedMemoryMaterializationProposal:
    proposal_id: str
    learning_candidate_id: str
    preference_candidate_id: str
    subject: str
    value: str
    approval_id: str
    approver: str
    approval_scope: ApprovedLearningScope
    human_response_reference: str
    m369_evaluation_fingerprint: str
    human_approval_fingerprint: str
    confidence: float
    evidence_ids: tuple[str, ...]
    consolidation: ConsolidationAssessment
    source_fingerprint: str
    policy_candidate_id: str = ""
    schema_version: str = "post-m409.1-approved-learning-memory-proposal-v1"
    learning_category: LearningCategory = LearningCategory.USER_PREFERENCE
    structural_evidence_fingerprint: str = field(default="")
    structural_eligibility: StructuralEligibilityEvidence | None = None
    learning_kind: CuriosityLearningKind = CuriosityLearningKind.PREFERENCE
    target: ConsolidationTarget = ConsolidationTarget.LONG_TERM
    requires_official_memory_gateway: bool = True
    read_only: bool = True
    persists_results: bool = False
    writes_memory: bool = False
    writes_knowledge: bool = False
    invokes_learning_writer: bool = False
    modifies_profile: bool = False
    executes_actions: bool = False
    grants_authority: bool = False

    def __post_init__(self) -> None:
        if not self.proposal_id.startswith("approved-learning-memory-proposal-"):
            raise ValueError("memory materialization proposal identifier is invalid")
        if not self.subject.strip() or not self.value.strip():
            raise ValueError("memory materialization proposal requires content")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("memory proposal confidence must be between zero and one")
        if self.consolidation.persistence_performed:
            raise ValueError("materialization proposal cannot persist memory")
        if self.consolidation.proposed_target is not ConsolidationTarget.LONG_TERM:
            raise ValueError(
                "approved learning must remain long-term memory proposal"
            )
        if not self.requires_official_memory_gateway or not self.read_only:
            raise ValueError(
                "memory proposal must preserve the official writer boundary"
            )
        if any(
            (
                self.persists_results,
                self.writes_memory,
                self.writes_knowledge,
                self.invokes_learning_writer,
                self.modifies_profile,
                self.executes_actions,
                self.grants_authority,
            )
        ):
            raise ValueError("memory materialization proposal violates governed limits")


@dataclass(frozen=True)
class ApprovedLearningMemoryMaterializationReport:
    report_id: str
    outcome: LearningMemoryMaterializationOutcome
    rationale_codes: tuple[str, ...]
    source_fingerprint: str
    proposal: GovernedMemoryMaterializationProposal | None = None
    schema_version: str = "post-m409.1-approved-learning-materialization-v1"
    read_only: bool = True
    persistence_performed: bool = False
    official_memory_gateway_called: bool = False

    def __post_init__(self) -> None:
        if not self.report_id.startswith("approved-learning-materialization-"):
            raise ValueError("materialization report identifier is invalid")
        if not self.rationale_codes:
            raise ValueError("materialization report requires rationale")
        ready = self.outcome is LearningMemoryMaterializationOutcome.PROPOSAL_READY
        if (self.proposal is not None) is not ready:
            raise ValueError("proposal presence must match materialization outcome")
        if not self.read_only:
            raise ValueError("materialization report must remain read-only")
        if self.persistence_performed or self.official_memory_gateway_called:
            raise ValueError("proposal foundation cannot call the memory writer")


class ApprovedLearningMemoryMaterializationProposalFoundation:
    """Build an M366.6-governed memory proposal without writing persistent state."""

    def __init__(self) -> None:
        self._consolidation = MemoryConsolidationFoundation()
        self._interpreter = GovernedContextualRuleInterpretationProducer()
        self._grounder = GovernedBoundedSemanticRoleRelationGrounder()
        self._compiler = GovernedContextualRuleGroundingCompiler()

    def build_structural_eligibility(
        self,
        evaluation: CuriosityM369LearningEvaluationReport,
        approval: ApprovedLearningEvidence,
    ) -> StructuralEligibilityEvidence | None:
        """Reuse governed Reasoning to certify bounded structure without persistence."""
        preference = evaluation.preference_candidate
        if preference is None or evaluation.learning_candidate_id is None:
            return None
        content = preference.preferred_value
        scope_reference = approval.scope.value
        candidate = self._interpreter.produce(
            content,
            source_reference=evaluation.source_fingerprint,
            scope_reference=scope_reference,
        )
        if candidate.normalized_status is not ContextualRuleCandidateStatus.CANDIDATE:
            return None
        grounding = self._grounder.ground(
            candidate,
            scope_reference=scope_reference,
        )
        if (
            grounding.normalized_status
            is not ContextualSemanticGroundingStatus.GROUNDED
        ):
            return None
        compilation = self._compiler.compile(
            rule_candidate=candidate,
            semantic_grounding=grounding,
            scope_reference=scope_reference,
        )
        if (
            compilation.normalized_status
            is not ContextualRuleGroundingCompilationStatus.COMPILED
        ):
            return None
        content_fingerprint = sha256(content.encode("utf-8")).hexdigest()
        rationale = (
            "structural_eligibility:governed_reasoning",
            "interpretation:candidate",
            "grounding:grounded",
            "compilation:compiled",
        )
        payload = (
            content_fingerprint,
            evaluation.source_fingerprint,
            evaluation.learning_candidate_id,
            scope_reference,
            candidate.source_fingerprint,
            grounding.source_fingerprint,
            compilation.source_fingerprint,
            True,
            rationale,
            "governed_reasoning",
        )
        return StructuralEligibilityEvidence(
            learned_content_fingerprint=content_fingerprint,
            evaluation_fingerprint=evaluation.source_fingerprint,
            learning_candidate_id=evaluation.learning_candidate_id,
            scope_reference=scope_reference,
            interpretation_fingerprint=candidate.source_fingerprint,
            grounding_fingerprint=grounding.source_fingerprint,
            compilation_fingerprint=compilation.source_fingerprint,
            source_fingerprint=sha256(repr(payload).encode("utf-8")).hexdigest(),
            supported=True,
            rationale_codes=rationale,
        )

    @staticmethod
    def _validate_structural_eligibility(
        evaluation: CuriosityM369LearningEvaluationReport,
        approval: ApprovedLearningEvidence,
    ) -> bool:
        if approval.learning_kind is not CuriosityLearningKind.STABLE_KNOWLEDGE:
            return True
        evidence = approval.structural_eligibility
        preference = evaluation.preference_candidate
        if evidence is None or preference is None:
            return False
        if not evidence.supported:
            return False
        if evidence.canonical_authority != "governed_reasoning":
            return False
        if evidence.source_fingerprint != evidence.recompute_fingerprint():
            return False
        if evidence.learned_content_fingerprint != sha256(
            preference.preferred_value.encode("utf-8")
        ).hexdigest():
            return False
        if evidence.evaluation_fingerprint != evaluation.source_fingerprint:
            return False
        if evidence.learning_candidate_id != evaluation.learning_candidate_id:
            return False
        if evidence.scope_reference != approval.scope.value:
            return False
        return bool(
            evidence.interpretation_fingerprint
            and evidence.grounding_fingerprint
            and evidence.compilation_fingerprint
        )

    def propose(
        self,
        evaluation: CuriosityM369LearningEvaluationReport,
        approval: ApprovedLearningEvidence,
    ) -> ApprovedLearningMemoryMaterializationReport:
        self._validate_linkage(evaluation, approval)
        if not self._validate_structural_eligibility(evaluation, approval):
            return self._report(
                evaluation,
                approval,
                LearningMemoryMaterializationOutcome.REVIEW_REQUIRED,
                ("structural_eligibility_required",),
            )
        if approval.scope in {
            ApprovedLearningScope.SESSION,
            ApprovedLearningScope.UNSPECIFIED,
        }:
            return self._report(
                evaluation,
                approval,
                LearningMemoryMaterializationOutcome.REVIEW_REQUIRED,
                ("durable_scope_required",),
            )

        preference = evaluation.preference_candidate
        if preference is None:
            raise ValueError(
                "approved preference evaluation requires preference candidate"
            )
        candidate = ConsolidationCandidate(
            candidate_id=f"approved-learning-{preference.preference_id}",
            content=preference.preferred_value,
            proposed_target=ConsolidationTarget.LONG_TERM,
            repetitions=max(1, preference.evidence_count),
            relevance=8,
            confidence=preference.confidence,
            explicit_user_intent=True,
            personal_or_sensitive=False,
            conflicts_with_memory=False,
            procedural_structure=False,
        )
        consolidation = self._consolidation.assess(candidate)
        if consolidation.disposition not in {
            ConsolidationDisposition.PROPOSE_LONG_TERM,
            ConsolidationDisposition.REQUEST_CONFIRMATION,
        }:
            return self._report(
                evaluation,
                approval,
                LearningMemoryMaterializationOutcome.REVIEW_REQUIRED,
                ("m366_6_did_not_produce_durable_proposal",),
            )

        proposal_fingerprint = sha256(
            repr(
                (
                    evaluation.source_fingerprint,
                    approval.source_fingerprint,
                    approval.scope.value,
                    preference,
                    consolidation,
                )
            ).encode("utf-8")
        ).hexdigest()
        proposal = GovernedMemoryMaterializationProposal(
            proposal_id=(
                f"approved-learning-memory-proposal-{proposal_fingerprint[:16]}"
            ),
            learning_candidate_id=approval.learning_candidate_id,
            preference_candidate_id=approval.preference_candidate_id,
            subject=preference.subject,
            value=preference.preferred_value,
            approval_id=approval.approval_id,
            approver=approval.approver,
            approval_scope=approval.scope,
            human_response_reference=approval.human_response_reference,
            m369_evaluation_fingerprint=evaluation.source_fingerprint,
            human_approval_fingerprint=approval.source_fingerprint,
            confidence=preference.confidence,
            evidence_ids=preference.evidence_ids,
            consolidation=consolidation,
            source_fingerprint=proposal_fingerprint,
            learning_category=(
                LearningCategory.STABLE_KNOWLEDGE
                if approval.learning_kind is CuriosityLearningKind.STABLE_KNOWLEDGE
                else LearningCategory.USER_PREFERENCE
            ),
            learning_kind=approval.learning_kind,
            structural_evidence_fingerprint=(
                approval.structural_eligibility.source_fingerprint
                if approval.structural_eligibility is not None
                else approval.structural_evidence_fingerprint
            ),
            structural_eligibility=approval.structural_eligibility,
        )
        return self._report(
            evaluation,
            approval,
            LearningMemoryMaterializationOutcome.PROPOSAL_READY,
            (
                "approved_governed_learning",
                "explicit_durable_scope",
                "existing_m366_6_consolidation_consumed",
                "official_memory_gateway_required_for_write",
            ),
            proposal,
        )

    @staticmethod
    def _validate_linkage(
        evaluation: CuriosityM369LearningEvaluationReport,
        approval: ApprovedLearningEvidence,
    ) -> None:
        if evaluation.outcome is not CuriosityM369EvaluationOutcome.REVIEW_REQUIRED:
            raise ValueError("materialization requires M369 REVIEW_REQUIRED evaluation")
        if evaluation.learning_candidate_id is None:
            raise ValueError("M369 evaluation is missing learning candidate identity")
        preference = evaluation.preference_candidate
        decision = evaluation.safe_learning_decision
        if preference is None or decision is None or not decision.review_authorized:
            raise ValueError(
                "materialization requires review-authorized M369 learning candidate"
            )
        if approval.evaluation_report_id != evaluation.report_id:
            raise ValueError("approval must exactly reference M369 evaluation report")
        if approval.learning_candidate_id != evaluation.learning_candidate_id:
            raise ValueError("approval must preserve learning candidate identity")
        if approval.preference_candidate_id != preference.preference_id:
            raise ValueError("approval must preserve preference candidate identity")

    @staticmethod
    def _report(
        evaluation: CuriosityM369LearningEvaluationReport,
        approval: ApprovedLearningEvidence,
        outcome: LearningMemoryMaterializationOutcome,
        rationale_codes: tuple[str, ...],
        proposal: GovernedMemoryMaterializationProposal | None = None,
    ) -> ApprovedLearningMemoryMaterializationReport:
        fingerprint = sha256(
            repr(
                (
                    evaluation.source_fingerprint,
                    approval.source_fingerprint,
                    outcome.value,
                    rationale_codes,
                    proposal.source_fingerprint if proposal is not None else None,
                )
            ).encode("utf-8")
        ).hexdigest()
        return ApprovedLearningMemoryMaterializationReport(
            report_id=f"approved-learning-materialization-{fingerprint[:16]}",
            outcome=outcome,
            rationale_codes=rationale_codes,
            source_fingerprint=fingerprint,
            proposal=proposal,
        )
