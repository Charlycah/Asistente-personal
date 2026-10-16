from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256


class ModelLocation(str, Enum):
    LOCAL = "local"
    REMOTE = "remote"


class InformationFreshness(str, Enum):
    STABLE = "stable"
    RECENT = "recent"
    LIVE = "live"


class ReasoningDemand(str, Enum):
    LIGHT = "light"
    STANDARD = "standard"
    COMPLEX = "complex"


class RoutingOutcome(str, Enum):
    SELECTED = "selected"
    WITHHELD = "withheld"
    NO_MODEL_REQUIRED = "no_model_required"


@dataclass(frozen=True)
class CognitiveModelProfile:
    name: str
    location: ModelLocation | str
    capabilities: tuple[str, ...] = ("text",)
    enabled: bool = True
    healthy: bool = True
    supports_current_information: bool = False
    reasoning_strength: int = 50
    privacy_score: int = 50
    latency_score: int = 50
    cost_score: int = 50

    def __post_init__(self) -> None:
        name = self.name.strip()
        if not name:
            raise ValueError("model profile name must not be blank")
        location = ModelLocation(self.location)
        capabilities = tuple(item.strip().casefold() for item in self.capabilities)
        if not capabilities or any(not item for item in capabilities):
            raise ValueError("model capabilities must not be blank")
        if len(capabilities) != len(set(capabilities)):
            raise ValueError("model capabilities must be unique")
        for value in (
            self.reasoning_strength,
            self.privacy_score,
            self.latency_score,
            self.cost_score,
        ):
            if not 0 <= value <= 100:
                raise ValueError("model profile scores must be between 0 and 100")
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "location", location)
        object.__setattr__(self, "capabilities", capabilities)


@dataclass(frozen=True)
class CognitiveRoutingRequest:
    owner: str
    purpose: str
    required_capabilities: tuple[str, ...] = ("text",)
    model_required: bool = True
    sensitive: bool = False
    freshness: InformationFreshness | str = InformationFreshness.STABLE
    reasoning: ReasoningDemand | str = ReasoningDemand.STANDARD
    remote_allowed: bool = True
    prefer_low_latency: bool = False
    prefer_low_cost: bool = False

    def __post_init__(self) -> None:
        owner = self.owner.strip()
        purpose = self.purpose.strip()
        capabilities = tuple(
            item.strip().casefold() for item in self.required_capabilities
        )
        if not owner:
            raise ValueError("routing owner must not be blank")
        if not purpose:
            raise ValueError("routing purpose must not be blank")
        if not capabilities or any(not item for item in capabilities):
            raise ValueError("required capabilities must not be blank")
        if len(capabilities) != len(set(capabilities)):
            raise ValueError("required capabilities must be unique")
        freshness = InformationFreshness(self.freshness)
        reasoning = ReasoningDemand(self.reasoning)
        if freshness is InformationFreshness.LIVE and not self.model_required:
            raise ValueError("live information request requires a model")
        object.__setattr__(self, "owner", owner)
        object.__setattr__(self, "purpose", purpose)
        object.__setattr__(self, "required_capabilities", capabilities)
        object.__setattr__(self, "freshness", freshness)
        object.__setattr__(self, "reasoning", reasoning)


@dataclass(frozen=True)
class CognitiveModelScore:
    model_name: str
    total: int
    privacy: int
    freshness: int
    reasoning: int
    latency: int
    cost: int
    local_first: int
    rationale: tuple[str, ...]


@dataclass(frozen=True)
class CognitiveRoutingDecision:
    request: CognitiveRoutingRequest
    outcome: RoutingOutcome | str
    selected_model: CognitiveModelProfile | None
    fallback_models: tuple[CognitiveModelProfile, ...]
    scores: tuple[CognitiveModelScore, ...]
    rationale: tuple[str, ...]
    network_access_required: bool
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    decision_id: str = ""

    def __post_init__(self) -> None:
        outcome = RoutingOutcome(self.outcome)
        fallbacks = tuple(self.fallback_models)
        scores = tuple(self.scores)
        rationale = tuple(item.strip() for item in self.rationale)
        if self.created_at.tzinfo is None:
            raise ValueError("routing decision timestamp must be timezone-aware")
        if not rationale or any(not item for item in rationale):
            raise ValueError("routing decision rationale must not be empty")
        if outcome is RoutingOutcome.SELECTED and self.selected_model is None:
            raise ValueError("selected outcome requires a model")
        if outcome is not RoutingOutcome.SELECTED and self.selected_model is not None:
            raise ValueError("inactive outcome cannot select a model")
        if self.selected_model is not None:
            if any(item.name == self.selected_model.name for item in fallbacks):
                raise ValueError("selected model cannot also be a fallback")
            expected_network = self.selected_model.location is ModelLocation.REMOTE
            if self.network_access_required != expected_network:
                raise ValueError("network requirement is inconsistent")
        elif self.network_access_required:
            raise ValueError("inactive decision cannot require network access")
        names = tuple(item.name.casefold() for item in fallbacks)
        if len(names) != len(set(names)):
            raise ValueError("fallback models must be unique")
        object.__setattr__(self, "outcome", outcome)
        object.__setattr__(self, "fallback_models", fallbacks)
        object.__setattr__(self, "scores", scores)
        object.__setattr__(self, "rationale", rationale)
        expected = sha256(self._identity_payload().encode()).hexdigest()
        if self.decision_id and self.decision_id != expected:
            raise ValueError("routing decision id is inconsistent")
        object.__setattr__(self, "decision_id", expected)

    def _identity_payload(self) -> str:
        return "|".join(
            (
                self.request.owner.casefold(),
                self.request.purpose,
                self.outcome.value,
                self.selected_model.name if self.selected_model else "",
                ",".join(item.name for item in self.fallback_models),
                self.created_at.isoformat(),
                *self.rationale,
            )
        )
