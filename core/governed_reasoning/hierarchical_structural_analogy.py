from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256

from .hierarchical_concept_composition import (
    CanonicalProductiveConceptEpisode,
    HierarchicalConceptComponent,
    HierarchicalConceptRelation,
)

_SCHEMA_VERSION = "cap-08-hierarchical-structural-analogy-v1"


class HierarchicalStructuralAnalogyStatus(StrEnum):
    ANALOGY_CANDIDATE = "analogy_candidate"
    NO_ANALOGY = "no_analogy"
    SCOPE_MISMATCH = "scope_mismatch"
    INSUFFICIENT_STRUCTURE = "insufficient_structure"
    AMBIGUOUS = "ambiguous"


@dataclass(frozen=True)
class HierarchicalConceptComponentCorrespondence:
    source_component_id: str
    target_component_id: str
    relation: str
    outcome: str

    def __post_init__(self) -> None:
        required = (
            self.source_component_id,
            self.target_component_id,
            self.relation,
            self.outcome,
        )
        if any(not item.strip() for item in required):
            raise ValueError("hierarchical analogy correspondence requires lineage")


@dataclass(frozen=True)
class GovernedHierarchicalStructuralAnalogyCandidate:
    status: HierarchicalStructuralAnalogyStatus
    scope_reference: str
    source_concept_episode_id: str
    target_concept_episode_id: str
    component_correspondences: tuple[HierarchicalConceptComponentCorrespondence, ...]
    matched_link_relations: tuple[HierarchicalConceptRelation, ...]
    rationale_codes: tuple[str, ...]
    source_fingerprint: str
    schema_version: str = _SCHEMA_VERSION
    canonical_authority: str = "governed_reasoning"
    read_only: bool = True
    session_local: bool = True
    persists: bool = False
    creates_memory: bool = False
    creates_learning: bool = False
    modifies_world_model: bool = False
    establishes_truth: bool = False
    authorizes_inference: bool = False
    executes_transfer: bool = False
    registers_rule: bool = False
    executes_actions: bool = False
    grants_authority: bool = False

    def __post_init__(self) -> None:
        required = (
            self.scope_reference,
            self.source_concept_episode_id,
            self.target_concept_episode_id,
            self.source_fingerprint,
        )
        if any(not item.strip() for item in required):
            raise ValueError("hierarchical analogy requires exact lineage")
        if not self.rationale_codes:
            raise ValueError("hierarchical analogy requires rationale")
        if self.canonical_authority != "governed_reasoning":
            raise ValueError("hierarchical analogy authority mismatch")
        if any(
            (
                not self.read_only,
                not self.session_local,
                self.persists,
                self.creates_memory,
                self.creates_learning,
                self.modifies_world_model,
                self.establishes_truth,
                self.authorizes_inference,
                self.executes_transfer,
                self.registers_rule,
                self.executes_actions,
                self.grants_authority,
            )
        ):
            raise ValueError("hierarchical analogy violates governed limits")
        if (
            self.status is HierarchicalStructuralAnalogyStatus.ANALOGY_CANDIDATE
            and len(self.component_correspondences) < 2
        ):
            raise ValueError("hierarchical analogy requires multiple components")


