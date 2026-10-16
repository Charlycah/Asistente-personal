from __future__ import annotations

from core.governed_operational_conversation_pipeline import ResponseOriginMetadata
from core.governed_operational_conversation_pipeline.response_origin import (
    ResponseDecision,
    ResponseVerification,
)

from .models import (
    CognitivePlan,
    CognitivePlanOutcomeAssessment,
    EvidenceLevel,
    FreshnessRequirement,
    PlannedResponseDecision,
    ShadowAssessmentStatus,
)


class CognitivePlanOutcomeAssessor:
    """Compare a shadow plan with response evidence without governing execution."""

    def assess(
        self,
        plan: CognitivePlan,
        origin: ResponseOriginMetadata,
    ) -> CognitivePlanOutcomeAssessment:
        record = origin.confidence_record
        evidence_count = record.evidence_count
        freshness_satisfied = self._freshness_satisfied(plan, origin)
        evidence_satisfied = self._evidence_satisfied(plan, origin)
        abstention_consistent = self._abstention_consistent(plan, origin)

        rationale: list[str] = []
        if not freshness_satisfied:
            rationale.append("planned_freshness_not_observed")
        if not evidence_satisfied:
            rationale.append("planned_evidence_not_observed")
        if not abstention_consistent:
            rationale.append("planned_abstention_policy_not_observed")
        if record.conflicting_sources:
            rationale.append("conflicting_sources_observed")
        if origin.abstained:
            rationale.append("response_abstained")
        if not rationale:
            rationale.append("plan_requirements_observed")

        applicable = (
            plan.freshness is FreshnessRequirement.CURRENT
            or plan.minimum_evidence
            in {EvidenceLevel.SINGLE_SOURCE, EvidenceLevel.CORROBORATED}
            or plan.response_decision is PlannedResponseDecision.ABSTAIN_IF_UNVERIFIED
        )
        if not applicable:
            status = ShadowAssessmentStatus.NOT_APPLICABLE
        elif freshness_satisfied and evidence_satisfied and abstention_consistent:
            status = ShadowAssessmentStatus.SATISFIED
        elif not freshness_satisfied and not evidence_satisfied:
            status = ShadowAssessmentStatus.UNSATISFIED
        else:
            status = ShadowAssessmentStatus.PARTIAL

        return CognitivePlanOutcomeAssessment(
            status=status,
            freshness_satisfied=freshness_satisfied,
            evidence_satisfied=evidence_satisfied,
            abstention_consistent=abstention_consistent,
            observed_evidence_count=evidence_count,
            observed_conflicting_sources=record.conflicting_sources,
            observed_freshness=origin.freshness,
            observed_verification=record.verification.value,
            observed_abstention=origin.abstained,
            rationale_codes=tuple(rationale),
        )

    @staticmethod
    def _freshness_satisfied(
        plan: CognitivePlan,
        origin: ResponseOriginMetadata,
    ) -> bool:
        if plan.freshness is FreshnessRequirement.NONE:
            return True
        if origin.abstained:
            return True
        return origin.freshness in {"live", "recent", "recent_but_conflicting"}

    @staticmethod
    def _evidence_satisfied(
        plan: CognitivePlan,
        origin: ResponseOriginMetadata,
    ) -> bool:
        record = origin.confidence_record
        if origin.abstained:
            return True
        if plan.minimum_evidence in {EvidenceLevel.NONE, EvidenceLevel.INTERNAL}:
            return True
        if plan.minimum_evidence is EvidenceLevel.SINGLE_SOURCE:
            return (
                record.evidence_count >= 1
                and record.verification is not ResponseVerification.UNAVAILABLE
            )
        return record.evidence_count >= 2 and record.verification in {
            ResponseVerification.VERIFIED,
            ResponseVerification.PARTIAL,
        }

    @staticmethod
    def _abstention_consistent(
        plan: CognitivePlan,
        origin: ResponseOriginMetadata,
    ) -> bool:
        if plan.response_decision is PlannedResponseDecision.RESPOND:
            return True
        record = origin.confidence_record
        verified_enough = CognitivePlanOutcomeAssessor._evidence_satisfied(plan, origin)
        fresh_enough = CognitivePlanOutcomeAssessor._freshness_satisfied(plan, origin)
        if verified_enough and fresh_enough:
            return record.decision is ResponseDecision.ANSWERED or origin.abstained
        return origin.abstained
