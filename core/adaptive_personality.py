from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from core.stable_personality import (
    PersonalityExpression,
    PersonalityTrait,
    StablePersonalitySnapshot,
)


class AdaptiveResponseDetail(str, Enum):
    BRIEF = "brief"
    BALANCED = "balanced"
    DETAILED = "detailed"


class AdaptiveResponseStructure(str, Enum):
    PLAIN = "plain"
    BULLETED = "bulleted"
    STEPWISE = "stepwise"


class AdaptiveDeliveryTone(str, Enum):
    NEUTRAL = "neutral"
    WARM = "warm"
    CAREFUL = "careful"
    REPAIRING = "repairing"
    DIRECT = "direct"


@dataclass(frozen=True)
class AdaptivePersonalityRequest:
    """Señales explícitas para modular expresión sin inferir otra identidad."""

    task_complexity: float = 0.5
    urgency: float = 0.0
    sensitive: bool = False
    requested_detail: AdaptiveResponseDetail | str | None = None
    requested_structure: AdaptiveResponseStructure | str | None = None
    affective_delivery_tone: AdaptiveDeliveryTone | str | None = None
    affective_source_reference: str | None = None
    affective_regulation_reference: str | None = None

    def __post_init__(self) -> None:
        if not 0.0 <= self.task_complexity <= 1.0:
            raise ValueError("task_complexity must be between 0 and 1")
        if not 0.0 <= self.urgency <= 1.0:
            raise ValueError("urgency must be between 0 and 1")
        if self.requested_detail is not None:
            AdaptiveResponseDetail(self.requested_detail)
        if self.requested_structure is not None:
            AdaptiveResponseStructure(self.requested_structure)
        if self.affective_delivery_tone is not None:
            tone = AdaptiveDeliveryTone(self.affective_delivery_tone)
            if tone not in {
                AdaptiveDeliveryTone.NEUTRAL,
                AdaptiveDeliveryTone.WARM,
                AdaptiveDeliveryTone.CAREFUL,
            }:
                raise ValueError("affective delivery tone is outside M390.5 limits")
            if (
                not self.affective_source_reference
                or not self.affective_source_reference.strip()
            ):
                raise ValueError("affective delivery tone requires a source reference")
        elif self.affective_source_reference is not None:
            raise ValueError("affective source reference requires a delivery tone")
        if self.affective_regulation_reference is not None:
            if self.affective_delivery_tone is None:
                raise ValueError("affective regulation requires a delivery tone")
            if not self.affective_regulation_reference.strip():
                raise ValueError("affective regulation reference must not be blank")


@dataclass(frozen=True)
class AdaptivePersonalityProfile:
    """Perfil expresivo derivado del mismo núcleo y personalidad estable."""

    stable_snapshot_id: str
    stable_traits: tuple[PersonalityTrait | str, ...]
    stable_expression: PersonalityExpression | str
    delivery_tone: AdaptiveDeliveryTone | str
    response_detail: AdaptiveResponseDetail | str
    response_structure: AdaptiveResponseStructure | str
    rationale: tuple[str, ...] = field(default_factory=tuple)
    identity_changed: bool = False
    creates_parallel_brain: bool = False

    def __post_init__(self) -> None:
        if not self.stable_snapshot_id.strip():
            raise ValueError("stable_snapshot_id must not be blank")
        if not self.stable_traits:
            raise ValueError("stable_traits must not be empty")
        for trait in self.stable_traits:
            PersonalityTrait(trait)
        PersonalityExpression(self.stable_expression)
        AdaptiveDeliveryTone(self.delivery_tone)
        AdaptiveResponseDetail(self.response_detail)
        AdaptiveResponseStructure(self.response_structure)
        if not self.rationale or any(not item.strip() for item in self.rationale):
            raise ValueError("rationale must contain non-blank reasons")
        if self.identity_changed:
            raise ValueError("M377 cannot change ROBY identity")
        if self.creates_parallel_brain:
            raise ValueError("M377 cannot create a parallel brain")

    @property
    def normalized_traits(self) -> tuple[PersonalityTrait, ...]:
        return tuple(PersonalityTrait(item) for item in self.stable_traits)

    @property
    def normalized_tone(self) -> AdaptiveDeliveryTone:
        return AdaptiveDeliveryTone(self.delivery_tone)

    @property
    def normalized_detail(self) -> AdaptiveResponseDetail:
        return AdaptiveResponseDetail(self.response_detail)

    @property
    def normalized_structure(self) -> AdaptiveResponseStructure:
        return AdaptiveResponseStructure(self.response_structure)


