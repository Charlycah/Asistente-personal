from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256

from core.governed_decision_advisory import GovernedDecisionOption


class ComplexDecisionCriterionOutcome(StrEnum):
    FAVORABLE = "favorable"
    NEUTRAL = "neutral"
    UNFAVORABLE = "unfavorable"
    INSUFFICIENT = "insufficient"


class ComplexDecisionOptionStatus(StrEnum):
    ELIGIBLE = "eligible"
    BLOCKED = "blocked"
    REVIEW_REQUIRED = "review_required"


class ComplexDecisionReasoningStatus(StrEnum):
    COMPLETE = "complete"
    REVIEW_REQUIRED = "review_required"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"


@dataclass(frozen=True)
class GovernedDecisionCriterion:
    """Explicit decision criterion supplied to the governed decision authority."""

    criterion_id: str
    title: str
    required: bool = False
    explicit_importance: float | None = None
    provenance_codes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.criterion_id.strip():
            raise ValueError("decision criterion id must not be blank")
        if not self.title.strip():
            raise ValueError("decision criterion title must not be blank")
        if self.explicit_importance is not None and not 0.0 <= float(
            self.explicit_importance
        ) <= 1.0:
            raise ValueError("explicit criterion importance must be between 0 and 1")
        if not self.provenance_codes or any(
            not code.strip() for code in self.provenance_codes
        ):
            raise ValueError("decision criterion requires provenance codes")


@dataclass(frozen=True)
class GovernedOptionCriterionAssessment:
    """Explicit evidence for one option against one explicit criterion."""

    option_id: str
    criterion_id: str
    outcome: ComplexDecisionCriterionOutcome
    evidence_codes: tuple[str, ...]
    explicit_value: float | None = None
    source_fingerprint: str | None = None
    read_only: bool = True
    advisory_only: bool = True
    creates_facts: bool = False
    action_authorized: bool = False

    def __post_init__(self) -> None:
        if not self.option_id.strip() or not self.criterion_id.strip():
            raise ValueError("option criterion assessment requires explicit ids")
        if not isinstance(self.outcome, ComplexDecisionCriterionOutcome):
            raise ValueError("option criterion assessment outcome is invalid")
        if not self.evidence_codes or any(
            not code.strip() for code in self.evidence_codes
        ):
            raise ValueError("option criterion assessment requires evidence codes")
        if self.explicit_value is not None and not 0.0 <= float(
            self.explicit_value
        ) <= 1.0:
            raise ValueError("explicit criterion value must be between 0 and 1")
        if self.source_fingerprint is not None and not self.source_fingerprint.strip():
            raise ValueError("assessment source fingerprint must not be blank")
        if not self.read_only or not self.advisory_only:
            raise ValueError(
                "option criterion assessment must remain advisory and read-only"
            )
        if self.creates_facts or self.action_authorized:
            raise ValueError(
                "option criterion assessment cannot create facts or actions"
            )


@dataclass(frozen=True)
class GovernedComplexDecisionOptionAssessment:
    option_id: str
    status: ComplexDecisionOptionStatus
    criterion_assessments: tuple[GovernedOptionCriterionAssessment, ...]
    blocking_criterion_ids: tuple[str, ...]
    review_criterion_ids: tuple[str, ...]
    rationale_codes: tuple[str, ...]
    source_fingerprint: str
    action_authorized: bool = False

    def __post_init__(self) -> None:
        if not self.option_id.strip():
            raise ValueError("complex decision option assessment requires option id")
        if not self.criterion_assessments:
            raise ValueError("complex decision option assessment requires criteria")
        if not self.rationale_codes or any(
            not code.strip() for code in self.rationale_codes
        ):
            raise ValueError("complex decision option assessment requires rationale")
        criterion_ids = tuple(item.criterion_id for item in self.criterion_assessments)
        if len(criterion_ids) != len(set(criterion_ids)):
            raise ValueError("complex decision option criteria must be unique")
        if self.action_authorized:
            raise ValueError("complex decision reasoning cannot authorize action")


