from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256

from .productive_abstraction_admission import CanonicalProductiveAbstractionEpisode
from .relational_abstraction import RelationalAbstractionStatus

_SCHEMA_VERSION = "hcc-governed-hierarchical-concept-v1"


class HierarchicalConceptCompositionStatus(StrEnum):
    INSUFFICIENT_COMPONENTS = "insufficient_components"
    SCOPE_MISMATCH = "scope_mismatch"
    NOT_COMPOSABLE = "not_composable"
    REVIEW_REQUIRED = "review_required"
    CONTESTED = "contested"
    ABSTAIN = "abstain"


class HierarchicalConceptRelation(StrEnum):
    PARENT_OF = "parent_of"
    CHILD_OF = "child_of"
    CONTAINS_COMPONENT = "contains_component"
    RELATED_COMPONENT = "related_component"


@dataclass(frozen=True)
class HierarchicalConceptComponent:
    component_id: str
    abstraction_episode_id: str
    abstraction_fingerprint: str
    relation: str
    outcome: str
    status: RelationalAbstractionStatus
    supporting_example_ids: tuple[str, ...]
    counterexample_ids: tuple[str, ...]
    rationale_codes: tuple[str, ...]

    def __post_init__(self) -> None:
        required = (
            self.component_id,
            self.abstraction_episode_id,
            self.abstraction_fingerprint,
            self.relation,
            self.outcome,
        )
        if any(not value.strip() for value in required):
            raise ValueError("hierarchical concept component requires complete lineage")
        if not self.supporting_example_ids:
            raise ValueError("hierarchical concept component requires support")
        if not self.rationale_codes:
            raise ValueError("hierarchical concept component requires rationale")


@dataclass(frozen=True)
class HierarchicalConceptLink:
    source_component_id: str
    target_component_id: str
    relation: HierarchicalConceptRelation

    def __post_init__(self) -> None:
        if not self.source_component_id.strip() or not self.target_component_id.strip():
            raise ValueError("hierarchical concept link requires component ids")
        if self.source_component_id == self.target_component_id:
            raise ValueError("hierarchical concept link cannot self-reference")


@dataclass(frozen=True)
class GovernedHierarchicalConceptCandidate:
    concept_id: str
    scope_reference: str
    components: tuple[HierarchicalConceptComponent, ...]
    links: tuple[HierarchicalConceptLink, ...]
    parent_concept_reference: str | None
    child_concept_references: tuple[str, ...]
    status: HierarchicalConceptCompositionStatus
    rationale_codes: tuple[str, ...]
    constituent_episode_ids: tuple[str, ...]
    constituent_fingerprints: tuple[str, ...]
    source_fingerprint: str
    schema_version: str = _SCHEMA_VERSION
    canonical_authority: str = "governed_reasoning"
    read_only: bool = True
    session_local: bool = True
    persists: bool = False
    creates_memory: bool = False
    creates_learning: bool = False
    modifies_world_model: bool = False
    modifies_personal_knowledge: bool = False
    executes_transfer: bool = False
    registers_rule: bool = False
    executes_actions: bool = False
    grants_authority: bool = False

    def __post_init__(self) -> None:
        if not self.concept_id.strip() or not self.scope_reference.strip():
            raise ValueError(
                "hierarchical concept candidate requires identity and scope"
            )
        if not self.rationale_codes or not self.source_fingerprint.strip():
            raise ValueError(
                "hierarchical concept candidate requires rationale/provenance"
            )
        if self.canonical_authority != "governed_reasoning":
            raise ValueError("hierarchical concept must preserve reasoning authority")
        if any(
            (
                not self.read_only,
                not self.session_local,
                self.persists,
                self.creates_memory,
                self.creates_learning,
                self.modifies_world_model,
                self.modifies_personal_knowledge,
                self.executes_transfer,
                self.registers_rule,
                self.executes_actions,
                self.grants_authority,
            )
        ):
            raise ValueError("hierarchical concept violates governed limits")
        if (
            self.status
            in {
                HierarchicalConceptCompositionStatus.REVIEW_REQUIRED,
                HierarchicalConceptCompositionStatus.CONTESTED,
            }
            and len(self.components) < 2
        ):
            raise ValueError("reviewable hierarchical concept requires components")


