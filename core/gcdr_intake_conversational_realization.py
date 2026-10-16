from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256

from core.governed_complex_decision_reasoning import ComplexDecisionReasoningStatus
from core.productive_gcdr_intake_integration import (
    ProductiveGCDRIntakeIntegrationResult,
    ProductiveGCDRIntakeIntegrationStatus,
)

_SCHEMA_VERSION = "post-m409.1-gcdr-intake-conversational-realization-v1"


class GCDRIntakeConversationalOutcome(StrEnum):
    RECOMMENDATION_PRESENT = "recommendation_present"
    REVIEW_REQUIRED = "review_required"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    CERTIFICATION_FAILED = "certification_failed"


@dataclass(frozen=True)
class GCDRIntakeConversationalRealization:
    response_text: str
    source_fingerprint: str
    advisory_report_id: str
    outcome: GCDRIntakeConversationalOutcome
    referenced_option_ids: tuple[str, ...]
    schema_version: str = _SCHEMA_VERSION
    read_only: bool = True
    advisory_only: bool = True
    human_decision_preserved: bool = True
    derives_new_reasoning: bool = False
    uses_llm: bool = False
    persists_results: bool = False
    executes_actions: bool = False
    grants_authority: bool = False
    starts_background_process: bool = False

    def __post_init__(self) -> None:
        if not self.response_text.strip():
            raise ValueError("GCDR realization text must not be blank")
        if len(self.source_fingerprint) != 64:
            raise ValueError("GCDR realization requires SHA-256 lineage")
        if not self.advisory_report_id.strip():
            raise ValueError("GCDR realization requires report reference")
        if any(
            (
                not self.read_only,
                not self.advisory_only,
                not self.human_decision_preserved,
                self.derives_new_reasoning,
                self.uses_llm,
                self.persists_results,
                self.executes_actions,
                self.grants_authority,
                self.starts_background_process,
            )
        ):
            raise ValueError("GCDR realization violates governed limits")


class GCDRIntakeConversationalRealizerV1:
    """Render certified GCDR intake results without adding decision reasoning."""

    def realize(
        self,
        result: ProductiveGCDRIntakeIntegrationResult,
    ) -> GCDRIntakeConversationalRealization:
        if result.status is ProductiveGCDRIntakeIntegrationStatus.NOT_APPLICABLE:
            raise ValueError("non-applicable GCDR intake must not be realized")

        if result.status is ProductiveGCDRIntakeIntegrationStatus.CERTIFICATION_FAILED:
            text = (
                "La decisión compleja está estructurada, pero su evidencia no puede "
                "certificarse de forma consistente. No voy a completar referencias ni "
                "inferir datos faltantes; revisá opciones, criterios y evidencia "
                "explícita."
            )
            return self._realization(
                result=result,
                response_text=text,
                advisory_report_id="gcdr-certification-failed",
                outcome=GCDRIntakeConversationalOutcome.CERTIFICATION_FAILED,
                option_ids=(),
            )

        if result.assembly is None or result.advisory is None:
            raise ValueError("ready GCDR intake requires certified advisory artifacts")

        report = result.advisory.report
        options_by_id = {
            option.option_id: option.title for option in result.assembly.options
        }
        option_ids = tuple(option.option_id for option in result.assembly.options)
        alternatives = self._alternatives(
            tuple(options_by_id[item] for item in option_ids)
        )

        if report.recommended_option_id is not None:
            recommended = options_by_id[report.recommended_option_id]
            outcome = GCDRIntakeConversationalOutcome.RECOMMENDATION_PRESENT
            text = (
                f"Entre {alternatives}, el análisis multicriterio gobernado favorece "
                f"«{recommended}». Es una recomendación consultiva; la decisión sigue "
                "siendo tuya."
            )
        elif report.status is ComplexDecisionReasoningStatus.REVIEW_REQUIRED:
            outcome = GCDRIntakeConversationalOutcome.REVIEW_REQUIRED
            text = (
                f"Entre {alternatives}, el análisis multicriterio gobernado requiere "
                "más revisión antes de recomendar una opción con fundamento. "
                "La decisión sigue siendo tuya."
            )
        else:
            outcome = GCDRIntakeConversationalOutcome.INSUFFICIENT_EVIDENCE
            text = (
                f"Entre {alternatives}, la evidencia certificada es insuficiente para "
                "recomendar una opción por encima de las demás. La decisión queda "
                "abierta y sigue siendo tuya."
            )

        return self._realization(
            result=result,
            response_text=text,
            advisory_report_id=report.report_id,
            outcome=outcome,
            option_ids=option_ids,
        )

    @staticmethod
    def _alternatives(titles: tuple[str, ...]) -> str:
        quoted = tuple(f"«{title}»" for title in titles)
        if len(quoted) == 2:
            return f"{quoted[0]} y {quoted[1]}"
        return f"{', '.join(quoted[:-1])} y {quoted[-1]}"

    @staticmethod
    def _realization(
        *,
        result: ProductiveGCDRIntakeIntegrationResult,
        response_text: str,
        advisory_report_id: str,
        outcome: GCDRIntakeConversationalOutcome,
        option_ids: tuple[str, ...],
    ) -> GCDRIntakeConversationalRealization:
        fingerprint = sha256(
            repr(
                (
                    _SCHEMA_VERSION,
                    result.source_fingerprint,
                    advisory_report_id,
                    outcome.value,
                    option_ids,
                    response_text,
                )
            ).encode("utf-8")
        ).hexdigest()
        return GCDRIntakeConversationalRealization(
            response_text=response_text,
            source_fingerprint=fingerprint,
            advisory_report_id=advisory_report_id,
            outcome=outcome,
            referenced_option_ids=option_ids,
        )
