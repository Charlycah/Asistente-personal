from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone

import pytest

from core.controlled_autonomy import (
    ActionCandidateGenerator,
    ActionTemplate,
    CandidateGenerationResult,
    CandidateGenerationStatus,
    CandidateRule,
    DecisionSituation,
    DeterministicActionCandidateGenerator,
    Reversibility,
    RiskAssessment,
    default_candidate_rules,
)

NOW = datetime(2026, 7, 26, 21, 0, tzinfo=timezone.utc)


def situation(**changes: object) -> DecisionSituation:
    values: dict[str, object] = {
        "kind": "runtime_component_unhealthy",
        "description": "A runtime component is unhealthy",
        "evidence": ("component_id=vosk", "health_state=unhealthy"),
        "observed_at": NOW,
        "source": "component_health.vosk",
        "urgency": 0.9,
        "situation_id": "situation-1",
    }
    values.update(changes)
    return DecisionSituation(**values)


def template(**changes: object) -> ActionTemplate:
    values: dict[str, object] = {
        "action": "restart_component",
        "description": "Restart component",
        "rationale": ("attempt_local_recovery",),
        "reversible": Reversibility.PARTIAL,
        "estimated_cost": 0.3,
    }
    values.update(changes)
    return ActionTemplate(**values)


def rule(**changes: object) -> CandidateRule:
    values: dict[str, object] = {
        "situation_kind": "runtime_component_unhealthy",
        "templates": (template(),),
        "rule_id": "unhealthy-rule",
    }
    values.update(changes)
    return CandidateRule(**values)


@pytest.mark.parametrize("field", ("action", "description"))
def test_template_rejects_blank_text(field):
    with pytest.raises(ValueError):
        template(**{field: ""})


def test_template_requires_rationale():
    with pytest.raises(ValueError):
        template(rationale=())


def test_template_rejects_negative_cost():
    with pytest.raises(ValueError):
        template(estimated_cost=-0.1)


def test_template_normalizes_reversibility():
    item = template(reversible="full")
    assert item.reversible is Reversibility.FULL


@pytest.mark.parametrize("field", ("situation_kind", "rule_id"))
def test_rule_rejects_blank_identity(field):
    with pytest.raises(ValueError):
        rule(**{field: ""})


def test_rule_requires_templates():
    with pytest.raises(ValueError):
        rule(templates=())


def test_rule_rejects_duplicate_action_names():
    with pytest.raises(ValueError):
        rule(templates=(template(), replace(template(), description="Second")))


def test_generator_satisfies_protocol():
    generator = DeterministicActionCandidateGenerator((rule(),))
    assert isinstance(generator, ActionCandidateGenerator)


def test_generator_rejects_duplicate_rule_ids():
    with pytest.raises(ValueError):
        DeterministicActionCandidateGenerator(
            (rule(), replace(rule(), situation_kind="another"))
        )


def test_generator_rejects_duplicate_situation_kinds():
    with pytest.raises(ValueError):
        DeterministicActionCandidateGenerator(
            (rule(), replace(rule(), rule_id="another"))
        )


def test_generator_exposes_immutable_rule_order():
    rules = (rule(),)
    assert DeterministicActionCandidateGenerator(rules).rules == rules


def test_matching_situation_generates_candidate():
    result = DeterministicActionCandidateGenerator((rule(),)).generate(situation())
    assert result.status is CandidateGenerationStatus.CANDIDATES_GENERATED
    assert result.matched_rule_id == "unhealthy-rule"
    assert result.candidates[0].action == "restart_component"


def test_candidate_preserves_situation_traceability():
    candidate = (
        DeterministicActionCandidateGenerator((rule(),))
        .generate(situation())
        .candidates[0]
    )
    assert "situation_id=situation-1" in candidate.rationale
    assert "candidate_rule_id=unhealthy-rule" in candidate.rationale
    assert "candidate_order=1" in candidate.rationale


def test_candidate_id_is_deterministic():
    generator = DeterministicActionCandidateGenerator((rule(),))
    first = generator.generate(situation()).candidates[0]
    second = generator.generate(situation()).candidates[0]
    assert first.candidate_id == second.candidate_id
    assert first.candidate_id == "situation-1:unhealthy-rule:1"


