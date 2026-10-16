from application.brain import (
    BrainManualTestCategory,
    BrainManualTestResult,
    build_m312_16_manual_test_bank,
)


def test_m312_16_bank_has_expected_campaign_shape() -> None:
    bank = build_m312_16_manual_test_bank()

    assert bank.version == "M312.16"
    assert bank.case_count == 20
    assert bank.category_counts() == {
        "isolated": 5,
        "rephrasing": 5,
        "continuity": 5,
        "topic_change": 3,
        "fallback": 2,
    }


def test_m312_16_case_ids_are_unique_and_ordered() -> None:
    bank = build_m312_16_manual_test_bank()
    case_ids = [case.case_id for case in bank.cases]

    assert len(case_ids) == len(set(case_ids))
    assert case_ids == [f"BRAIN-{number:03d}" for number in range(1, 21)]


def test_m312_16_multiturn_cases_define_expected_behavior_per_turn() -> None:
    bank = build_m312_16_manual_test_bank()
    continuity = [
        case
        for case in bank.cases
        if case.category is BrainManualTestCategory.CONTINUITY
    ]

    assert all(len(case.turns) == 2 for case in continuity)
    assert all(turn.expected_behavior for case in bank.cases for turn in case.turns)


def test_m312_16_bank_serialization_is_deterministic() -> None:
    first = build_m312_16_manual_test_bank().to_dict()
    second = build_m312_16_manual_test_bank().to_dict()

    assert first == second
    assert first["case_count"] == 20


def test_m312_16_result_record_does_not_execute_runtime() -> None:
    result = BrainManualTestResult(
        case_id="BRAIN-001",
        channel="text",
        observed_response="Buenas tardes. ¿Cómo estás?",
        passed=True,
        observed_intent="saludo",
        context_used=False,
        memory_written=False,
    )

    assert result.passed is True
    assert result.memory_written is False