@dataclass(frozen=True)
class GovernedComplexDecisionReport:
    report_id: str
    status: ComplexDecisionReasoningStatus
    source_option_ids: tuple[str, ...]
    criteria: tuple[GovernedDecisionCriterion, ...]
    option_assessments: tuple[GovernedComplexDecisionOptionAssessment, ...]
    recommended_option_id: str | None
    tradeoff_codes: tuple[str, ...]
    rationale_codes: tuple[str, ...]
    source_fingerprint: str
    schema_version: str = "post-m409.1-governed-complex-decision-reasoning-v1"
    canonical_authority: str = "unified_cognitive_coordination"
    canonical_facade: str = "CanonicalDecisionFacade"
    read_only: bool = True
    advisory_only: bool = True
    derivational: bool = True
    human_decision_preserved: bool = True
    establishes_truth: bool = False
    assigns_probability: bool = False
    creates_facts: bool = False
    creates_plans: bool = False
    creates_tasks: bool = False
    persists_results: bool = False
    modifies_memory: bool = False
    modifies_learning: bool = False
    modifies_world_model: bool = False
    modifies_planning: bool = False
    modifies_organization: bool = False
    executes_actions: bool = False
    grants_authority: bool = False
    starts_background_process: bool = False

    def __post_init__(self) -> None:
        if not self.report_id.startswith("complex-decision-"):
            raise ValueError("complex decision report id is invalid")
        if self.canonical_authority != "unified_cognitive_coordination":
            raise ValueError("canonical decision authority must be preserved")
        if self.canonical_facade != "CanonicalDecisionFacade":
            raise ValueError("canonical decision facade must be preserved")
        if not self.source_option_ids:
            raise ValueError("complex decision report requires option lineage")
        if not self.criteria:
            raise ValueError("complex decision report requires criterion lineage")
        if not self.option_assessments:
            raise ValueError("complex decision report requires option assessments")
        option_ids = tuple(item.option_id for item in self.option_assessments)
        if tuple(sorted(self.source_option_ids)) != tuple(sorted(option_ids)):
            raise ValueError("complex decision report option lineage mismatch")
        criterion_ids = tuple(item.criterion_id for item in self.criteria)
        if len(criterion_ids) != len(set(criterion_ids)):
            raise ValueError("complex decision report criterion ids must be unique")
        if len(option_ids) != len(set(option_ids)):
            raise ValueError("complex decision option ids must be unique")
        if self.recommended_option_id is not None:
            if self.recommended_option_id not in option_ids:
                raise ValueError("recommended complex decision option must exist")
            selected = next(
                item
                for item in self.option_assessments
                if item.option_id == self.recommended_option_id
            )
            if selected.status is ComplexDecisionOptionStatus.BLOCKED:
                raise ValueError(
                    "recommended complex decision option cannot be blocked"
                )
            if (
                selected.status is ComplexDecisionOptionStatus.REVIEW_REQUIRED
                and "complex_decision:sole_required_constraint_survivor"
                not in self.rationale_codes
            ):
                raise ValueError(
                    "review-required recommendation needs required-survivor rationale"
                )
        if not self.rationale_codes or any(
            not code.strip() for code in self.rationale_codes
        ):
            raise ValueError("complex decision report requires rationale")
        if not self.source_fingerprint.strip():
            raise ValueError("complex decision report requires source fingerprint")
        if not self.read_only or not self.advisory_only or not self.derivational:
            raise ValueError(
                "complex decision reasoning must remain derived and read-only"
            )
        if not self.human_decision_preserved:
            raise ValueError("complex decision reasoning must preserve human decision")
        if any(
            (
                self.establishes_truth,
                self.assigns_probability,
                self.creates_facts,
                self.creates_plans,
                self.creates_tasks,
                self.persists_results,
                self.modifies_memory,
                self.modifies_learning,
                self.modifies_world_model,
                self.modifies_planning,
                self.modifies_organization,
                self.executes_actions,
                self.grants_authority,
                self.starts_background_process,
            )
        ):
            raise ValueError("complex decision reasoning violates governed limits")