class GovernedHierarchicalStructuralAnalogyMatcher:
    """Compare two governed HCC episodes without applying structural transfer."""

    MINIMUM_COMPONENTS = 2

    def match(
        self,
        *,
        source: CanonicalProductiveConceptEpisode,
        target: CanonicalProductiveConceptEpisode,
        scope_reference: str,
    ) -> GovernedHierarchicalStructuralAnalogyCandidate:
        if not scope_reference.strip():
            raise ValueError("hierarchical analogy requires scope")
        if source.episode_id == target.episode_id:
            return self._result(
                source=source,
                target=target,
                scope_reference=scope_reference,
                status=HierarchicalStructuralAnalogyStatus.NO_ANALOGY,
                rationale_codes=("hierarchical_analogy:same_episode",),
            )
        if (
            source.scope_reference != scope_reference
            or target.scope_reference != scope_reference
        ):
            return self._result(
                source=source,
                target=target,
                scope_reference=scope_reference,
                status=HierarchicalStructuralAnalogyStatus.SCOPE_MISMATCH,
                rationale_codes=("hierarchical_analogy:scope_mismatch",),
            )

        source_components = self._component_index(source)
        target_components = self._component_index(target)
        if (
            len(source_components) < self.MINIMUM_COMPONENTS
            or len(target_components) < self.MINIMUM_COMPONENTS
        ):
            return self._result(
                source=source,
                target=target,
                scope_reference=scope_reference,
                status=HierarchicalStructuralAnalogyStatus.INSUFFICIENT_STRUCTURE,
                rationale_codes=("hierarchical_analogy:multiple_components_required",),
            )
        if set(source_components) != set(target_components):
            return self._result(
                source=source,
                target=target,
                scope_reference=scope_reference,
                status=HierarchicalStructuralAnalogyStatus.NO_ANALOGY,
                rationale_codes=("hierarchical_analogy:component_topology_mismatch",),
            )

        correspondences = tuple(
            HierarchicalConceptComponentCorrespondence(
                source_component_id=source_components[key].component_id,
                target_component_id=target_components[key].component_id,
                relation=key[0],
                outcome=key[1],
            )
            for key in sorted(source_components)
        )
        source_links = self._link_signature(source, source_components)
        target_links = self._link_signature(target, target_components)
        if source_links != target_links:
            return self._result(
                source=source,
                target=target,
                scope_reference=scope_reference,
                status=HierarchicalStructuralAnalogyStatus.NO_ANALOGY,
                rationale_codes=("hierarchical_analogy:link_topology_mismatch",),
            )
        return self._result(
            source=source,
            target=target,
            scope_reference=scope_reference,
            status=HierarchicalStructuralAnalogyStatus.ANALOGY_CANDIDATE,
            correspondences=correspondences,
            matched_link_relations=tuple(item[2] for item in source_links),
            rationale_codes=(
                "hierarchical_analogy:hcc_component_structure_match",
                "hierarchical_analogy:hcc_link_structure_match",
                "hierarchical_analogy:candidate_only_non_authoritative",
                "hierarchical_analogy:not_structural_transfer_execution",
            ),
        )

    @staticmethod
    def _component_index(
        episode: CanonicalProductiveConceptEpisode,
    ) -> dict[tuple[str, str], HierarchicalConceptComponent]:
        result: dict[tuple[str, str], HierarchicalConceptComponent] = {}
        for component in episode.concept_candidate.components:
            key = (component.relation, component.outcome)
            if key in result:
                return {}
            result[key] = component
        return result

    @staticmethod
    def _link_signature(
        episode: CanonicalProductiveConceptEpisode,
        components: dict[tuple[str, str], HierarchicalConceptComponent],
    ) -> tuple[
        tuple[tuple[str, str], tuple[str, str], HierarchicalConceptRelation],
        ...,
    ]:
        by_id = {item.component_id: key for key, item in components.items()}
        signature = []
        for link in episode.concept_candidate.links:
            source_key = by_id.get(link.source_component_id)
            target_key = by_id.get(link.target_component_id)
            if source_key is None or target_key is None:
                return ()
            signature.append((source_key, target_key, link.relation))
        return tuple(
            sorted(
                signature,
                key=lambda item: (item[0], item[1], item[2].value),
            )
        )

    @staticmethod
    def _result(
        *,
        source: CanonicalProductiveConceptEpisode,
        target: CanonicalProductiveConceptEpisode,
        scope_reference: str,
        status: HierarchicalStructuralAnalogyStatus,
        rationale_codes: tuple[str, ...],
        correspondences: tuple[HierarchicalConceptComponentCorrespondence, ...] = (),
        matched_link_relations: tuple[HierarchicalConceptRelation, ...] = (),
    ) -> GovernedHierarchicalStructuralAnalogyCandidate:
        payload = repr(
            (
                _SCHEMA_VERSION,
                status.value,
                scope_reference,
                source.episode_id,
                target.episode_id,
                source.source_fingerprint,
                target.source_fingerprint,
                correspondences,
                tuple(item.value for item in matched_link_relations),
                rationale_codes,
            )
        )
        return GovernedHierarchicalStructuralAnalogyCandidate(
            status=status,
            scope_reference=scope_reference,
            source_concept_episode_id=source.episode_id,
            target_concept_episode_id=target.episode_id,
            component_correspondences=correspondences,
            matched_link_relations=matched_link_relations,
            rationale_codes=rationale_codes,
            source_fingerprint=sha256(payload.encode("utf-8")).hexdigest(),
        )
