from __future__ import annotations

from dataclasses import dataclass

from core.agenda_evidence import AgendaEventEvidence
from core.household_goals import GoalStatus, HouseholdGoal
from core.household_projects import HouseholdProject, ProjectStatus
from core.intelligent_personal_organization import PersonalOrganizationItem
from core.personal_knowledge_base import KnowledgeItem, KnowledgeKind, KnowledgeStatus
from core.personal_organization import PersonalOrganizationCapability
from core.task_intelligence import Task, TaskStatus
from domain.reminders.entities import Reminder
from domain.reminders.enums import ReminderStatus


@dataclass(frozen=True)
class ProductiveOrganizationEvidenceProjection:
    """Pure read-only projection of admitted organization evidence into M391.5."""

    CANONICAL_AUTHORITY = "PersonalOrganizationAuthority"
    TARGET_CONTRACT = "M391.5"

    def project(
        self,
        *,
        tasks: tuple[Task, ...] = (),
        goals: tuple[HouseholdGoal, ...] = (),
        projects: tuple[HouseholdProject, ...] = (),
        reminders: tuple[Reminder, ...] = (),
        agenda_events: tuple[AgendaEventEvidence, ...] = (),
        knowledge_notes: tuple[KnowledgeItem, ...] = (),
    ) -> tuple[PersonalOrganizationItem, ...]:
        items = (
            *(
                self.project_knowledge_note(item)
                for item in knowledge_notes
                if self._admit_knowledge_note(item)
            ),
            *(
                self.project_agenda_event(event)
                for event in agenda_events
            ),
            *(self.project_task(task) for task in tasks if self._admit_task(task)),
            *(self.project_goal(goal) for goal in goals if self._admit_goal(goal)),
            *(
                self.project_project(project)
                for project in projects
                if self._admit_project(project)
            ),
            *(
                self.project_reminder(reminder)
                for reminder in reminders
                if self._admit_reminder(reminder)
            ),
        )
        self._validate_unique_ids(items)
        return tuple(
            sorted(
                items,
                key=lambda item: (item.normalized_capability.value, item.item_id),
            )
        )

    @staticmethod
    def project_knowledge_note(item: KnowledgeItem) -> PersonalOrganizationItem:
        if item.normalized_kind is not KnowledgeKind.NOTE:
            raise ValueError(
                "organization Notes projection requires KnowledgeKind.NOTE"
            )
        return PersonalOrganizationItem(
            item_id=item.item_id,
            capability=PersonalOrganizationCapability.NOTES,
            title=item.title,
            user_declared=True,
            source_reference=f"knowledge:note:{item.item_id}",
        )

    @staticmethod
    def project_agenda_event(
        event: AgendaEventEvidence,
        *,
        now=None,
    ) -> PersonalOrganizationItem:
        del now
        return PersonalOrganizationItem(
            item_id=event.agenda_id,
            capability=PersonalOrganizationCapability.AGENDA,
            title=event.title,
            deadline_proximity=1.0,
            source_reference=event.source_reference,
        )

    @staticmethod
    def project_task(task: Task) -> PersonalOrganizationItem:
        return PersonalOrganizationItem(
            item_id=task.task_id,
            capability=PersonalOrganizationCapability.TASKS,
            title=task.title,
            urgency=task.urgency / 10.0,
            importance=task.importance / 10.0,
            blocked=task.normalized_status is TaskStatus.BLOCKED,
            source_reference=f"task:{task.task_id}",
        )

    @staticmethod
    def project_goal(goal: HouseholdGoal) -> PersonalOrganizationItem:
        return PersonalOrganizationItem(
            item_id=goal.goal_id,
            capability=PersonalOrganizationCapability.GOALS,
            title=goal.name,
            source_reference=f"goal:{goal.goal_id}",
        )

    @staticmethod
    def project_project(project: HouseholdProject) -> PersonalOrganizationItem:
        return PersonalOrganizationItem(
            item_id=project.project_id,
            capability=PersonalOrganizationCapability.PROJECTS,
            title=project.name,
            source_reference=f"project:{project.project_id}",
        )

    @staticmethod
    def project_reminder(reminder: Reminder) -> PersonalOrganizationItem:
        return PersonalOrganizationItem(
            item_id=str(reminder.id),
            capability=PersonalOrganizationCapability.REMINDERS,
            title=reminder.title,
            source_reference=f"reminder:{reminder.id}",
        )

    @staticmethod
    def _admit_knowledge_note(item: KnowledgeItem) -> bool:
        return (
            item.normalized_kind is KnowledgeKind.NOTE
            and item.normalized_status is KnowledgeStatus.ACTIVE
        )

    @staticmethod
    def _admit_task(task: Task) -> bool:
        return task.normalized_status in {
            TaskStatus.PENDING,
            TaskStatus.IN_PROGRESS,
            TaskStatus.BLOCKED,
        }

    @staticmethod
    def _admit_goal(goal: HouseholdGoal) -> bool:
        return goal.normalized_status in {GoalStatus.ACTIVE, GoalStatus.PAUSED}

    @staticmethod
    def _admit_project(project: HouseholdProject) -> bool:
        return project.normalized_status in {ProjectStatus.ACTIVE, ProjectStatus.PAUSED}

    @staticmethod
    def _admit_reminder(reminder: Reminder) -> bool:
        return reminder.status is ReminderStatus.PENDING

    @staticmethod
    def _validate_unique_ids(items: tuple[PersonalOrganizationItem, ...]) -> None:
        ids = tuple(item.item_id for item in items)
        if len(ids) != len(set(ids)):
            raise ValueError("projected organization item ids must be unique")