@dataclass(frozen=True)
class CanonicalProductiveConceptEpisode:
    episode_id: str
    owner: str
    session_id: str
    turn_id: str
    scope_reference: str
    concept_candidate: GovernedHierarchicalConceptCandidate
    source_abstraction_episode_ids: tuple[str, ...]
    source_fingerprint: str
    schema_version: str = _SCHEMA_VERSION
    canonical_authority: str = "governed_reasoning"
    read_only: bool = True
    session_local: bool = True
    persists: bool = False
    creates_memory: bool = False
    creates_learning: bool = False
    modifies_world_model: bool = False
    modifies_personal_knowledge: bool = False
    executes_transfer: bool = False
    registers_rule: bool = False
    executes_actions: bool = False
    grants_authority: bool = False

    def __post_init__(self) -> None:
        required = (
            self.episode_id,
            self.owner,
            self.session_id,
            self.turn_id,
            self.scope_reference,
            self.source_fingerprint,
        )
        if any(not value.strip() for value in required):
            raise ValueError("productive concept episode requires exact lineage")
        if len(self.source_abstraction_episode_ids) < 2:
            raise ValueError(
                "productive concept episode requires multiple abstractions"
            )
        if self.concept_candidate.scope_reference != self.scope_reference:
            raise ValueError("productive concept episode scope mismatch")
        if self.concept_candidate.constituent_episode_ids != (
            self.source_abstraction_episode_ids
        ):
            raise ValueError("productive concept episode lineage mismatch")
        if self.canonical_authority != "governed_reasoning":
            raise ValueError("productive concept episode authority mismatch")
        if any(
            (
                not self.read_only,
                not self.session_local,
                self.persists,
                self.creates_memory,
                self.creates_learning,
                self.modifies_world_model,
                self.modifies_personal_knowledge,
                self.executes_transfer,
                self.registers_rule,
                self.executes_actions,
                self.grants_authority,
            )
        ):
            raise ValueError("productive concept episode violates governed limits")


class GovernedHierarchicalConceptComposer:
    """Compose canonical relational-abstraction episodes into one bounded concept."""

    MINIMUM_COMPONENTS = 2

    def compose(
        self,
        *,
        episodes: tuple[CanonicalProductiveAbstractionEpisode, ...],
        scope_reference: str,
        links: tuple[HierarchicalConceptLink, ...] = (),
        parent_concept_reference: str | None = None,
        child_concept_references: tuple[str, ...] = (),
    ) -> GovernedHierarchicalConceptCandidate:
        if not scope_reference.strip():
            raise ValueError("hierarchical concept composition requires scope")

        ordered = tuple(sorted(episodes, key=lambda item: item.episode_id))
        unique_ids = tuple(item.episode_id for item in ordered)
        if len(unique_ids) != len(set(unique_ids)):
            return self._result(
                scope_reference=scope_reference,
                status=HierarchicalConceptCompositionStatus.NOT_COMPOSABLE,
                episodes=(),
                components=(),
                links=(),
                parent_concept_reference=None,
                child_concept_references=(),
                rationale_codes=("hcc:duplicate_episode",),
            )
        if len(ordered) < self.MINIMUM_COMPONENTS:
            return self._result(
                scope_reference=scope_reference,
                status=HierarchicalConceptCompositionStatus.INSUFFICIENT_COMPONENTS,
                episodes=ordered,
                components=(),
                links=(),
                parent_concept_reference=None,
                child_concept_references=(),
                rationale_codes=("hcc:multiple_abstraction_episodes_required",),
            )
        if any(item.scope_reference != scope_reference for item in ordered):
            return self._result(
                scope_reference=scope_reference,
                status=HierarchicalConceptCompositionStatus.SCOPE_MISMATCH,
                episodes=(),
                components=(),
                links=(),
                parent_concept_reference=None,
                child_concept_references=(),
                rationale_codes=("hcc:scope_mismatch",),
            )

        eligible = {
            RelationalAbstractionStatus.REVIEW_REQUIRED,
            RelationalAbstractionStatus.CONTESTED,
        }
        if any(item.abstraction_candidate.status not in eligible for item in ordered):
            return self._result(
                scope_reference=scope_reference,
                status=HierarchicalConceptCompositionStatus.ABSTAIN,
                episodes=ordered,
                components=(),
                links=(),
                parent_concept_reference=None,
                child_concept_references=(),
                rationale_codes=("hcc:non_reviewable_abstraction_component",),
            )

        components = tuple(self._component(item) for item in ordered)
        component_ids = {item.component_id for item in components}
        normalized_links = tuple(
            sorted(
                links,
                key=lambda item: (
                    item.source_component_id,
                    item.target_component_id,
                    item.relation.value,
                ),
            )
        )
        if any(
            item.source_component_id not in component_ids
            or item.target_component_id not in component_ids
            for item in normalized_links
        ):
            return self._result(
                scope_reference=scope_reference,
                status=HierarchicalConceptCompositionStatus.NOT_COMPOSABLE,
                episodes=ordered,
                components=components,
                links=(),
                parent_concept_reference=None,
                child_concept_references=(),
                rationale_codes=("hcc:link_component_missing",),
            )

        status = (
            HierarchicalConceptCompositionStatus.CONTESTED
            if any(
                item.status is RelationalAbstractionStatus.CONTESTED
                for item in components
            )
            else HierarchicalConceptCompositionStatus.REVIEW_REQUIRED
        )
        rationale = (
            "hcc:bounded_hierarchical_composition",
            (
                "hcc:component_counterevidence_preserved"
                if status is HierarchicalConceptCompositionStatus.CONTESTED
                else "hcc:all_components_reviewable"
            ),
        )
        return self._result(
            scope_reference=scope_reference,
            status=status,
            episodes=ordered,
            components=components,
            links=normalized_links,
            parent_concept_reference=(
                parent_concept_reference.strip() if parent_concept_reference else None
            ),
            child_concept_references=tuple(
                sorted(
                    {item.strip() for item in child_concept_references if item.strip()}
                )
            ),
            rationale_codes=rationale,
        )

    @staticmethod
    def _component(
        episode: CanonicalProductiveAbstractionEpisode,
    ) -> HierarchicalConceptComponent:
        candidate = episode.abstraction_candidate
        if not candidate.invariant_relation or not candidate.invariant_outcome:
            raise ValueError("hierarchical concept component requires full invariant")
        fingerprint = sha256(
            repr(
                (
                    episode.episode_id,
                    episode.source_fingerprint,
                    candidate.source_fingerprint,
                )
            ).encode("utf-8")
        ).hexdigest()
        return HierarchicalConceptComponent(
            component_id=f"hcc-component:{fingerprint[:16]}",
            abstraction_episode_id=episode.episode_id,
            abstraction_fingerprint=candidate.source_fingerprint,
            relation=candidate.invariant_relation,
            outcome=candidate.invariant_outcome,
            status=candidate.status,
            supporting_example_ids=candidate.supporting_example_ids,
            counterexample_ids=candidate.counterexample_ids,
            rationale_codes=candidate.rationale_codes,
        )

    @staticmethod
    def _result(
        *,
        scope_reference: str,
        status: HierarchicalConceptCompositionStatus,
        episodes: tuple[CanonicalProductiveAbstractionEpisode, ...],
        components: tuple[HierarchicalConceptComponent, ...],
        links: tuple[HierarchicalConceptLink, ...],
        parent_concept_reference: str | None,
        child_concept_references: tuple[str, ...],
        rationale_codes: tuple[str, ...],
    ) -> GovernedHierarchicalConceptCandidate:
        episode_ids = tuple(item.episode_id for item in episodes)
        fingerprints = tuple(item.source_fingerprint for item in episodes)
        source_fingerprint = sha256(
            repr(
                (
                    scope_reference,
                    status.value,
                    episode_ids,
                    fingerprints,
                    tuple(
                        (
                            item.component_id,
                            item.status.value,
                            item.counterexample_ids,
                        )
                        for item in components
                    ),
                    tuple(
                        (
                            item.source_component_id,
                            item.target_component_id,
                            item.relation.value,
                        )
                        for item in links
                    ),
                    parent_concept_reference,
                    child_concept_references,
                    rationale_codes,
                )
            ).encode("utf-8")
        ).hexdigest()
        return GovernedHierarchicalConceptCandidate(
            concept_id=f"governed-concept:{source_fingerprint[:16]}",
            scope_reference=scope_reference,
            components=components,
            links=links,
            parent_concept_reference=parent_concept_reference,
            child_concept_references=child_concept_references,
            status=status,
            rationale_codes=rationale_codes,
            constituent_episode_ids=episode_ids,
            constituent_fingerprints=fingerprints,
            source_fingerprint=source_fingerprint,
        )

