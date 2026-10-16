from __future__ import annotations

import os
from collections.abc import Callable
from datetime import timedelta

from app.medical_appointment_consultation_offer import (
    MedicalAppointmentConsultationOffer,
)
from core.always_on_personal_runtime import (
    BatteryAwarenessPolicy,
    BatteryAwarenessService,
    IntelligentReminderPolicy,
    ReminderAwarenessService,
)
from infrastructure.persistence.sqlite import SQLiteReminderRuntimeStore
from infrastructure.system import NativeBatterySensor

_TRUE = {"1", "true", "yes", "on"}


def build_battery_awareness_from_environment(
    *,
    notify: Callable[[str], None],
    owner: str,
) -> BatteryAwarenessService | None:
    if not _env_bool("ROBY_PERSONAL_RUNTIME_ENABLED", True):
        return None
    if not _env_bool("ROBY_BATTERY_AWARENESS_ENABLED", True):
        return None
    return BatteryAwarenessService(
        NativeBatterySensor(),
        notify=notify,
        owner=owner,
        policy=BatteryAwarenessPolicy(
            low_threshold=_env_int("ROBY_BATTERY_LOW_PERCENT", 15),
            recovery_margin=_env_int("ROBY_BATTERY_RECOVERY_MARGIN", 5),
            poll_interval=timedelta(
                seconds=_env_float("ROBY_BATTERY_POLL_SECONDS", 30.0)
            ),
            repeat_after=timedelta(
                seconds=_env_float("ROBY_BATTERY_REPEAT_SECONDS", 1800.0)
            ),
        ),
    )


def build_reminder_awareness_from_environment(
    *,
    notify: Callable[[str], None],
    owner: str,
) -> ReminderAwarenessService | None:
    if not _env_bool("ROBY_PERSONAL_RUNTIME_ENABLED", True):
        return None
    if not _env_bool("ROBY_REMINDER_AWARENESS_ENABLED", True):
        return None
    store = SQLiteReminderRuntimeStore(
        os.getenv("ROBY_REMINDER_DB_PATH", ".roby/reminders.db"),
        owner=owner,
    )
    return ReminderAwarenessService(
        store,
        notify=notify,
        owner=owner,
        poll_interval=timedelta(seconds=_env_float("ROBY_REMINDER_POLL_SECONDS", 30.0)),
        intelligent_policy=IntelligentReminderPolicy(),
        enhance_notice=MedicalAppointmentConsultationOffer().enhance,
    )


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None or not value.strip():
        return default
    return value.strip().casefold() in _TRUE


def _env_int(name: str, default: int) -> int:
    value = os.getenv(name, "").strip()
    return default if not value else int(value)


def _env_float(name: str, default: float) -> float:
    value = os.getenv(name, "").strip()
    return default if not value else float(value)


def build_ambient_proactive_runtime_from_environment(
    *,
    notify: Callable[[str], None],
    coordinator,
    latest_self_analysis,
    request_visual_capture=None,
):
    """Build the resident RP.06 loop when a local ambient source is configured."""
    if not _env_bool("ROBY_PERSONAL_RUNTIME_ENABLED", True):
        return None
    if not _env_bool("ROBY_AMBIENT_PROACTIVE_ENABLED", False):
        return None
    command = tuple(
        part for part in os.getenv("ROBY_AMBIENT_INPUT_COMMAND", "").split() if part
    )
    if not command:
        return None
    from app.ambient_proactive_runtime import (
        AmbientProactiveRuntime,
        AmbientProactiveRuntimePolicy,
        LocalCommandAmbientObservationSource,
    )

    return AmbientProactiveRuntime(
        LocalCommandAmbientObservationSource(command),
        coordinator,
        notify=notify,
        request_visual_capture=request_visual_capture,
        latest_self_analysis=latest_self_analysis,
        policy=AmbientProactiveRuntimePolicy(
            poll_interval=timedelta(
                seconds=_env_float("ROBY_AMBIENT_POLL_SECONDS", 2.0)
            )
        ),
    )


