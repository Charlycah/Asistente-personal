from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256

from core.explicit_human_decision_deliberation import (
    ExplicitDecisionDeliberationEvidence,
    ExplicitDecisionDeliberationStatus,
)
from core.governed_decision_advisory import GovernedDecisionOption

_OPTION_ID_NAMESPACE = "post-m409.1-explicit-deliberation-decision-option-v1"
_OPTION_ID_PREFIX = "explicit-deliberation-option-"


@dataclass(frozen=True)
class ExplicitDeliberationDecisionOptionBinding:
    option_id: str
    source_fingerprint: str
    alternative_ordinal: int
    source_start_offset: int
    source_end_offset: int

    def __post_init__(self) -> None:
        if not self.option_id.strip():
            raise ValueError("decision option binding option id must not be blank")
        if not self.source_fingerprint.strip():
            raise ValueError("decision option binding fingerprint must not be blank")
        if self.alternative_ordinal < 0:
            raise ValueError("decision option binding ordinal must be non-negative")
        if self.source_start_offset < 0:
            raise ValueError(
                "decision option binding start offset must be non-negative"
            )  # noqa: E501
        if self.source_end_offset <= self.source_start_offset:
            raise ValueError("decision option binding span is invalid")


@dataclass(frozen=True)
class ExplicitDeliberationDecisionOptionAdaptation:
    options: tuple[GovernedDecisionOption, ...]
    bindings: tuple[ExplicitDeliberationDecisionOptionBinding, ...]
    source_fingerprint: str
    schema_version: str = "post-m409.1-explicit-deliberation-option-adapter-v1"
    read_only: bool = True
    persists_results: bool = False
    executes_actions: bool = False
    grants_authority: bool = False
    starts_background_process: bool = False

    def __post_init__(self) -> None:
        if not self.source_fingerprint.strip():
            raise ValueError("decision option adaptation fingerprint must not be blank")
        if len(self.options) != len(self.bindings):
            raise ValueError(
                "decision option adaptation requires one binding per option"
            )
        if len(self.options) < 2:
            raise ValueError("decision option adaptation requires at least two options")
        if len(self.options) > 5:
            raise ValueError("decision option adaptation supports at most five options")
        if any(
            (
                not self.read_only,
                self.persists_results,
                self.executes_actions,
                self.grants_authority,
                self.starts_background_process,
            )
        ):
            raise ValueError("decision option adaptation violates governed limits")
        option_ids = tuple(option.option_id for option in self.options)
        binding_ids = tuple(binding.option_id for binding in self.bindings)
        if option_ids != binding_ids:
            raise ValueError(
                "decision option bindings must preserve option order and identity"
            )
        if len(set(option_ids)) != len(option_ids):
            raise ValueError("decision option adaptation ids must be unique")
        if any(
            binding.source_fingerprint != self.source_fingerprint
            for binding in self.bindings
        ):
            raise ValueError(
                "decision option binding fingerprint must match adaptation"
            )


@dataclass(frozen=True)
class ExplicitDeliberationDecisionOptionAdapter:
    """Map explicit deliberation evidence into M391.6 input options only."""

    def adapt(
        self,
        evidence: ExplicitDecisionDeliberationEvidence,
    ) -> ExplicitDeliberationDecisionOptionAdaptation:
        if evidence.status is not ExplicitDecisionDeliberationStatus.EXPLICIT:
            raise ValueError(
                "only explicit deliberation evidence can become decision options"
            )

        options: list[GovernedDecisionOption] = []
        bindings: list[ExplicitDeliberationDecisionOptionBinding] = []
        for alternative in evidence.alternatives:
            option_id = self._option_id(
                evidence.source_fingerprint,
                alternative.ordinal,
            )
            options.append(
                GovernedDecisionOption(
                    option_id=option_id,
                    title=alternative.normalized_text,
                    organization_item_id=None,
                    scenario_hypothesis_id=None,
                    causal_relation_id=None,
                    explicit_preference=0.0,
                )
            )
            bindings.append(
                ExplicitDeliberationDecisionOptionBinding(
                    option_id=option_id,
                    source_fingerprint=evidence.source_fingerprint,
                    alternative_ordinal=alternative.ordinal,
                    source_start_offset=alternative.start_offset,
                    source_end_offset=alternative.end_offset,
                )
            )

        return ExplicitDeliberationDecisionOptionAdaptation(
            options=tuple(options),
            bindings=tuple(bindings),
            source_fingerprint=evidence.source_fingerprint,
        )

    @staticmethod
    def _option_id(source_fingerprint: str, ordinal: int) -> str:
        payload = f"{_OPTION_ID_NAMESPACE}:{source_fingerprint}:{ordinal}"
        digest = sha256(payload.encode("utf-8")).hexdigest()
        return f"{_OPTION_ID_PREFIX}{digest}"
