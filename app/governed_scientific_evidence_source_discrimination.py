from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Iterable

from core.governed_reasoning.multi_hypothesis_discrimination import (
    DiscriminatingEvidenceRequirement,
)

from .governed_conversational_source_selection import (
    GovernedConversationalSourceSelection,
    GovernedConversationalSourceSelectionRequest,
    GovernedConversationalSourceSelectionStatus,
    GovernedConversationalSourceSelector,
)
from .governed_information_sources import (
    GovernedInformationSource,
    GovernedInformationSources,
    InformationEvidenceKind,
    InformationSourceKind,
    InformationSourceStatus,
)


class GovernedScientificEvidenceSourceDiscriminationStatus(StrEnum):
    SELECTED = "selected"
    NOT_AUTHORIZED = "not_authorized"
    NOT_SUPPORTED = "not_supported"
    UNAVAILABLE = "unavailable"


@dataclass(frozen=True)
class GovernedScientificEvidenceSourceDiscriminationResult:
    status: GovernedScientificEvidenceSourceDiscriminationStatus
    requirement_id: str
    selection: GovernedConversationalSourceSelection | None = None
    eligible_source_ids: tuple[str, ...] = ()
    accepted_evidence_kinds: tuple[InformationEvidenceKind, ...] = ()
    rationale_codes: tuple[str, ...] = ()


class GovernedScientificEvidenceSourceDiscrimination:
    """Bound scientific evidence need to existing governed source contracts."""

    _SCIENTIFIC_MARKERS = frozenset(
        {
            "clinical",
            "evidence",
            "guidance",
            "guideline",
            "health",
            "nutrition",
            "scientific",
            "study",
        }
    )
    _OFFICIAL_MARKERS = frozenset(
        {
            "agency",
            "announcement",
            "document",
            "official",
            "record",
            "status",
        }
    )

    def __init__(
        self,
        *,
        sources: GovernedInformationSources,
        selector: GovernedConversationalSourceSelector,
    ) -> None:
        self.sources = sources
        self.selector = selector

    def discriminate(
        self,
        *,
        explicit_scientific_intent: bool,
        requirement: DiscriminatingEvidenceRequirement,
        request: GovernedConversationalSourceSelectionRequest,
        registered_sources: Iterable[str],
    ) -> GovernedScientificEvidenceSourceDiscriminationResult:
        if not explicit_scientific_intent:
            return self._result(
                requirement,
                GovernedScientificEvidenceSourceDiscriminationStatus.NOT_AUTHORIZED,
                rationale_codes=("explicit_scientific_intent_required",),
            )

        evidence_kinds = self._evidence_kinds_for(requirement)
        if not evidence_kinds:
            return self._result(
                requirement,
                GovernedScientificEvidenceSourceDiscriminationStatus.NOT_SUPPORTED,
                rationale_codes=("scientific_evidence_source_need_not_supported",),
            )

        eligible_ids = self._eligible_source_ids(
            registered_sources,
            request=request,
            evidence_kinds=evidence_kinds,
        )
        if not eligible_ids:
            return self._result(
                requirement,
                GovernedScientificEvidenceSourceDiscriminationStatus.UNAVAILABLE,
                accepted_evidence_kinds=evidence_kinds,
                rationale_codes=("no_registered_governed_source_matches_need",),
            )

        selection = self.selector.select(
            request,
            registered_sources=eligible_ids,
        )
        if selection.status is not GovernedConversationalSourceSelectionStatus.SELECTED:
            return self._result(
                requirement,
                GovernedScientificEvidenceSourceDiscriminationStatus.UNAVAILABLE,
                eligible_source_ids=eligible_ids,
                accepted_evidence_kinds=evidence_kinds,
                rationale_codes=("governed_source_selector_found_no_source",),
            )
        return self._result(
            requirement,
            GovernedScientificEvidenceSourceDiscriminationStatus.SELECTED,
            selection=selection,
            eligible_source_ids=eligible_ids,
            accepted_evidence_kinds=evidence_kinds,
            rationale_codes=(
                "existing_registered_governed_source_selected",
                "source_selection_stops_before_retrieval",
                "source_selection_does_not_establish_truth_or_sufficiency",
            ),
        )

    def _eligible_source_ids(
        self,
        registered_sources: Iterable[str],
        *,
        request: GovernedConversationalSourceSelectionRequest,
        evidence_kinds: tuple[InformationEvidenceKind, ...],
    ) -> tuple[str, ...]:
        eligible: list[GovernedInformationSource] = []
        seen: set[str] = set()
        for source_id in registered_sources:
            normalized = source_id.strip().casefold()
            if not normalized or normalized in seen:
                continue
            seen.add(normalized)
            try:
                source = self.sources.source_for(normalized)
            except KeyError:
                continue
            if not self._is_scientific_or_official_candidate(
                source,
                request=request,
                evidence_kinds=evidence_kinds,
            ):
                continue
            eligible.append(source)
        return tuple(source.source_id for source in eligible)

    @staticmethod
    def _is_scientific_or_official_candidate(
        source: GovernedInformationSource,
        *,
        request: GovernedConversationalSourceSelectionRequest,
        evidence_kinds: tuple[InformationEvidenceKind, ...],
    ) -> bool:
        if source.status is not InformationSourceStatus.DECLARED:
            return False
        if source.kind not in {
            InformationSourceKind.OFFICIAL,
            InformationSourceKind.PUBLIC_INSTITUTION,
        }:
            return False
        if source.classification.evidence not in evidence_kinds:
            return False
        return request.topics.issubset(source.topics)

    @classmethod
    def _evidence_kinds_for(
        cls,
        requirement: DiscriminatingEvidenceRequirement,
    ) -> tuple[InformationEvidenceKind, ...]:
        tokens = cls._requirement_tokens(requirement)
        kinds: list[InformationEvidenceKind] = []
        if tokens.intersection(cls._SCIENTIFIC_MARKERS):
            kinds.append(InformationEvidenceKind.SCIENTIFIC_GUIDANCE)
        if tokens.intersection(cls._OFFICIAL_MARKERS):
            kinds.extend(
                (
                    InformationEvidenceKind.OFFICIAL_RECORD,
                    InformationEvidenceKind.OFFICIAL_ANNOUNCEMENT,
                )
            )
        return tuple(dict.fromkeys(kinds))

    @staticmethod
    def _requirement_tokens(
        requirement: DiscriminatingEvidenceRequirement,
    ) -> frozenset[str]:
        values = (
            *requirement.missing_evidence_descriptions,
            *requirement.evidence_codes,
        )
        normalized = " ".join(values).casefold()
        for separator in ("-", "_", "/", ":", ",", ".", ";"):
            normalized = normalized.replace(separator, " ")
        return frozenset(normalized.split())

    @staticmethod
    def _result(
        requirement: DiscriminatingEvidenceRequirement,
        status: GovernedScientificEvidenceSourceDiscriminationStatus,
        *,
        selection: GovernedConversationalSourceSelection | None = None,
        eligible_source_ids: tuple[str, ...] = (),
        accepted_evidence_kinds: tuple[InformationEvidenceKind, ...] = (),
        rationale_codes: tuple[str, ...],
    ) -> GovernedScientificEvidenceSourceDiscriminationResult:
        return GovernedScientificEvidenceSourceDiscriminationResult(
            status=status,
            requirement_id=requirement.requirement_id,
            selection=selection,
            eligible_source_ids=eligible_source_ids,
            accepted_evidence_kinds=accepted_evidence_kinds,
            rationale_codes=rationale_codes,
        )