def build_continuous_cognitive_loop_from_environment(
    *,
    latest_self_analysis,
    open_commitments=None,
    active_goals=None,
    active_projects=None,
    active_tasks=None,
    pending_reminders=None,
    upcoming_calendar_events=None,
    relevant_notes=None,
    ambient_activity=None,
    agenda_manager=None,
):
    """Build RP.10's lightweight resident cognitive state loop."""
    if not _env_bool("ROBY_PERSONAL_RUNTIME_ENABLED", True):
        return None
    if not _env_bool("ROBY_CONTINUOUS_COGNITIVE_LOOP_ENABLED", True):
        return None
    from app.cognitive_agenda_manager import (
        CognitiveAgendaKind,
        CognitiveAgendaManager,
        CognitiveAgendaSignal,
        CognitiveAgendaStatus,
    )
    from app.cognitive_agenda_sources import CallableCognitiveAgendaSource
    from app.continuous_internal_cognitive_loop import (
        ContinuousCognitiveLoopPolicy,
        ContinuousInternalCognitiveLoop,
    )

    if agenda_manager is None:
        sources = []
        if latest_self_analysis is not None:

            def collect_conversation(now):
                report = latest_self_analysis()
                if report is None or not any(
                    finding.dimension in {"repair", "context"}
                    for finding in report.findings
                ):
                    return ()
                return (
                    CognitiveAgendaSignal(
                        key="conversation:repair",
                        kind=CognitiveAgendaKind.CONVERSATION,
                        title="Reparar continuidad conversacional",
                        source="conversational_self_analysis",
                        priority=0.95,
                        urgency=0.85,
                        relevance=1.0,
                        observed_at=now,
                        rationale="recent_self_analysis_requires_conversation_repair",
                    ),
                )

            sources.append(
                CallableCognitiveAgendaSource(
                    "conversational_self_analysis", collect_conversation
                )
            )
        if open_commitments is not None:

            def collect_commitments(now):
                count = max(0, int(open_commitments()))
                if count == 0:
                    return ()
                return (
                    CognitiveAgendaSignal(
                        key="commitments:open",
                        kind=CognitiveAgendaKind.COMMITMENT,
                        title="Mantener continuidad de compromisos abiertos",
                        source="open_commitments",
                        priority=min(1.0, 0.55 + count * 0.05),
                        relevance=0.9,
                        observed_at=now,
                        rationale="open_commitments_require_continuity",
                    ),
                )

            sources.append(
                CallableCognitiveAgendaSource("open_commitments", collect_commitments)
            )
        if active_goals is not None:

            def collect_goals(now):
                signals = []
                for goal in active_goals():
                    status = getattr(goal, "normalized_status", None)
                    status_value = getattr(
                        status, "value", str(status or "")
                    ).casefold()
                    if status_value != "active":
                        continue
                    next_step = str(getattr(goal, "next_step", "") or "").strip()
                    target_date = getattr(goal, "target_date", None)
                    if not next_step and target_date is None:
                        continue
                    goal_id = str(getattr(goal, "goal_id", "") or "").strip()
                    name = str(getattr(goal, "name", "") or "").strip()
                    if not goal_id or not name:
                        continue
                    signals.append(
                        CognitiveAgendaSignal(
                            key=f"goal:{goal_id}",
                            kind=CognitiveAgendaKind.GOAL,
                            title=name,
                            source="household_goals",
                            priority=0.72,
                            relevance=0.82,
                            observed_at=now,
                            rationale="active_goal_requires_continuity",
                        )
                    )
                return tuple(signals)

            sources.append(
                CallableCognitiveAgendaSource("household_goals", collect_goals)
            )
        if active_projects is not None:

            def collect_projects(now):
                signals = []
                for project in active_projects():
                    status = getattr(project, "normalized_status", None)
                    status_value = getattr(
                        status, "value", str(status or "")
                    ).casefold()
                    next_step = str(getattr(project, "next_step", "") or "").strip()
                    if status_value != "active" or not next_step:
                        continue
                    project_id = str(getattr(project, "project_id", "") or "").strip()
                    name = str(getattr(project, "name", "") or "").strip()
                    if not project_id or not name:
                        continue
                    signals.append(
                        CognitiveAgendaSignal(
                            key=f"project:{project_id}",
                            kind=CognitiveAgendaKind.PROJECT,
                            title=name,
                            source="household_projects",
                            priority=0.7,
                            relevance=0.8,
                            observed_at=now,
                            rationale="active_project_next_step_requires_continuity",
                        )
                    )
                return tuple(signals)

            sources.append(
                CallableCognitiveAgendaSource("household_projects", collect_projects)
            )
        if active_tasks is not None:

            def collect_tasks(now):
                signals = []
                active_statuses = {"pending", "in_progress", "blocked"}
                for task in active_tasks():
                    status = getattr(task, "normalized_status", None)
                    status_value = getattr(
                        status, "value", str(status or "")
                    ).casefold()
                    if status_value not in active_statuses:
                        continue
                    deadline = getattr(task, "deadline", None)
                    importance = int(getattr(task, "importance", 0) or 0)
                    urgency = int(getattr(task, "urgency", 0) or 0)
                    deadline_relevant = (
                        deadline is not None and deadline <= now + timedelta(days=7)
                    )
                    if (
                        status_value != "blocked"
                        and importance < 8
                        and urgency < 8
                        and not deadline_relevant
                    ):
                        continue
                    task_id = str(getattr(task, "task_id", "") or "").strip()
                    title = str(getattr(task, "title", "") or "").strip()
                    if not task_id or not title:
                        continue
                    signals.append(
                        CognitiveAgendaSignal(
                            key=f"task:{task_id}",
                            kind=CognitiveAgendaKind.FOLLOW_UP,
                            title=title,
                            source="resident_tasks",
                            priority=min(1.0, importance / 10.0),
                            urgency=min(1.0, urgency / 10.0),
                            relevance=0.86,
                            status=(
                                CognitiveAgendaStatus.BLOCKED
                                if status_value == "blocked"
                                else CognitiveAgendaStatus.ACTIVE
                            ),
                            observed_at=now,
                            rationale="relevant_personal_task_requires_attention",
                        )
                    )
                return tuple(signals)

            sources.append(
                CallableCognitiveAgendaSource(
                    "resident_tasks",
                    collect_tasks,
                    absence_status=CognitiveAgendaStatus.CLOSED,
                )
            )
        if pending_reminders is not None:

            def collect_reminders(now):
                signals = []
                horizon = now + timedelta(hours=48)
                for reminder in pending_reminders():
                    status = getattr(reminder, "status", None)
                    status_value = getattr(
                        status, "value", str(status or "")
                    ).casefold()
                    due_at = getattr(reminder, "due_at", None)
                    if status_value != "pending" or due_at is None:
                        continue
                    if due_at > horizon:
                        continue
                    reminder_id = str(getattr(reminder, "id", "") or "").strip()
                    title = str(getattr(reminder, "title", "") or "").strip()
                    if not reminder_id or not title:
                        continue
                    seconds = (due_at - now).total_seconds()
                    urgency = (
                        1.0 if seconds <= 0 else max(0.65, 1.0 - seconds / (48 * 3600))
                    )
                    signals.append(
                        CognitiveAgendaSignal(
                            key=f"reminder:{reminder_id}",
                            kind=CognitiveAgendaKind.FOLLOW_UP,
                            title=title,
                            source="resident_reminders",
                            priority=0.82,
                            urgency=urgency,
                            relevance=0.92,
                            observed_at=now,
                            rationale="pending_reminder_is_temporally_relevant",
                        )
                    )
                return tuple(signals)

            sources.append(
                CallableCognitiveAgendaSource(
                    "resident_reminders",
                    collect_reminders,
                    absence_status=CognitiveAgendaStatus.CLOSED,
                )
            )
        if upcoming_calendar_events is not None:

            def collect_calendar(now):
                signals = []
                for event in upcoming_calendar_events(now):
                    event_id = str(getattr(event, "event_id", "") or "").strip()
                    title = str(getattr(event, "title", "") or "").strip()
                    time_range = getattr(event, "time_range", None)
                    starts_at = getattr(time_range, "starts_at", None)
                    ends_at = getattr(time_range, "ends_at", None)
                    if (
                        not event_id
                        or not title
                        or starts_at is None
                        or ends_at is None
                        or ends_at <= now
                    ):
                        continue
                    hours = max(0.0, (starts_at - now).total_seconds() / 3600)
                    urgency = max(0.55, min(1.0, 1.0 - hours / 48.0))
                    signals.append(
                        CognitiveAgendaSignal(
                            key=f"calendar:{event_id}",
                            kind=CognitiveAgendaKind.FOLLOW_UP,
                            title=title,
                            source="calendar_read",
                            priority=0.72,
                            urgency=urgency,
                            relevance=0.88,
                            observed_at=now,
                            expires_at=ends_at,
                            rationale="upcoming_calendar_event_requires_awareness",
                        )
                    )
                return tuple(signals)

            sources.append(
                CallableCognitiveAgendaSource(
                    "calendar_read",
                    collect_calendar,
                    absence_status=CognitiveAgendaStatus.ARCHIVED,
                )
            )
        if relevant_notes is not None:

            def collect_notes(now):
                signals = []
                follow_up_tags = {
                    "actionable",
                    "agenda",
                    "follow_up",
                    "pendiente",
                    "seguimiento",
                }
                for note in relevant_notes():
                    kind = getattr(note, "normalized_kind", None)
                    kind_value = getattr(kind, "value", str(kind or "")).casefold()
                    status = getattr(note, "normalized_status", None)
                    status_value = getattr(
                        status, "value", str(status or "")
                    ).casefold()
                    tags = set(getattr(note, "normalized_tags", ()) or ())
                    if (
                        kind_value != "note"
                        or status_value != "active"
                        or not tags.intersection(follow_up_tags)
                    ):
                        continue
                    item_id = str(getattr(note, "item_id", "") or "").strip()
                    title = str(getattr(note, "title", "") or "").strip()
                    if not item_id or not title:
                        continue
                    signals.append(
                        CognitiveAgendaSignal(
                            key=f"note:{item_id}",
                            kind=CognitiveAgendaKind.FOLLOW_UP,
                            title=title,
                            source="personal_knowledge_notes",
                            priority=0.62,
                            urgency=0.35,
                            relevance=0.78,
                            observed_at=now,
                            rationale="explicit_follow_up_note_requires_attention",
                        )
                    )
                return tuple(signals)

            sources.append(
                CallableCognitiveAgendaSource(
                    "personal_knowledge_notes",
                    collect_notes,
                    absence_status=CognitiveAgendaStatus.ARCHIVED,
                )
            )
        if ambient_activity is not None:

            def collect_ambient(now):
                count = max(0, int(ambient_activity()))
                if count == 0:
                    return ()
                return (
                    CognitiveAgendaSignal(
                        key="ambient:current",
                        kind=CognitiveAgendaKind.AMBIENT,
                        title="Mantener conciencia del contexto ambiental",
                        source="ambient_runtime",
                        priority=0.7,
                        urgency=min(1.0, 0.4 + count * 0.05),
                        relevance=0.8,
                        observed_at=now,
                        rationale="ambient_activity_is_current",
                    ),
                )

            sources.append(
                CallableCognitiveAgendaSource("ambient_runtime", collect_ambient)
            )
        repository = None
        if _env_bool("ROBY_COGNITIVE_AGENDA_PERSISTENCE_ENABLED", True):
            from infrastructure.repositories.sqlite_cognitive_agenda_repository import (
                SQLiteCognitiveAgendaRepository,
            )

            repository = SQLiteCognitiveAgendaRepository(
                os.getenv(
                    "ROBY_COGNITIVE_AGENDA_DB_PATH",
                    ".roby/cognitive_agenda.db",
                )
            )
        agenda_manager = CognitiveAgendaManager(sources, repository=repository)

    return ContinuousInternalCognitiveLoop(
        latest_self_analysis=latest_self_analysis,
        open_commitments=open_commitments,
        ambient_activity=ambient_activity,
        agenda_manager=agenda_manager,
        policy=ContinuousCognitiveLoopPolicy(
            cycle_interval=timedelta(
                seconds=_env_float("ROBY_COGNITIVE_LOOP_SECONDS", 15.0)
            )
        ),
    )
