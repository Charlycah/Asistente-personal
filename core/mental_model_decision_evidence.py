from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256

from core.adaptive_cognition.mental_models import (
    MentalModel,
    MentalModelStatus,
    ModelAssertionStatus,
)
from core.scope_guard import ScopeDomain


@dataclass(frozen=True)
class MentalModelDecisionEvidence:
    option_id: str
    model_id: str
    assertion_id: str
    subject: str
    predicate: str
    value: str
    confidence: float
    owner: str
    domains: tuple[str, ...]
    provenance: tuple[str, ...]
    evidence_id: str
    canonical_authority: str = "unified_cognitive_coordination"
    read_only: bool = True
    creates_options: bool = False
    executes_actions: bool = False
    persists_results: bool = False

    def __post_init__(self) -> None:
        if not self.option_id.strip() or not self.provenance:
            raise ValueError("mental-model decision evidence is incomplete")
        if self.canonical_authority != "unified_cognitive_coordination":
            raise ValueError("canonical decision authority must be preserved")
        if any((not self.read_only, self.creates_options, self.executes_actions,
                self.persists_results)):
            raise ValueError("mental-model evidence violates governed limits")


class GovernedMentalModelDecisionEvidenceProjector:
    """Project explicit accepted assertions into bounded decision evidence."""

    MIN_CONFIDENCE = 0.85

    def project(
        self,
        models: tuple[MentalModel, ...],
        *,
        owner: str,
        domains: tuple[ScopeDomain | str, ...],
        option_matches: dict[str, tuple[tuple[str, str], ...]],
    ) -> tuple[MentalModelDecisionEvidence, ...]:
        allowed_domains = {ScopeDomain(item).value for item in domains}
        evidence: list[MentalModelDecisionEvidence] = []
        for model in models:
            model_domains = {item.value for item in model.normalized_domains}
            active = model.normalized_status is MentalModelStatus.ACTIVE
            if model.owner != owner or not active:
                continue
            if not model_domains.intersection(allowed_domains):
                continue
            for assertion in model.assertions:
                if assertion.normalized_status is not ModelAssertionStatus.ACCEPTED:
                    continue
                confident = assertion.confidence >= self.MIN_CONFIDENCE
                if not confident or not assertion.references:
                    continue
                for option_id, matches in sorted(option_matches.items()):
                    normalized = {
                        (predicate.strip().lower(), value.strip().lower())
                        for predicate, value in matches
                    }
                    key = (
                    assertion.predicate.strip().lower(),
                    assertion.value.strip().lower(),
                )
                    if key not in normalized:
                        continue
                    provenance = tuple(
                        f"{ref.reference_type}:{ref.reference_id}:{ref.fingerprint}"
                        for ref in assertion.references
                    )
                    fingerprint = sha256(
                        repr(
                            (
                                option_id,
                                model.model_id,
                                assertion.assertion_id,
                                owner,
                                sorted(model_domains),
                                provenance,
                            )
                        ).encode("utf-8")
                    ).hexdigest()
                    evidence.append(
                        MentalModelDecisionEvidence(
                            option_id=option_id,
                            model_id=model.model_id,
                            assertion_id=assertion.assertion_id,
                            subject=model.subject,
                            predicate=assertion.predicate,
                            value=assertion.value,
                            confidence=assertion.confidence,
                            owner=owner,
                            domains=tuple(sorted(model_domains)),
                            provenance=provenance,
                            evidence_id=f"mental-model-decision-{fingerprint[:16]}",
                        )
                    )
        return tuple(evidence)
