from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256

from core.governed_reasoning.multistage_causal_path import (
    GovernedMultiStageCausalPath,
    MultiStageCausalPathStatus,
)


class CounterfactualPathComparisonStatus(StrEnum):
    COMPARISON_CANDIDATE = "comparison_candidate"
    INSUFFICIENT_PATHS = "insufficient_paths"
    LINEAGE_MISMATCH = "lineage_mismatch"
    PATH_REVIEW_REQUIRED = "path_review_required"
    NO_DIVERGENCE = "no_divergence"


@dataclass(frozen=True)
class CounterfactualPathDivergence:
    stage_index: int
    path_projections: tuple[tuple[str, str, str, str], ...]
    rationale_codes: tuple[str, ...]
    establishes_preference: bool = False
    establishes_truth: bool = False

    def __post_init__(self) -> None:
        if self.stage_index < 1:
            raise ValueError("counterfactual divergence stage must be positive")
        if self.establishes_preference or self.establishes_truth:
            raise ValueError("counterfactual divergence is consultative only")


@dataclass(frozen=True)
class GovernedCounterfactualPathComparison:
    comparison_id: str
    owner: str
    session_id: str
    baseline_snapshot_id: str
    path_ids: tuple[str, ...]
    relation_lineage: tuple[tuple[str, tuple[str, ...]], ...]
    divergences: tuple[CounterfactualPathDivergence, ...]
    status: CounterfactualPathComparisonStatus
    rationale_codes: tuple[str, ...]
    risk_codes: tuple[str, ...]
    source_fingerprint: str
    schema_version: str = "cap-06-counterfactual-path-comparison-v1"
    canonical_authority: str = "governed_reasoning"
    read_only: bool = True
    consultative: bool = True
    establishes_truth: bool = False
    establishes_causality: bool = False
    establishes_preference: bool = False
    selects_winner: bool = False
    calibrates_probability: bool = False
    persists_results: bool = False
    modifies_world_model: bool = False
    modifies_memory: bool = False
    modifies_learning: bool = False
    modifies_planning: bool = False
    registers_rule: bool = False
    executes_transfer: bool = False
    executes_actions: bool = False
    grants_authority: bool = False

    def __post_init__(self) -> None:
        if not self.comparison_id.startswith("counterfactual-path-comparison-"):
            raise ValueError("counterfactual path comparison identifier is invalid")
        if self.canonical_authority != "governed_reasoning":
            raise ValueError("counterfactual comparison must preserve authority")
        if not self.read_only or not self.consultative or any(
            (
                self.establishes_truth,
                self.establishes_causality,
                self.establishes_preference,
                self.selects_winner,
                self.calibrates_probability,
                self.persists_results,
                self.modifies_world_model,
                self.modifies_memory,
                self.modifies_learning,
                self.modifies_planning,
                self.registers_rule,
                self.executes_transfer,
                self.executes_actions,
                self.grants_authority,
            )
        ):
            raise ValueError("counterfactual comparison violates governed limits")


class GovernedCounterfactualPathComparator:
    """Compare explicit governed causal paths without selecting a true path."""

    CANONICAL_AUTHORITY = "governed_reasoning"

    def compare(
        self,
        paths: tuple[GovernedMultiStageCausalPath, ...],
    ) -> GovernedCounterfactualPathComparison:
        ordered = tuple(sorted(paths, key=lambda item: item.path_id))
        if len(ordered) < 2 or len({item.path_id for item in ordered}) < 2:
            return self._result(
                ordered,
                CounterfactualPathComparisonStatus.INSUFFICIENT_PATHS,
                (),
                ("counterfactual:at_least_two_distinct_paths_required",),
            )
        owner_keys = {item.owner.strip().casefold() for item in ordered}
        sessions = {item.session_id for item in ordered}
        baselines = {item.baseline_snapshot_id for item in ordered}
        if len(owner_keys) != 1 or len(sessions) != 1 or len(baselines) != 1:
            return self._result(
                ordered,
                CounterfactualPathComparisonStatus.LINEAGE_MISMATCH,
                (),
                ("counterfactual:shared_owner_session_baseline_required",),
            )
        if any(
            item.status is not MultiStageCausalPathStatus.PATH_CANDIDATE
            for item in ordered
        ):
            return self._result(
                ordered,
                CounterfactualPathComparisonStatus.PATH_REVIEW_REQUIRED,
                (),
                ("counterfactual:all_paths_must_be_governed_candidates",),
            )

        divergences = []
        max_stages = max(len(item.stages) for item in ordered)
        for index in range(max_stages):
            projections = []
            for path in ordered:
                if index >= len(path.stages):
                    projections.append(
                        (path.path_id, "<absent>", "<absent>", "<absent>")
                    )
                    continue
                stage = path.stages[index]
                projections.append(
                    (
                        path.path_id,
                        stage.effect_domain,
                        stage.effect_key,
                        stage.effect_value,
                    )
                )
            semantic = {
                tuple(value.strip().casefold() for value in item[1:])
                for item in projections
            }
            if len(semantic) > 1:
                divergences.append(
                    CounterfactualPathDivergence(
                        stage_index=index + 1,
                        path_projections=tuple(projections),
                        rationale_codes=(
                            "counterfactual:explicit_projection_divergence",
                            "counterfactual:no_true_path_selected",
                        ),
                    )
                )

        status = (
            CounterfactualPathComparisonStatus.COMPARISON_CANDIDATE
            if divergences
            else CounterfactualPathComparisonStatus.NO_DIVERGENCE
        )
        return self._result(
            ordered,
            status,
            tuple(divergences),
            (
                "counterfactual:shared_factual_baseline_preserved",
                "counterfactual:alternative_paths_remain_hypothetical",
            ),
        )

    @staticmethod
    def _result(
        paths: tuple[GovernedMultiStageCausalPath, ...],
        status: CounterfactualPathComparisonStatus,
        divergences: tuple[CounterfactualPathDivergence, ...],
        rationale_codes: tuple[str, ...],
    ) -> GovernedCounterfactualPathComparison:
        owner = paths[0].owner if paths else "unknown"
        session_id = paths[0].session_id if paths else "unknown"
        baseline = paths[0].baseline_snapshot_id if paths else "unknown"
        path_ids = tuple(item.path_id for item in paths)
        lineage = tuple((item.path_id, item.relation_ids) for item in paths)
        fingerprint = sha256(
            repr(
                (
                    owner.casefold(),
                    session_id,
                    baseline,
                    path_ids,
                    lineage,
                    tuple(
                        (
                            item.stage_index,
                            item.path_projections,
                        )
                        for item in divergences
                    ),
                    status.value,
                )
            ).encode("utf-8")
        ).hexdigest()
        return GovernedCounterfactualPathComparison(
            comparison_id=f"counterfactual-path-comparison-{fingerprint[:24]}",
            owner=owner,
            session_id=session_id,
            baseline_snapshot_id=baseline,
            path_ids=path_ids,
            relation_lineage=lineage,
            divergences=divergences,
            status=status,
            rationale_codes=rationale_codes,
            risk_codes=(
                "counterfactual_does_not_establish_truth",
                "counterfactual_does_not_establish_causality",
                "counterfactual_does_not_select_action",
            ),
            source_fingerprint=fingerprint,
        )
