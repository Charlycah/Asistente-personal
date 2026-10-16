from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BrainStructuralComponent:
    name: str
    role: str
    read_only: bool
    dependencies: tuple[str, ...] = ()


@dataclass(frozen=True)
class BrainStructuralAuditReport:
    components: tuple[BrainStructuralComponent, ...]
    entry_points: tuple[str, ...]
    write_points: tuple[str, ...]
    runtime_connected: bool

    @property
    def component_count(self) -> int:
        return len(self.components)

    def to_dict(self) -> dict[str, object]:
        return {
            "summary": {
                "component_count": self.component_count,
                "runtime_connected": self.runtime_connected,
            },
            "entry_points": list(self.entry_points),
            "write_points": list(self.write_points),
            "components": [
                {
                    "name": item.name,
                    "role": item.role,
                    "read_only": item.read_only,
                    "dependencies": list(item.dependencies),
                }
                for item in self.components
            ],
        }


class BrainStructuralAudit:
    """Static, side-effect-free map of the composed identity BRAIN."""

    def inspect(self) -> BrainStructuralAuditReport:
        components = (
            BrainStructuralComponent(
                "brain_service",
                "memory orchestration and query filtering",
                False,
                ("brain_repository", "brain_readers"),
            ),
            BrainStructuralComponent(
                "official_memory_adapter",
                "read-only official memory reader",
                True,
            ),
            BrainStructuralComponent(
                "goal_project_adapter",
                "read-only goals and projects reader",
                True,
            ),
            BrainStructuralComponent(
                "relationship_preference_adapter",
                "read-only relationship and preference reader",
                True,
            ),
            BrainStructuralComponent(
                "identity_profile_adapter",
                "read-only identity profile reader",
                True,
            ),
            BrainStructuralComponent(
                "active_identity_resolver",
                "active private identity resolution",
                True,
            ),
            BrainStructuralComponent(
                "safe_personal_context",
                "identity-scoped personal context selection",
                True,
                ("brain_service", "active_identity_resolver"),
            ),
            BrainStructuralComponent(
                "conversation_context_preparer",
                "bounded conversational context preparation",
                True,
                ("safe_personal_context",),
            ),
            BrainStructuralComponent(
                "conversation_context_diagnostic",
                "prepared context consistency inspection",
                True,
                ("conversation_context_preparer",),
            ),
        )
        return BrainStructuralAuditReport(
            components=components,
            entry_points=(
                "BrainService.remember",
                "BrainService.recall",
                "BrainService.update",
                "BrainService.forget",
                "BrainService.expire",
                "ConversationContextPreparer.prepare",
            ),
            write_points=(
                "BrainService.remember",
                "BrainService.update",
                "BrainService.forget",
                "BrainService.expire",
            ),
            runtime_connected=False,
        )