class GovernedConstituentAbstractionReopener:
    """Resolve exact bounded abstraction lineage for one governed concept."""

    @staticmethod
    def reopen(
        *,
        concept_episode: CanonicalProductiveConceptEpisode,
        available_episodes: tuple[CanonicalProductiveAbstractionEpisode, ...],
    ) -> tuple[CanonicalProductiveAbstractionEpisode, ...]:
        if (
            concept_episode.canonical_authority != "governed_reasoning"
            or not concept_episode.read_only
            or not concept_episode.session_local
            or concept_episode.persists
        ):
            return ()

        by_id = {episode.episode_id: episode for episode in available_episodes}
        if len(by_id) != len(available_episodes):
            return ()

        ids = concept_episode.source_abstraction_episode_ids
        fingerprints = concept_episode.concept_candidate.constituent_fingerprints
        if len(ids) != len(fingerprints):
            return ()

        reopened = []
        for episode_id, fingerprint in zip(ids, fingerprints, strict=True):
            episode = by_id.get(episode_id)
            if (
                episode is None
                or episode.session_id != concept_episode.session_id
                or episode.scope_reference != concept_episode.scope_reference
                or episode.source_fingerprint != fingerprint
                or episode.canonical_authority != "governed_reasoning"
                or not episode.read_only
                or not episode.session_local
                or episode.persists
            ):
                return ()
            reopened.append(episode)
        return tuple(reopened)

