from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256

from .hierarchical_concept_composition import CanonicalProductiveConceptEpisode

_SCHEMA_VERSION = "cap-19-cross-domain-concept-synthesis-v1"


class CrossDomainConceptSynthesisStatus(StrEnum):
    SYNTHESIS_CANDIDATE = "synthesis_candidate"
    SAME_DOMAIN = "same_domain"
    INSUFFICIENT_STRUCTURE = "insufficient_structure"
    NO_STRUCTURAL_CORRESPONDENCE = "no_structural_correspondence"
    LINEAGE_MISMATCH = "lineage_mismatch"


@dataclass(frozen=True)
class CrossDomainConceptSource:
    domain_reference: str
    concept_episode: CanonicalProductiveConceptEpisode

    def __post_init__(self) -> None:
        if not self.domain_reference.strip():
            raise ValueError("cross-domain concept source requires domain provenance")


@dataclass(frozen=True)
class CrossDomainConceptCorrespondence:
    source_component_id: str
    target_component_id: str
    relation: str
    outcome: str

    def __post_init__(self) -> None:
        if any(
            not item.strip()
            for item in (
                self.source_component_id,
                self.target_component_id,
                self.relation,
                self.outcome,
            )
        ):
            raise ValueError("cross-domain correspondence requires complete lineage")


@dataclass(frozen=True)
class GovernedCrossDomainConceptSynthesisCandidate:
    status: CrossDomainConceptSynthesisStatus
    source_domain_reference: str
    target_domain_reference: str
    source_scope_reference: str
    target_scope_reference: str
    source_concept_episode_id: str
    target_concept_episode_id: str
    correspondences: tuple[CrossDomainConceptCorrespondence, ...]
    rationale_codes: tuple[str, ...]
    source_fingerprint: str
    schema_version: str = _SCHEMA_VERSION
    canonical_authority: str = "governed_reasoning"
    read_only: bool = True
    session_local: bool = True
    persists: bool = False
    establishes_truth: bool = False
    establishes_causality: bool = False
    authorizes_inference: bool = False
    creates_memory: bool = False
    creates_learning: bool = False
    modifies_world_model: bool = False
    executes_transfer: bool = False
    registers_rule: bool = False
    executes_actions: bool = False
    grants_authority: bool = False

    def __post_init__(self) -> None:
        required = (
            self.source_domain_reference,
            self.target_domain_reference,
            self.source_scope_reference,
            self.target_scope_reference,
            self.source_concept_episode_id,
            self.target_concept_episode_id,
            self.source_fingerprint,
        )
        if any(not item.strip() for item in required):
            raise ValueError("cross-domain synthesis requires exact provenance")
        if not self.rationale_codes:
            raise ValueError("cross-domain synthesis requires rationale")
        if self.canonical_authority != "governed_reasoning":
            raise ValueError("cross-domain synthesis authority mismatch")
        if any(
            (
                not self.read_only,
                not self.session_local,
                self.persists,
                self.establishes_truth,
                self.establishes_causality,
                self.authorizes_inference,
                self.creates_memory,
                self.creates_learning,
                self.modifies_world_model,
                self.executes_transfer,
                self.registers_rule,
                self.executes_actions,
                self.grants_authority,
            )
        ):
            raise ValueError("cross-domain synthesis violates governed limits")
        if (
            self.status is CrossDomainConceptSynthesisStatus.SYNTHESIS_CANDIDATE
            and len(self.correspondences) < 2
        ):
            raise ValueError("cross-domain synthesis requires multiple correspondences")


