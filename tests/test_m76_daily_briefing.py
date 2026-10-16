from datetime import datetime, timedelta, timezone

import pytest

from core.daily_briefing import (
    BriefingItem,
    BriefingPeriod,
    BriefingSeverity,
    BriefingSource,
    DailyBriefing,
    DailyBriefingManager,
    DailyBriefingSignal,
)
from core.household_memory import (
    HouseholdMemoryCategory,
    HouseholdMemoryEntry,
    HouseholdMemoryManager,
)
from core.task_intelligence import TaskIntelligenceManager, TaskOwner

NOW = datetime(2026, 7, 10, 8, 0, tzinfo=timezone.utc)


def test_briefing_item_requires_content() -> None:
    with pytest.raises(ValueError):
        BriefingItem("", "detail", BriefingSource.SYSTEM)


def test_briefing_item_requires_aware_deadline() -> None:
    with pytest.raises(ValueError):
        BriefingItem(
            "Turno",
            "Revisar",
            BriefingSource.TASKS,
            due_at=datetime(2026, 7, 11),
        )


def test_daily_briefing_renders_empty_state() -> None:
    briefing = DailyBriefing(
        period=BriefingPeriod.MORNING,
        owner=TaskOwner.SHARED,
        items=(),
        signals=(DailyBriefingSignal.EMPTY,),
        generated_at=NOW,
    )
    assert "No hay asuntos relevantes" in briefing.render_text()


def test_manager_rejects_invalid_limit() -> None:
    with pytest.raises(ValueError):
        DailyBriefingManager(max_items=0)


def test_manager_rejects_naive_timestamp() -> None:
    with pytest.raises(ValueError):
        DailyBriefingManager().generate(now=datetime(2026, 7, 10))


def test_empty_briefing_contains_expected_signals() -> None:
    briefing = DailyBriefingManager().generate(now=NOW)
    assert DailyBriefingSignal.GENERATED in briefing.signals
    assert DailyBriefingSignal.EMPTY in briefing.signals
    assert DailyBriefingSignal.SCOPE_PRESERVED in briefing.signals


def test_overdue_task_is_urgent() -> None:
    tasks = TaskIntelligenceManager()
    task = tasks.approve(
        tasks.create_candidate(
            title="Renovar documento",
            description="Completar trámite personal",
            deadline=NOW - timedelta(hours=1),
        ),
        reviewed=True,
        now=NOW - timedelta(days=2),
    )
    briefing = DailyBriefingManager(task_intelligence=tasks).generate(now=NOW)
    assert briefing.items[0].reference_id == task.task_id
    assert briefing.items[0].normalized_severity is BriefingSeverity.URGENT
    assert briefing.urgent_count == 1


def test_task_due_in_three_days_requires_attention() -> None:
    tasks = TaskIntelligenceManager()
    tasks.approve(
        tasks.create_candidate(
            title="Preparar documentación",
            description="Reunir documentación necesaria",
            deadline=NOW + timedelta(days=2),
        ),
        reviewed=True,
        now=NOW,
    )
    briefing = DailyBriefingManager(task_intelligence=tasks).generate(now=NOW)
    assert briefing.items[0].normalized_severity is BriefingSeverity.ATTENTION


def test_owner_filter_keeps_shared_and_selected_tasks() -> None:
    tasks = TaskIntelligenceManager()
    for title, owner in (
        ("Tarea Carlos", TaskOwner.CARLOS),
        ("Tarea pareja", TaskOwner.PARTNER),
        ("Tarea común", TaskOwner.SHARED),
    ):
        tasks.approve(
            tasks.create_candidate(
                title=title,
                description="Seguimiento",
                owner=owner,
            ),
            reviewed=True,
            now=NOW,
        )
    briefing = DailyBriefingManager(task_intelligence=tasks).generate(
        owner=TaskOwner.CARLOS,
        now=NOW,
    )
    titles = {item.title for item in briefing.items}
    assert titles == {"Tarea Carlos", "Tarea común"}


def test_household_due_entry_is_included() -> None:
    memory = HouseholdMemoryManager()
    entry = memory.remember(
        HouseholdMemoryEntry(
            title="Revisar garantía",
            details="Garantía próxima a vencer",
            category=HouseholdMemoryCategory.WARRANTY,
            due_at=NOW,
        )
    )
    briefing = DailyBriefingManager(household_memory=memory).generate(now=NOW)
    assert briefing.items[0].reference_id == entry.entry_id
    assert briefing.items[0].normalized_source is BriefingSource.HOUSEHOLD_MEMORY


def test_max_items_is_enforced() -> None:
    tasks = TaskIntelligenceManager()
    for index in range(4):
        tasks.approve(
            tasks.create_candidate(
                title=f"Tarea {index}",
                description="Seguimiento diario",
                urgency=index + 1,
            ),
            reviewed=True,
            now=NOW,
        )
    briefing = DailyBriefingManager(
        task_intelligence=tasks,
        max_items=2,
    ).generate(now=NOW)
    assert len(briefing.items) == 2


def test_urgent_items_sort_before_informational_items() -> None:
    items = (
        BriefingItem("Info", "Detalle", BriefingSource.SYSTEM),
        BriefingItem(
            "Urgente",
            "Detalle",
            BriefingSource.SYSTEM,
            BriefingSeverity.URGENT,
        ),
    )
    manager = DailyBriefingManager()
    ordered = sorted(items, key=manager._sort_key)
    assert ordered[0].title == "Urgente"


def test_briefing_serialization_includes_rendered_text() -> None:
    briefing = DailyBriefingManager().generate(
        period=BriefingPeriod.EVENING,
        now=NOW,
    )
    payload = briefing.to_dict()
    assert payload["period"] == "evening"
    assert "Resumen del día" in str(payload["text"])


def test_system_prompt_before_generation_is_safe() -> None:
    lines = DailyBriefingManager().system_prompt_lines()
    assert "Todavía no se generó" in "\n".join(lines)


def test_system_prompt_after_generation_reports_counts() -> None:
    manager = DailyBriefingManager()
    manager.generate(now=NOW)
    lines = manager.system_prompt_lines()
    assert "- Elementos relevantes: 0" in lines
