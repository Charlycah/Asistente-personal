from __future__ import annotations

from hashlib import sha256

from app.approved_learning_memory_materialization import (
    ApprovedLearningMemoryMaterializationProposalFoundation,
    ApprovedLearningMemoryMaterializationReport,
    ApprovedLearningScope,
    GovernedMemoryMaterializationProposal,
    LearningMemoryMaterializationOutcome,
    StructuralEligibilityEvidence,
)
from app.governed_g6_explicit_human_learning_approval import (
    GovernedApprovedLearningEvidence,
    GovernedG6ExplicitHumanLearningApprovalV1,
)
from app.governed_learning_candidate_m369_evaluation import (
    GovernedLearningCandidateM369EvaluationResult,
    GovernedLearningCandidateM369EvaluationStatus,
)
from core.cognitive_memory import LearningCategory
from core.governed_reasoning.contextual_rule_grounding_compilation import (
    ContextualRuleGroundingCompilationStatus,
)
from core.governed_reasoning.contextual_rule_interpretation import (
    ContextualRuleCandidateStatus,
)
from core.governed_reasoning.contextual_semantic_grounding import (
    ContextualSemanticGroundingStatus,
)
from core.memory_consolidation_foundation import (
    ConsolidationCandidate,
    ConsolidationDisposition,
    ConsolidationTarget,
)
from core.safe_learning_policies import SafeLearningDisposition