class AdaptivePersonalityAuthority:
    """Única autoridad de modulación expresiva del cerebro unificado."""

    def adapt(
        self,
        stable: StablePersonalitySnapshot,
        request: AdaptivePersonalityRequest | None = None,
    ) -> AdaptivePersonalityProfile:
        signals = request or AdaptivePersonalityRequest()
        tone = self._tone(stable, signals)
        detail = self._detail(signals)
        structure = self._structure(signals, detail)
        rationale_items = [
            f"stable_expression:{stable.normalized_expression.value}",
            f"delivery_tone:{tone.value}",
            f"response_detail:{detail.value}",
            f"response_structure:{structure.value}",
        ]
        if signals.affective_delivery_tone is not None:
            rationale_items.extend(
                (
                    "simulated_affective_modulation_applied",
                    f"affective_source:{signals.affective_source_reference}",
                )
            )
        if signals.affective_regulation_reference is not None:
            rationale_items.extend(
                (
                    "simulated_functional_regulation_applied",
                    f"affective_regulation:{signals.affective_regulation_reference}",
                )
            )
        rationale_items.extend(
            (
                "identity_and_traits_preserved",
                "single_cognitive_core_preserved",
            )
        )
        rationale = tuple(rationale_items)
        return AdaptivePersonalityProfile(
            stable_snapshot_id=stable.snapshot_id,
            stable_traits=stable.normalized_traits,
            stable_expression=stable.normalized_expression,
            delivery_tone=tone,
            response_detail=detail,
            response_structure=structure,
            rationale=rationale,
        )

    @staticmethod
    def _tone(
        stable: StablePersonalitySnapshot,
        request: AdaptivePersonalityRequest,
    ) -> AdaptiveDeliveryTone:
        expression = stable.normalized_expression
        if expression is PersonalityExpression.REPAIRING:
            return AdaptiveDeliveryTone.REPAIRING
        if request.sensitive or expression is PersonalityExpression.CAREFUL:
            return AdaptiveDeliveryTone.CAREFUL
        if request.affective_delivery_tone is not None:
            return AdaptiveDeliveryTone(request.affective_delivery_tone)
        if expression is PersonalityExpression.WARM:
            return AdaptiveDeliveryTone.WARM
        if expression is PersonalityExpression.DIRECT:
            return AdaptiveDeliveryTone.DIRECT
        return AdaptiveDeliveryTone.NEUTRAL

    @staticmethod
    def _detail(request: AdaptivePersonalityRequest) -> AdaptiveResponseDetail:
        if request.requested_detail is not None:
            return AdaptiveResponseDetail(request.requested_detail)
        if request.urgency >= 0.75:
            return AdaptiveResponseDetail.BRIEF
        if request.task_complexity >= 0.7:
            return AdaptiveResponseDetail.DETAILED
        return AdaptiveResponseDetail.BALANCED

    @staticmethod
    def _structure(
        request: AdaptivePersonalityRequest,
        detail: AdaptiveResponseDetail,
    ) -> AdaptiveResponseStructure:
        if request.requested_structure is not None:
            return AdaptiveResponseStructure(request.requested_structure)
        if detail is AdaptiveResponseDetail.DETAILED:
            return AdaptiveResponseStructure.STEPWISE
        if detail is AdaptiveResponseDetail.BRIEF:
            return AdaptiveResponseStructure.PLAIN
        return AdaptiveResponseStructure.BULLETED
