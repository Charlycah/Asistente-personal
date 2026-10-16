from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from hashlib import sha256

from core.adaptive_personality import AdaptivePersonalityRequest

from .conversation_reflection import ConversationReflectionReport
from .explicit_inner_continuity import ExplicitInnerContinuityReport
from .simulated_functional_regulation import SimulatedFunctionalRegulationReport
from .simulated_inner_state import SimulatedInnerStateSnapshot


class M390IntegralEvidenceStatus(str, Enum):
    COMPLETE = "complete"
    INCOMPLETE = "incomplete"
    CONFLICT = "conflict"


@dataclass(frozen=True)
class M390IntegralEvidenceReport:
    report_id: str
    status: M390IntegralEvidenceStatus
    evidence_codes: tuple[str, ...]
    missing_codes: tuple[str, ...]
    conflict_codes: tuple[str, ...]
    source_references: tuple[str, ...]
    source_fingerprint: str
    schema_version: str = "m390.8"
    read_only: bool = True
    grants_authority: bool = False
    persists_state: bool = False
    creates_memory: bool = False
    modifies_learning: bool = False
    modifies_personality: bool = False
    modifies_planning: bool = False
    executes_action: bool = False

    def __post_init__(self) -> None:
        if not self.report_id.startswith("m390-integral-evidence-"):
            raise ValueError("M390 integral evidence identifier is invalid")
        if not self.read_only or self.grants_authority or self.persists_state:
            raise ValueError("M390 integral evidence must remain advisory")
        if any(
            (
                self.creates_memory,
                self.modifies_learning,
                self.modifies_personality,
                self.modifies_planning,
                self.executes_action,
            )
        ):
            raise ValueError("M390 integral evidence cannot modify governed domains")


class M390IntegralEvidenceDiagnostic:
    """Read-only closure diagnostic for explicit M390 evidence lineage."""

    diagnostic_id = "m390_integral_evidence"

    def diagnose(
        self,
        inner_state: SimulatedInnerStateSnapshot | None,
        continuity: ExplicitInnerContinuityReport | None = None,
        regulation: SimulatedFunctionalRegulationReport | None = None,
        reflection: ConversationReflectionReport | None = None,
        expression: AdaptivePersonalityRequest | None = None,
    ) -> M390IntegralEvidenceReport:
        evidence: set[str] = set()
        missing: set[str] = set()
        conflicts: set[str] = set()
        references: list[str] = []

        if inner_state is None:
            missing.add("missing_simulated_inner_state_snapshot")
        else:
            evidence.add("simulated_inner_state_present")
            references.append(inner_state.snapshot_id)

        if continuity is None:
            missing.add("missing_explicit_inner_continuity")
        else:
            evidence.add("explicit_inner_continuity_present")
            references.append(continuity.report_id)
            if inner_state is not None and continuity.current_snapshot_id != (
                inner_state.snapshot_id
            ):
                conflicts.add("continuity_current_snapshot_mismatch")

        if regulation is None:
            missing.add("missing_simulated_functional_regulation")
        else:
            evidence.add("simulated_functional_regulation_present")
            references.append(regulation.report_id)
            if inner_state is not None and regulation.current_snapshot_id != (
                inner_state.snapshot_id
            ):
                conflicts.add("regulation_current_snapshot_mismatch")
            if continuity is not None and regulation.continuity_report_id not in {
                None,
                continuity.report_id,
            }:
                conflicts.add("regulation_continuity_mismatch")

        if reflection is None:
            missing.add("missing_inner_state_reflection")
        else:
            evidence.add("inner_state_reflection_present")
            references.append(reflection.report_id)
            if inner_state is not None and reflection.inner_state_snapshot_id != (
                inner_state.snapshot_id
            ):
                conflicts.add("reflection_inner_state_mismatch")
            if continuity is not None and reflection.inner_continuity_report_id != (
                continuity.report_id
            ):
                conflicts.add("reflection_continuity_mismatch")
            if regulation is not None and reflection.inner_regulation_report_id != (
                regulation.report_id
            ):
                conflicts.add("reflection_regulation_mismatch")

        if expression is None:
            missing.add("missing_governed_expressive_modulation")
        else:
            evidence.add("governed_expressive_modulation_present")
            if expression.affective_source_reference is not None:
                references.append(expression.affective_source_reference)
            if (
                inner_state is not None
                and expression.affective_source_reference
                not in {None, inner_state.snapshot_id}
            ):
                conflicts.add("expression_inner_state_mismatch")
            if (
                regulation is not None
                and expression.affective_regulation_reference
                not in {None, regulation.report_id}
            ):
                conflicts.add("expression_regulation_mismatch")

        status = M390IntegralEvidenceStatus.COMPLETE
        if conflicts:
            status = M390IntegralEvidenceStatus.CONFLICT
        elif missing:
            status = M390IntegralEvidenceStatus.INCOMPLETE

        ordered_evidence = tuple(sorted(evidence))
        ordered_missing = tuple(sorted(missing))
        ordered_conflicts = tuple(sorted(conflicts))
        ordered_references = tuple(references)
        fingerprint = sha256(
            repr(
                (
                    status,
                    ordered_evidence,
                    ordered_missing,
                    ordered_conflicts,
                    ordered_references,
                )
            ).encode("utf-8")
        ).hexdigest()
        return M390IntegralEvidenceReport(
            report_id=f"m390-integral-evidence-{fingerprint[:16]}",
            status=status,
            evidence_codes=ordered_evidence,
            missing_codes=ordered_missing,
            conflict_codes=ordered_conflicts,
            source_references=ordered_references,
            source_fingerprint=fingerprint,
        )