class GovernedG7ApprovedLearningMemoryMaterializationV1(
    ApprovedLearningMemoryMaterializationProposalFoundation
):
    """Admit exact G6/G7 approved learning into existing M366.6 proposal logic."""

    def build_structural_eligibility(
        self,
        evaluation: GovernedLearningCandidateM369EvaluationResult,
        approval: GovernedApprovedLearningEvidence,
    ) -> StructuralEligibilityEvidence | None:
        self._validate_linkage(evaluation, approval)
        content = evaluation.source_candidate.proposed_value
        scope_reference = approval.scope.value
        candidate = self._interpreter.produce(
            content,
            source_reference=approval.source_evaluation_fingerprint,
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
            "source_neutral_learning_candidate:preserved",
            "exact_g6_g7_linkage:preserved",
        )
        payload = (
            content_fingerprint,
            approval.source_evaluation_fingerprint,
            approval.learning_candidate_id,
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
            evaluation_fingerprint=approval.source_evaluation_fingerprint,
            learning_candidate_id=approval.learning_candidate_id,
            scope_reference=scope_reference,
            interpretation_fingerprint=candidate.source_fingerprint,
            grounding_fingerprint=grounding.source_fingerprint,
            compilation_fingerprint=compilation.source_fingerprint,
            source_fingerprint=sha256(repr(payload).encode("utf-8")).hexdigest(),
            supported=True,
            rationale_codes=rationale,
        )

    def propose(
        self,
        evaluation: GovernedLearningCandidateM369EvaluationResult,
        approval: GovernedApprovedLearningEvidence,
        *,
        structural_eligibility: StructuralEligibilityEvidence | None,
    ) -> ApprovedLearningMemoryMaterializationReport:
        self._validate_linkage(evaluation, approval)
        if approval.scope in {
            ApprovedLearningScope.SESSION,
            ApprovedLearningScope.UNSPECIFIED,
        }:
            return self._source_neutral_report(
                evaluation,
                approval,
                LearningMemoryMaterializationOutcome.REVIEW_REQUIRED,
                ("durable_scope_required",),
            )
        if not self._valid_structural_eligibility(
            evaluation,
            approval,
            structural_eligibility,
        ):
            return self._source_neutral_report(
                evaluation,
                approval,
                LearningMemoryMaterializationOutcome.REVIEW_REQUIRED,
                ("structural_eligibility_required",),
            )

        policy = evaluation.policy_candidate
        assert policy is not None
        candidate = ConsolidationCandidate(
            candidate_id=f"approved-learning-{policy.candidate_id}",
            content=evaluation.source_candidate.proposed_value,
            proposed_target=ConsolidationTarget.LONG_TERM,
            repetitions=max(1, len(policy.evidence_ids)),
            relevance=8,
            confidence=policy.confidence,
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
            return self._source_neutral_report(
                evaluation,
                approval,
                LearningMemoryMaterializationOutcome.REVIEW_REQUIRED,
                ("m366_6_did_not_produce_durable_proposal",),
            )

        proposal_fingerprint = sha256(
            repr(
                (
                    approval.source_evaluation_fingerprint,
                    approval.source_fingerprint,
                    approval.scope.value,
                    evaluation.source_candidate,
                    policy,
                    consolidation,
                    structural_eligibility.source_fingerprint,
                )
            ).encode("utf-8")
        ).hexdigest()
        proposal = GovernedMemoryMaterializationProposal(
            proposal_id=(
                f"approved-learning-memory-proposal-{proposal_fingerprint[:16]}"
            ),
            learning_candidate_id=approval.learning_candidate_id,
            preference_candidate_id="",
            policy_candidate_id=approval.policy_candidate_id,
            subject=evaluation.source_candidate.subject,
            value=evaluation.source_candidate.proposed_value,
            approval_id=approval.approval_id,
            approver=approval.approver,
            approval_scope=approval.scope,
            human_response_reference=approval.human_response_reference,
            m369_evaluation_fingerprint=approval.source_evaluation_fingerprint,
            human_approval_fingerprint=approval.source_fingerprint,
            confidence=policy.confidence,
            evidence_ids=policy.evidence_ids,
            consolidation=consolidation,
            source_fingerprint=proposal_fingerprint,
            learning_category=LearningCategory.STABLE_KNOWLEDGE,
            structural_evidence_fingerprint=(
                structural_eligibility.source_fingerprint
            ),
            structural_eligibility=structural_eligibility,
        )
        return self._source_neutral_report(
            evaluation,
            approval,
            LearningMemoryMaterializationOutcome.PROPOSAL_READY,
            (
                "approved_governed_learning",
                "source_neutral_stable_knowledge",
                "existing_m366_6_consolidation_consumed",
                "official_memory_gateway_required_for_write",
            ),
            proposal,
        )

    @staticmethod
    def _validate_linkage(
        evaluation: GovernedLearningCandidateM369EvaluationResult,
        approval: GovernedApprovedLearningEvidence,
    ) -> None:
        policy = evaluation.policy_candidate
        decision = evaluation.safe_learning_decision
        expected_fingerprint = (
            GovernedG6ExplicitHumanLearningApprovalV1.source_evaluation_fingerprint(
                evaluation
            )
        )
        linked = bool(
            evaluation.status
            is GovernedLearningCandidateM369EvaluationStatus.REVIEW_REQUIRED
            and policy is not None
            and decision is not None
            and decision.disposition is SafeLearningDisposition.REVIEW_REQUIRED
            and decision.review_authorized is True
            and decision.acceptance_authorized is False
            and decision.persistence_authorized is False
            and decision.adaptation_authorized is False
            and approval.source_evaluation_fingerprint == expected_fingerprint
            and approval.learning_candidate_id
            == evaluation.source_candidate.candidate_id
            and approval.policy_candidate_id == policy.candidate_id
        )
        if not linked:
            raise ValueError("exact G6/G7 learning materialization linkage required")

    @staticmethod
    def _valid_structural_eligibility(
        evaluation: GovernedLearningCandidateM369EvaluationResult,
        approval: GovernedApprovedLearningEvidence,
        evidence: StructuralEligibilityEvidence | None,
    ) -> bool:
        if evidence is None or not evidence.supported:
            return False
        if evidence.canonical_authority != "governed_reasoning":
            return False
        if evidence.source_fingerprint != evidence.recompute_fingerprint():
            return False
        expected_content = sha256(
            evaluation.source_candidate.proposed_value.encode("utf-8")
        ).hexdigest()
        if evidence.learned_content_fingerprint != expected_content:
            return False
        return bool(
            evidence.evaluation_fingerprint
            == approval.source_evaluation_fingerprint
            and evidence.learning_candidate_id == approval.learning_candidate_id
            and evidence.scope_reference == approval.scope.value
            and evidence.interpretation_fingerprint
            and evidence.grounding_fingerprint
            and evidence.compilation_fingerprint
        )

    @staticmethod
    def _source_neutral_report(
        evaluation: GovernedLearningCandidateM369EvaluationResult,
        approval: GovernedApprovedLearningEvidence,
        outcome: LearningMemoryMaterializationOutcome,
        rationale_codes: tuple[str, ...],
        proposal: GovernedMemoryMaterializationProposal | None = None,
    ) -> ApprovedLearningMemoryMaterializationReport:
        fingerprint = sha256(
            repr(
                (
                    approval.source_evaluation_fingerprint,
                    approval.source_fingerprint,
                    evaluation.source_candidate.candidate_id,
                    approval.policy_candidate_id,
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
