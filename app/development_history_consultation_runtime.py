from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from app.development_history_source import (
    DevelopmentHistorySourceAdapter,
    HistoricalSourceKind,
    build_development_history_source_from_environment,
)
from core.capability_registry import (
    CapabilityDescriptor,
    CapabilityEffectClass,
    CapabilityInitiationPolicy,
    CapabilityInteractionScope,
    PermissionScope,
)
from core.governed_operational_conversation_pipeline import (
    GovernedOperationalInterception,
)

_PENDING_TTL = timedelta(minutes=5)


@dataclass(frozen=True)
class _PendingSelection:
    candidates: tuple
    created_at: datetime


class DevelopmentHistoryConsultationInterceptionPort:
    """Human-explicit, read-only consultation of governed development history."""

    def __init__(self, source: DevelopmentHistorySourceAdapter) -> None:
        self.source = source
        self._pending: dict[str, _PendingSelection] = {}

    def intercept(self, request, *, now: datetime):
        text = request.text.strip()
        normalized = text.casefold()
        pending = self._pending.get(request.session_id)
        if pending is not None:
            if now - pending.created_at > _PENDING_TTL:
                self._pending.pop(request.session_id, None)
                return None
            if "cancel" in normalized:
                self._pending.pop(request.session_id, None)
                return GovernedOperationalInterception("Consulta histórica cancelada.")
            selected = self._select_presented(pending.candidates, text)
            if selected is not None:
                self._pending.pop(request.session_id, None)
                if selected.source_kind is HistoricalSourceKind.OPAQUE:
                    return GovernedOperationalInterception(
                        "Ese artefacto histórico es opaque y no se puede leer."
                    )
                observation = self.source.read_selected(selected.candidate_id)
                return GovernedOperationalInterception(observation.text)
        query = self._explicit_query(text)
        if query is None:
            return None
        candidates = tuple(
            item for item in self.source.discover().candidates
            if query.casefold() in item.relative_path.casefold()
        )
        if not candidates:
            return GovernedOperationalInterception(
                "No encontré coincidencias en el historial de desarrollo."
            )
        self._pending[request.session_id] = _PendingSelection(candidates, now)
        metadata_only = "d:\\roby" in normalized
        if (
            len(candidates) == 1
            and not metadata_only
            and candidates[0].source_kind is HistoricalSourceKind.DIRECT_READABLE
        ):
            observation = self.source.read_selected(candidates[0].candidate_id)
            self._pending.pop(request.session_id, None)
            return GovernedOperationalInterception(observation.text)
        lines = []
        for index, candidate in enumerate(candidates, 1):
            marker = (
                " (opaque)"
                if candidate.source_kind is HistoricalSourceKind.OPAQUE
                else ""
            )
            lines.append(f"{index}. {candidate.relative_path}{marker}")
        return GovernedOperationalInterception("\n".join(lines))

    def _explicit_query(self, text: str) -> str | None:
        normalized = text.casefold()
        markers = (
            "consultá el historial de desarrollo",
            "consulta el historial de desarrollo",
            "consultá d:\\roby",
            "consulta d:\\roby",
        )
        marker = next((item for item in markers if item in normalized), None)
        if marker is None:
            return None
        tail = text[normalized.index(marker) + len(marker):].strip(" :")
        if tail.casefold().startswith("de roby"):
            tail = tail[7:].strip(" :")
        if tail.casefold().startswith("por "):
            tail = tail[4:].strip()
        return tail or ""

    def _select_presented(self, candidates: tuple, text: str):
        if text.isdigit():
            index = int(text) - 1
            return candidates[index] if 0 <= index < len(candidates) else None
        normalized = text.replace("\\", "/").casefold()
        return next(
            (
                item
                for item in candidates
                if item.relative_path.casefold() == normalized
            ),
            None,
        )


def development_history_consult_descriptor() -> CapabilityDescriptor:
    return CapabilityDescriptor(
        name="development_history.consult",
        description="Explicit read-only consultation of ROBY development history.",
        permission_scope=PermissionScope.READ,
        initiation_policy=CapabilityInitiationPolicy.HUMAN_APPROVAL,
        effect_class=CapabilityEffectClass.READ_ONLY,
        interaction_scope=CapabilityInteractionScope.HUMAN,
    )


def build_development_history_consultation_runtime_from_environment(registry):
    source = build_development_history_source_from_environment()
    if source is None:
        return None
    runtime = DevelopmentHistoryConsultationInterceptionPort(source)
    registry.register_descriptor(
        development_history_consult_descriptor(),
        interceptor=runtime,
    )
    return runtime
