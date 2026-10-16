from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from hashlib import sha256

from .unified_epistemic_evidence import UnifiedEpistemicCategory

SIMULATION_DISCLOSURE = (
    "Estado afectivo funcional simulado; no implica experiencia subjetiva."
)


class SimulatedInnerStateStatus(str, Enum):
    COMPLETE = "complete"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    DEGRADED = "degraded"


class SimulatedAffectiveTone(str, Enum):
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    POSITIVE = "positive"
    MIXED = "mixed"
    UNKNOWN = "unknown"


class SimulatedActivationLevel(str, Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    UNKNOWN = "unknown"


class SimulatedStabilityLevel(str, Enum):
    STABLE = "stable"
    VARIABLE = "variable"
    UNSTABLE = "unstable"
    UNKNOWN = "unknown"


class SimulatedConcernLevel(str, Enum):
    NONE = "none"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    UNKNOWN = "unknown"


class SimulatedRelationalOpenness(str, Enum):
    RESERVED = "reserved"
    BALANCED = "balanced"
    OPEN = "open"
    UNKNOWN = "unknown"


class SimulatedDominantState(str, Enum):
    CALM = "calm"
    ATTENTIVE = "attentive"
    CONCERNED = "concerned"
    ENCOURAGED = "encouraged"
    CAUTIOUS = "cautious"
    CURIOUS = "curious"
    SUPPORTIVE = "supportive"
    CONFLICTED = "conflicted"
    UNCERTAIN = "uncertain"
    NEUTRAL = "neutral"


@dataclass(frozen=True)
class SimulatedInnerStateSignal:
    source_authority: str
    source_reference: str
    epistemic_category: UnifiedEpistemicCategory
    affective_tone: SimulatedAffectiveTone
    activation_level: SimulatedActivationLevel
    stability_level: SimulatedStabilityLevel
    concern_level: SimulatedConcernLevel
    relational_openness: SimulatedRelationalOpenness
    dominant_state: SimulatedDominantState
    evidence_codes: tuple[str, ...]
    risk_codes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.source_authority.strip() or not self.source_reference.strip():
            raise ValueError("simulated inner-state signal requires coded provenance")
        if not self.evidence_codes:
            raise ValueError("simulated inner-state signal requires evidence codes")
        if any(not code.strip() for code in self.evidence_codes + self.risk_codes):
            raise ValueError("simulated inner-state codes cannot be blank")


@dataclass(frozen=True)
class SimulatedInnerStateSnapshot:
    snapshot_id: str
    status: SimulatedInnerStateStatus
    source_references: tuple[str, ...]
    affective_tone: SimulatedAffectiveTone
    activation_level: SimulatedActivationLevel
    stability_level: SimulatedStabilityLevel
    concern_level: SimulatedConcernLevel
    relational_openness: SimulatedRelationalOpenness
    dominant_state: SimulatedDominantState
    evidence_codes: tuple[str, ...]
    uncertainty_codes: tuple[str, ...]
    risk_codes: tuple[str, ...]
    simulation_disclosure: str
    source_fingerprint: str
    schema_version: str = "m390.1"
    read_only: bool = True
    grants_authority: bool = False
    contains_conversation_content: bool = False
    persists_state: bool = False
    claims_consciousness: bool = False
    claims_subjective_experience: bool = False
    claims_real_emotion: bool = False
    creates_memory: bool = False
    modifies_memory: bool = False
    creates_learning_candidate: bool = False
    modifies_learning: bool = False
    modifies_planning: bool = False
    modifies_personality: bool = False
    modifies_permissions: bool = False
    creates_goal: bool = False
    creates_task: bool = False
    schedules_action: bool = False
    executes_action: bool = False

    def __post_init__(self) -> None:
        if not self.snapshot_id.startswith("simulated-inner-state-"):
            raise ValueError("simulated inner-state identifier is invalid")
        if self.simulation_disclosure != SIMULATION_DISCLOSURE:
            raise ValueError("simulated inner state must disclose its simulated nature")
        if not self.read_only or self.grants_authority or self.persists_state:
            raise ValueError(
                "simulated inner state must remain read-only and transient"
            )
        if self.contains_conversation_content:
            raise ValueError(
                "simulated inner state cannot contain conversation content"
            )
        if any(
            (
                self.claims_consciousness,
                self.claims_subjective_experience,
                self.claims_real_emotion,
            )
        ):
            raise ValueError("simulated inner state cannot claim subjective experience")
        if any(
            (
                self.creates_memory,
                self.modifies_memory,
                self.creates_learning_candidate,
                self.modifies_learning,
                self.modifies_planning,
                self.modifies_personality,
                self.modifies_permissions,
                self.creates_goal,
                self.creates_task,
                self.schedules_action,
                self.executes_action,
            )
        ):
            raise ValueError("simulated inner state cannot modify governed domains")


class SimulatedInnerStateAuthority:
    """Single read-only authority for ROBY's functional simulated inner state."""

    authority_id = "simulated_inner_state"

    def evaluate(
        self,
        signals: tuple[SimulatedInnerStateSignal, ...],
    ) -> SimulatedInnerStateSnapshot:
        ordered = tuple(
            sorted(
                signals,
                key=lambda item: (
                    item.source_authority,
                    item.source_reference,
                    item.dominant_state.value,
                ),
            )
        )
        status = (
            SimulatedInnerStateStatus.COMPLETE
            if ordered
            else SimulatedInnerStateStatus.INSUFFICIENT_EVIDENCE
        )
        source_references = tuple(
            f"{item.source_authority}:{item.source_reference}" for item in ordered
        )
        affective_tone, tone_conflict = self._tone(ordered)
        activation_level, activation_conflict = self._consensus(
            ordered,
            "activation_level",
            SimulatedActivationLevel.UNKNOWN,
        )
        stability_level, stability_conflict = self._stability(ordered)
        concern_level, concern_conflict = self._consensus(
            ordered,
            "concern_level",
            SimulatedConcernLevel.UNKNOWN,
        )
        relational_openness, relational_conflict = self._consensus(
            ordered,
            "relational_openness",
            SimulatedRelationalOpenness.UNKNOWN,
        )
        dominant_state, dominant_conflict = self._dominant_state(ordered)
        conflict_fields = tuple(
            name
            for name, present in (
                ("affective_tone", tone_conflict),
                ("activation_level", activation_conflict),
                ("stability_level", stability_conflict),
                ("concern_level", concern_conflict),
                ("relational_openness", relational_conflict),
                ("dominant_state", dominant_conflict),
            )
            if present
        )
        evidence_codes = tuple(
            sorted({code for item in ordered for code in item.evidence_codes})
        )
        uncertainty_codes = self._uncertainty_codes(ordered, conflict_fields)
        risk_codes = tuple(
            sorted(
                {code for item in ordered for code in item.risk_codes}
                | (
                    {"simulated_inner_state_signal_conflict"}
                    if conflict_fields
                    else set()
                )
            )
        )
        fingerprint = sha256(
            repr(
                (
                    ordered,
                    status,
                    affective_tone,
                    activation_level,
                    stability_level,
                    concern_level,
                    relational_openness,
                    dominant_state,
                    evidence_codes,
                    uncertainty_codes,
                    risk_codes,
                )
            ).encode("utf-8")
        ).hexdigest()
        return SimulatedInnerStateSnapshot(
            snapshot_id=f"simulated-inner-state-{fingerprint[:16]}",
            status=status,
            source_references=source_references,
            affective_tone=affective_tone,
            activation_level=activation_level,
            stability_level=stability_level,
            concern_level=concern_level,
            relational_openness=relational_openness,
            dominant_state=dominant_state,
            evidence_codes=evidence_codes,
            uncertainty_codes=uncertainty_codes,
            risk_codes=risk_codes,
            simulation_disclosure=SIMULATION_DISCLOSURE,
            source_fingerprint=fingerprint,
        )

    def evaluate_safely(
        self,
        signals: tuple[SimulatedInnerStateSignal, ...],
    ) -> SimulatedInnerStateSnapshot:
        try:
            return self.evaluate(signals)
        except Exception:
            fingerprint = sha256(b"simulated-inner-state-failure").hexdigest()
            return SimulatedInnerStateSnapshot(
                snapshot_id=f"simulated-inner-state-{fingerprint[:16]}",
                status=SimulatedInnerStateStatus.DEGRADED,
                source_references=(),
                affective_tone=SimulatedAffectiveTone.UNKNOWN,
                activation_level=SimulatedActivationLevel.UNKNOWN,
                stability_level=SimulatedStabilityLevel.UNKNOWN,
                concern_level=SimulatedConcernLevel.UNKNOWN,
                relational_openness=SimulatedRelationalOpenness.UNKNOWN,
                dominant_state=SimulatedDominantState.UNCERTAIN,
                evidence_codes=("safe_degradation_without_side_effects",),
                uncertainty_codes=("simulated_inner_state_unavailable",),
                risk_codes=("simulated_inner_state_failure",),
                simulation_disclosure=SIMULATION_DISCLOSURE,
                source_fingerprint=fingerprint,
            )

    @staticmethod
    def _known_values(signals, attribute, unknown):
        return {
            getattr(item, attribute)
            for item in signals
            if getattr(item, attribute) != unknown
        }

    @classmethod
    def _consensus(cls, signals, attribute, unknown):
        values = cls._known_values(signals, attribute, unknown)
        if not values:
            return unknown, False
        if len(values) == 1:
            return next(iter(values)), False
        return unknown, True

    @classmethod
    def _tone(cls, signals):
        values = cls._known_values(
            signals, "affective_tone", SimulatedAffectiveTone.UNKNOWN
        )
        if not values:
            return SimulatedAffectiveTone.UNKNOWN, False
        if len(values) == 1:
            return next(iter(values)), False
        return SimulatedAffectiveTone.MIXED, True

    @classmethod
    def _stability(cls, signals):
        values = cls._known_values(
            signals, "stability_level", SimulatedStabilityLevel.UNKNOWN
        )
        if not values:
            return SimulatedStabilityLevel.UNKNOWN, False
        if len(values) == 1:
            return next(iter(values)), False
        return SimulatedStabilityLevel.VARIABLE, True

    @classmethod
    def _dominant_state(cls, signals):
        values = {item.dominant_state for item in signals}
        if not values:
            return SimulatedDominantState.UNCERTAIN, False
        if len(values) == 1:
            return next(iter(values)), False
        return SimulatedDominantState.CONFLICTED, True

    @staticmethod
    def _uncertainty_codes(signals, conflict_fields):
        codes = {f"conflict:{field}" for field in conflict_fields}
        if not signals:
            codes.add("no_simulated_inner_state_signals")
        if any(
            item.epistemic_category is UnifiedEpistemicCategory.INSUFFICIENT_INFORMATION
            for item in signals
        ):
            codes.add("source_epistemic_information_insufficient")
        if any(
            item.epistemic_category is UnifiedEpistemicCategory.POSSIBLE
            for item in signals
        ):
            codes.add("source_contains_possibility")
        return tuple(sorted(codes))