class GovernedCrossDomainConceptSynthesizer:
    """Compare governed concepts across explicit domains without transfer."""

    MINIMUM_COMPONENTS = 2

    def synthesize(
        self,
        *,
        source: CrossDomainConceptSource,
        target: CrossDomainConceptSource,
    ) -> GovernedCrossDomainConceptSynthesisCandidate:
        source_episode = source.concept_episode
        target_episode = target.concept_episode
        if source_episode.owner.casefold() != target_episode.owner.casefold() or (
            source_episode.session_id != target_episode.session_id
        ):
            return self._result(
                source=source,
                target=target,
                status=CrossDomainConceptSynthesisStatus.LINEAGE_MISMATCH,
                rationale=("cross_domain_synthesis:owner_or_session_mismatch",),
            )
        if source.domain_reference.casefold() == target.domain_reference.casefold():
            return self._result(
                source=source,
                target=target,
                status=CrossDomainConceptSynthesisStatus.SAME_DOMAIN,
                rationale=("cross_domain_synthesis:distinct_domains_required",),
            )
        source_index = self._component_index(source_episode)
        target_index = self._component_index(target_episode)
        if (
            len(source_index) < self.MINIMUM_COMPONENTS
            or len(target_index) < self.MINIMUM_COMPONENTS
        ):
            return self._result(
                source=source,
                target=target,
                status=CrossDomainConceptSynthesisStatus.INSUFFICIENT_STRUCTURE,
                rationale=("cross_domain_synthesis:multiple_components_required",),
            )
        if set(source_index) != set(target_index):
            return self._result(
                source=source,
                target=target,
                status=CrossDomainConceptSynthesisStatus.NO_STRUCTURAL_CORRESPONDENCE,
                rationale=("cross_domain_synthesis:component_structure_mismatch",),
            )
        if self._link_signature(source_episode) != self._link_signature(target_episode):
            return self._result(
                source=source,
                target=target,
                status=CrossDomainConceptSynthesisStatus.NO_STRUCTURAL_CORRESPONDENCE,
                rationale=("cross_domain_synthesis:link_structure_mismatch",),
            )
        correspondences = tuple(
            CrossDomainConceptCorrespondence(
                source_component_id=source_index[key].component_id,
                target_component_id=target_index[key].component_id,
                relation=key[0],
                outcome=key[1],
            )
            for key in sorted(source_index)
        )
        return self._result(
            source=source,
            target=target,
            status=CrossDomainConceptSynthesisStatus.SYNTHESIS_CANDIDATE,
            rationale=(
                "cross_domain_synthesis:explicit_distinct_domain_provenance",
                "cross_domain_synthesis:hcc_structure_correspondence",
                "cross_domain_synthesis:candidate_only_non_authoritative",
            ),
            correspondences=correspondences,
        )

    @staticmethod
    def _component_index(episode: CanonicalProductiveConceptEpisode) -> dict:
        return {
            (component.relation, component.outcome): component
            for component in episode.concept_candidate.components
        }

    @staticmethod
    def _link_signature(episode: CanonicalProductiveConceptEpisode) -> tuple:
        by_id = {
            component.component_id: (component.relation, component.outcome)
            for component in episode.concept_candidate.components
        }
        return tuple(
            sorted(
                (
                    by_id[link.source_component_id],
                    by_id[link.target_component_id],
                    link.relation.value,
                )
                for link in episode.concept_candidate.links
            )
        )

    def _result(
        self,
        *,
        source: CrossDomainConceptSource,
        target: CrossDomainConceptSource,
        status: CrossDomainConceptSynthesisStatus,
        rationale: tuple[str, ...],
        correspondences: tuple[CrossDomainConceptCorrespondence, ...] = (),
    ) -> GovernedCrossDomainConceptSynthesisCandidate:
        source_episode = source.concept_episode
        target_episode = target.concept_episode
        fingerprint = sha256(
            repr(
                (
                    source.domain_reference.casefold(),
                    target.domain_reference.casefold(),
                    source_episode.episode_id,
                    target_episode.episode_id,
                    source_episode.scope_reference,
                    target_episode.scope_reference,
                    status.value,
                    tuple(
                        (
                            item.source_component_id,
                            item.target_component_id,
                            item.relation,
                            item.outcome,
                        )
                        for item in correspondences
                    ),
                    rationale,
                )
            ).encode("utf-8")
        ).hexdigest()
        return GovernedCrossDomainConceptSynthesisCandidate(
            status=status,
            source_domain_reference=source.domain_reference,
            target_domain_reference=target.domain_reference,
            source_scope_reference=source_episode.scope_reference,
            target_scope_reference=target_episode.scope_reference,
            source_concept_episode_id=source_episode.episode_id,
            target_concept_episode_id=target_episode.episode_id,
            correspondences=correspondences,
            rationale_codes=rationale,
            source_fingerprint=fingerprint,
        )