def test_candidate_order_follows_template_order():
    second = template(
        action="notify_user",
        description="Notify user",
        reversible="full",
    )
    result = DeterministicActionCandidateGenerator(
        (rule(templates=(template(), second)),)
    ).generate(situation())
    assert tuple(item.action for item in result.candidates) == (
        "restart_component",
        "notify_user",
    )


def test_unknown_situation_is_unsupported():
    result = DeterministicActionCandidateGenerator((rule(),)).generate(
        situation(kind="unknown")
    )
    assert result.status is CandidateGenerationStatus.UNSUPPORTED
    assert result.candidates == ()
    assert result.rationale == ("no_rule_for_situation_kind",)


def test_generated_result_requires_candidates():
    with pytest.raises(ValueError):
        CandidateGenerationResult(
            status="candidates_generated",
            situation=situation(),
            candidates=(),
            rationale=("x",),
            matched_rule_id="rule",
        )


def test_generated_result_requires_rule_id():
    candidate = (
        DeterministicActionCandidateGenerator((rule(),))
        .generate(situation())
        .candidates[0]
    )
    with pytest.raises(ValueError):
        CandidateGenerationResult(
            status="candidates_generated",
            situation=situation(),
            candidates=(candidate,),
            rationale=("x",),
        )


def test_unsupported_result_rejects_candidates():
    candidate = (
        DeterministicActionCandidateGenerator((rule(),))
        .generate(situation())
        .candidates[0]
    )
    with pytest.raises(ValueError):
        CandidateGenerationResult(
            status="unsupported",
            situation=situation(),
            candidates=(candidate,),
            rationale=("x",),
        )


def test_result_rejects_duplicate_candidate_ids():
    candidate = (
        DeterministicActionCandidateGenerator((rule(),))
        .generate(situation())
        .candidates[0]
    )
    with pytest.raises(ValueError):
        CandidateGenerationResult(
            status="candidates_generated",
            situation=situation(),
            candidates=(candidate, candidate),
            rationale=("x",),
            matched_rule_id="rule",
        )


def test_default_rules_cover_assessed_situations():
    kinds = {item.situation_kind for item in default_candidate_rules()}
    assert kinds == {
        "battery_requires_attention",
        "reminder_requires_delivery",
        "runtime_component_degraded",
        "runtime_component_unhealthy",
    }


@pytest.mark.parametrize(
    "kind,actions",
    (
        (
            "runtime_component_degraded",
            ("verify_component_health", "notify_user", "do_nothing"),
        ),
        (
            "runtime_component_unhealthy",
            (
                "restart_component",
                "enter_degraded_mode",
                "notify_user",
                "do_nothing",
            ),
        ),
        (
            "battery_requires_attention",
            ("notify_user", "enable_power_saving", "do_nothing"),
        ),
        (
            "reminder_requires_delivery",
            ("deliver_reminder", "postpone_reminder", "do_nothing"),
        ),
    ),
)
def test_default_rules_generate_expected_order(kind, actions):
    result = DeterministicActionCandidateGenerator(default_candidate_rules()).generate(
        situation(kind=kind)
    )
    assert tuple(item.action for item in result.candidates) == actions


def test_default_candidates_have_non_negative_costs():
    generator = DeterministicActionCandidateGenerator(default_candidate_rules())
    for kind in (rule.situation_kind for rule in generator.rules):
        result = generator.generate(situation(kind=kind))
        assert all(item.estimated_cost >= 0.0 for item in result.candidates)


def test_default_candidates_include_do_nothing_fallback():
    generator = DeterministicActionCandidateGenerator(default_candidate_rules())
    for item in generator.rules:
        result = generator.generate(situation(kind=item.situation_kind))
        assert result.candidates[-1].action == "do_nothing"


def test_generator_does_not_create_risk_assessments():
    result = DeterministicActionCandidateGenerator(default_candidate_rules()).generate(
        situation()
    )
    assert all(not isinstance(item, RiskAssessment) for item in result.candidates)


def test_generator_has_no_execute_method():
    generator = DeterministicActionCandidateGenerator(default_candidate_rules())
    assert not hasattr(generator, "execute")
    assert not hasattr(generator, "authorize")
    assert not hasattr(generator, "decide")


def test_repeated_generation_preserves_value_equality():
    generator = DeterministicActionCandidateGenerator((rule(),))
    assert (
        generator.generate(situation()).candidates
        == generator.generate(situation()).candidates
    )