class GovernedComplexDecisionReasoningFoundationV1:
    """Pure multicriterion reasoning subordinate to canonical decision authority."""

    CANONICAL_AUTHORITY = "unified_cognitive_coordination"
    CANONICAL_FACADE = "CanonicalDecisionFacade"

    def assess(
        self,
        options: tuple[GovernedDecisionOption, ...],
        criteria: tuple[GovernedDecisionCriterion, ...],
        assessments: tuple[GovernedOptionCriterionAssessment, ...],
    ) -> GovernedComplexDecisionReport:
        self._validate_inputs(options, criteria, assessments)
        ordered_options = tuple(sorted(options, key=lambda item: item.option_id))
        ordered_criteria = tuple(sorted(criteria, key=lambda item: item.criterion_id))
        by_pair = {(item.option_id, item.criterion_id): item for item in assessments}

        option_assessments = tuple(
            self._assess_option(option, ordered_criteria, by_pair)
            for option in ordered_options
        )
        eligible = tuple(
            item
            for item in option_assessments
            if item.status is ComplexDecisionOptionStatus.ELIGIBLE
        )
        required_survivor = self._sole_required_constraint_survivor(
            option_assessments,
            ordered_criteria,
        )
        if required_survivor is not None:
            recommended = required_survivor.option_id
            tradeoffs = ()
            selection_rationale = (
                "complex_decision:sole_required_constraint_survivor",
            )
        else:
            recommended, tradeoffs, selection_rationale = self._select(
                eligible,
                ordered_criteria,
            )
            if any(
                item.status is ComplexDecisionOptionStatus.REVIEW_REQUIRED
                for item in option_assessments
            ):
                recommended = None
                selection_rationale = selection_rationale + (
                    "complex_decision:"
                    "recommendation_withheld_for_incomplete_evidence",
                )
        status, status_rationale = self._status(
            option_assessments,
            recommended,
            required_survivor is not None,
        )
        rationale = tuple(sorted(set(status_rationale + selection_rationale)))
        fingerprint = self._fingerprint(
            ordered_options,
            ordered_criteria,
            tuple(
                sorted(
                    assessments,
                    key=lambda item: (item.option_id, item.criterion_id),
                )
            ),
            recommended,
            status,
            tradeoffs,
        )
        return GovernedComplexDecisionReport(
            report_id=f"complex-decision-{fingerprint[:16]}",
            status=status,
            source_option_ids=tuple(item.option_id for item in ordered_options),
            criteria=ordered_criteria,
            option_assessments=option_assessments,
            recommended_option_id=recommended,
            tradeoff_codes=tradeoffs,
            rationale_codes=rationale,
            source_fingerprint=fingerprint,
        )

    @classmethod
    def _validate_inputs(
        cls,
        options: tuple[GovernedDecisionOption, ...],
        criteria: tuple[GovernedDecisionCriterion, ...],
        assessments: tuple[GovernedOptionCriterionAssessment, ...],
    ) -> None:
        if not options:
            raise ValueError("complex decision reasoning requires explicit options")
        if not criteria:
            raise ValueError("complex decision reasoning requires explicit criteria")
        option_ids = tuple(item.option_id for item in options)
        criterion_ids = tuple(item.criterion_id for item in criteria)
        if len(option_ids) != len(set(option_ids)):
            raise ValueError("complex decision option ids must be unique")
        if len(criterion_ids) != len(set(criterion_ids)):
            raise ValueError("complex decision criterion ids must be unique")
        option_id_set = set(option_ids)
        criterion_id_set = set(criterion_ids)
        seen_pairs: set[tuple[str, str]] = set()
        for assessment in assessments:
            if assessment.option_id not in option_id_set:
                raise ValueError("criterion assessment references unknown option")
            if assessment.criterion_id not in criterion_id_set:
                raise ValueError("criterion assessment references unknown criterion")
            pair = (assessment.option_id, assessment.criterion_id)
            if pair in seen_pairs:
                raise ValueError("criterion assessment pairs must be unique")
            seen_pairs.add(pair)
        expected_pairs = {
            (option_id, criterion_id)
            for option_id in option_id_set
            for criterion_id in criterion_id_set
        }
        if seen_pairs != expected_pairs:
            raise ValueError(
                "complex decision reasoning requires complete option criterion evidence"
            )

    @classmethod
    def _assess_option(
        cls,
        option: GovernedDecisionOption,
        criteria: tuple[GovernedDecisionCriterion, ...],
        by_pair: dict[tuple[str, str], GovernedOptionCriterionAssessment],
    ) -> GovernedComplexDecisionOptionAssessment:
        items = tuple(
            by_pair[(option.option_id, criterion.criterion_id)]
            for criterion in criteria
        )
        blocking = tuple(
            criterion.criterion_id
            for criterion in criteria
            if criterion.required
            and by_pair[(option.option_id, criterion.criterion_id)].outcome
            is ComplexDecisionCriterionOutcome.UNFAVORABLE
        )
        review = tuple(
            criterion.criterion_id
            for criterion in criteria
            if by_pair[(option.option_id, criterion.criterion_id)].outcome
            is ComplexDecisionCriterionOutcome.INSUFFICIENT
        )
        if blocking:
            status = ComplexDecisionOptionStatus.BLOCKED
            rationale = ("complex_decision:hard_constraint_failed",)
        elif review:
            status = ComplexDecisionOptionStatus.REVIEW_REQUIRED
            rationale = ("complex_decision:criterion_evidence_insufficient",)
        else:
            status = ComplexDecisionOptionStatus.ELIGIBLE
            rationale = ("complex_decision:option_evaluable",)
        fingerprint = sha256(
            repr(
                (
                    option,
                    tuple(
                        (item, by_pair[(option.option_id, item.criterion_id)])
                        for item in criteria
                    ),
                    status.value,
                )
            ).encode("utf-8")
        ).hexdigest()
        return GovernedComplexDecisionOptionAssessment(
            option_id=option.option_id,
            status=status,
            criterion_assessments=items,
            blocking_criterion_ids=blocking,
            review_criterion_ids=review,
            rationale_codes=rationale,
            source_fingerprint=fingerprint,
        )

    @classmethod
    def _sole_required_constraint_survivor(
        cls,
        option_assessments: tuple[
            GovernedComplexDecisionOptionAssessment, ...
        ],
        criteria: tuple[GovernedDecisionCriterion, ...],
    ) -> GovernedComplexDecisionOptionAssessment | None:
        required = tuple(item for item in criteria if item.required)
        if not required:
            return None

        survivors = tuple(
            option
            for option in option_assessments
            if all(
                cls._criterion_assessment(
                    option,
                    criterion.criterion_id,
                ).outcome
                is ComplexDecisionCriterionOutcome.FAVORABLE
                for criterion in required
            )
        )
        if len(survivors) != 1:
            return None

        survivor = survivors[0]
        competitors = tuple(
            option
            for option in option_assessments
            if option.option_id != survivor.option_id
        )
        if not competitors or not all(
            option.status is ComplexDecisionOptionStatus.BLOCKED
            for option in competitors
        ):
            return None
        return survivor

    @classmethod
    def _select(
        cls,
        eligible: tuple[GovernedComplexDecisionOptionAssessment, ...],
        criteria: tuple[GovernedDecisionCriterion, ...],
    ) -> tuple[str | None, tuple[str, ...], tuple[str, ...]]:
        if not eligible:
            return None, (), ("complex_decision:no_eligible_option",)
        if len(eligible) == 1:
            return (
                eligible[0].option_id,
                (),
                ("complex_decision:single_eligible_option",),
            )

        dominant = tuple(
            candidate
            for candidate in eligible
            if all(
                candidate is other or cls._dominates(candidate, other, criteria)
                for other in eligible
            )
        )
        if len(dominant) == 1:
            return (
                dominant[0].option_id,
                (),
                ("complex_decision:pareto_dominance",),
            )

        tradeoffs = cls._tradeoff_codes(eligible, criteria)
        lexicographic = cls._lexicographic_selection(eligible, criteria)
        if lexicographic is not None:
            return (
                lexicographic,
                tradeoffs,
                ("complex_decision:explicit_importance_resolved_tradeoff",),
            )
        return (
            None,
            tradeoffs,
            ("complex_decision:non_dominated_review_required",),
        )

    @classmethod
    def _dominates(
        cls,
        left: GovernedComplexDecisionOptionAssessment,
        right: GovernedComplexDecisionOptionAssessment,
        criteria: tuple[GovernedDecisionCriterion, ...],
    ) -> bool:
        comparisons = tuple(
            cls._compare(
                cls._criterion_assessment(left, criterion.criterion_id),
                cls._criterion_assessment(right, criterion.criterion_id),
            )
            for criterion in criteria
        )
        return all(value >= 0 for value in comparisons) and any(
            value > 0 for value in comparisons
        )

    @classmethod
    def _lexicographic_selection(
        cls,
        eligible: tuple[GovernedComplexDecisionOptionAssessment, ...],
        criteria: tuple[GovernedDecisionCriterion, ...],
    ) -> str | None:
        if any(item.explicit_importance is None for item in criteria):
            return None
        groups: dict[float, list[GovernedDecisionCriterion]] = {}
        for criterion in criteria:
            assert criterion.explicit_importance is not None
            groups.setdefault(float(criterion.explicit_importance), []).append(
                criterion
            )

        contenders = eligible
        for importance in sorted(groups, reverse=True):
            group = tuple(
                sorted(groups[importance], key=lambda item: item.criterion_id)
            )
            best = cls._best_in_importance_group(contenders, group)
            if best is None:
                return None
            if len(best) == 1:
                return best[0].option_id
            contenders = best
        return None

    @classmethod
    def _best_in_importance_group(
        cls,
        contenders: tuple[GovernedComplexDecisionOptionAssessment, ...],
        criteria: tuple[GovernedDecisionCriterion, ...],
    ) -> tuple[GovernedComplexDecisionOptionAssessment, ...] | None:
        vectors = {
            item.option_id: tuple(
                cls._value_key(cls._criterion_assessment(item, criterion.criterion_id))
                for criterion in criteria
            )
            for item in contenders
        }
        maxima = tuple(
            item
            for item in contenders
            if all(
                item is other
                or cls._vector_not_worse(
                    vectors[item.option_id], vectors[other.option_id]
                )
                for other in contenders
            )
        )
        if not maxima:
            return None
        return maxima

    @staticmethod
    def _vector_not_worse(
        left: tuple[tuple[int, float], ...],
        right: tuple[tuple[int, float], ...],
    ) -> bool:
        return all(a >= b for a, b in zip(left, right, strict=True))

    @classmethod
    def _compare(
        cls,
        left: GovernedOptionCriterionAssessment,
        right: GovernedOptionCriterionAssessment,
    ) -> int:
        left_key = cls._value_key(left)
        right_key = cls._value_key(right)
        return (left_key > right_key) - (left_key < right_key)

    @staticmethod
    def _value_key(
        assessment: GovernedOptionCriterionAssessment,
    ) -> tuple[int, float]:
        rank = {
            ComplexDecisionCriterionOutcome.UNFAVORABLE: 0,
            ComplexDecisionCriterionOutcome.NEUTRAL: 1,
            ComplexDecisionCriterionOutcome.FAVORABLE: 2,
            ComplexDecisionCriterionOutcome.INSUFFICIENT: -1,
        }[assessment.outcome]
        explicit = (
            float(assessment.explicit_value)
            if assessment.explicit_value is not None
            else 0.0
        )
        return rank, explicit

    @staticmethod
    def _criterion_assessment(
        assessment: GovernedComplexDecisionOptionAssessment,
        criterion_id: str,
    ) -> GovernedOptionCriterionAssessment:
        return next(
            item
            for item in assessment.criterion_assessments
            if item.criterion_id == criterion_id
        )

    @classmethod
    def _tradeoff_codes(
        cls,
        eligible: tuple[GovernedComplexDecisionOptionAssessment, ...],
        criteria: tuple[GovernedDecisionCriterion, ...],
    ) -> tuple[str, ...]:
        codes: set[str] = set()
        for index, left in enumerate(eligible):
            for right in eligible[index + 1 :]:
                left_better: list[str] = []
                right_better: list[str] = []
                for criterion in criteria:
                    comparison = cls._compare(
                        cls._criterion_assessment(left, criterion.criterion_id),
                        cls._criterion_assessment(right, criterion.criterion_id),
                    )
                    if comparison > 0:
                        left_better.append(criterion.criterion_id)
                    elif comparison < 0:
                        right_better.append(criterion.criterion_id)
                if left_better and right_better:
                    codes.add(
                        "complex_decision:tradeoff:"
                        f"{left.option_id}:{','.join(sorted(left_better))}|"
                        f"{right.option_id}:{','.join(sorted(right_better))}"
                    )
        return tuple(sorted(codes))

    @staticmethod
    def _status(
        option_assessments: tuple[GovernedComplexDecisionOptionAssessment, ...],
        recommended: str | None,
        required_survivor_selected: bool = False,
    ) -> tuple[ComplexDecisionReasoningStatus, tuple[str, ...]]:
        if required_survivor_selected and recommended is not None:
            return (
                ComplexDecisionReasoningStatus.COMPLETE,
                (
                    "complex_decision:"
                    "required_constraint_survivor_advisory_complete",
                ),
            )
        if any(
            item.status is ComplexDecisionOptionStatus.REVIEW_REQUIRED
            for item in option_assessments
        ):
            return (
                ComplexDecisionReasoningStatus.INSUFFICIENT_EVIDENCE,
                ("complex_decision:insufficient_evidence_preserved",),
            )
        if recommended is None:
            return (
                ComplexDecisionReasoningStatus.REVIEW_REQUIRED,
                ("complex_decision:human_review_preserved",),
            )
        return (
            ComplexDecisionReasoningStatus.COMPLETE,
            ("complex_decision:advisory_complete",),
        )

    @staticmethod
    def _fingerprint(
        options: tuple[GovernedDecisionOption, ...],
        criteria: tuple[GovernedDecisionCriterion, ...],
        assessments: tuple[GovernedOptionCriterionAssessment, ...],
        recommended: str | None,
        status: ComplexDecisionReasoningStatus,
        tradeoffs: tuple[str, ...],
    ) -> str:
        payload = repr(
            (
                options,
                criteria,
                assessments,
                recommended,
                status.value,
                tradeoffs,
            )
        )
        return sha256(payload.encode("utf-8")).hexdigest()
