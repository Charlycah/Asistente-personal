from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from threading import RLock

from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
    GovernedOperationalInterception,
)
from core.map_display import (
    MapDisplayRequest,
    MapDisplayTarget,
    MapDocumentRenderer,
    MapGeocodingProvider,
    MapPresentationMode,
    MapPresentationStatus,
    MapPresenter,
)


@dataclass(frozen=True)
class MapConversationPolicy:
    owner: str = "Carlos"
    presentation_mode: MapPresentationMode = MapPresentationMode.SYSTEM_BROWSER
    zoom: int = 16
    clarification_ttl_seconds: int = 300
    maximum_pending_sessions: int = 32

    def __post_init__(self) -> None:
        if not self.owner.strip():
            raise ValueError("map conversation owner must not be blank")
        object.__setattr__(
            self,
            "presentation_mode",
            MapPresentationMode(self.presentation_mode),
        )
        if not 1 <= self.zoom <= 20:
            raise ValueError("map conversation zoom must be between 1 and 20")
        if self.clarification_ttl_seconds < 1:
            raise ValueError("map clarification ttl must be positive")
        if self.maximum_pending_sessions < 1:
            raise ValueError("maximum pending map sessions must be positive")


@dataclass(frozen=True)
class _PendingMapClarification:
    query: str
    targets: tuple[MapDisplayTarget, ...]
    expires_at: datetime


class MapConversationInterceptionPort:
    """Connects natural-language map requests to geocoding and desktop display."""

    _QUERY_PATTERNS = (
        re.compile(
            r"\b(?:mostrame|mostrar|abr[ií]|abrir|ver)\s+"
            r"(?:un\s+|el\s+)?mapa\s+(?:de\s+)?(.+?)[?.!,]*$",
            re.IGNORECASE,
        ),
        re.compile(
            r"\b(?:mostrame|mostrar)\s+(.+?)\s+en\s+(?:el\s+)?mapa[?.!,]*$",
            re.IGNORECASE,
        ),
        re.compile(r"\b(?:d[oó]nde\s+queda)\s+(.+?)[?.!,]*$", re.IGNORECASE),
        re.compile(r"\b(?:ubicaci[oó]n\s+de)\s+(.+?)[?.!,]*$", re.IGNORECASE),
        re.compile(r"\bmapa\s+(?:de\s+)?(.+?)[?.!,]*$", re.IGNORECASE),
    )
    _ORDINALS = {
        "primera": 0,
        "primero": 0,
        "uno": 0,
        "segunda": 1,
        "segundo": 1,
        "dos": 1,
        "tercera": 2,
        "tercero": 2,
        "tres": 2,
    }
    _CANCEL_TERMS = {
        "cancelar",
        "cancelalo",
        "cancelá",
        "cancela",
        "ninguna",
        "ninguno",
        "dejalo",
        "déjalo",
    }

    def __init__(
        self,
        geocoder: MapGeocodingProvider,
        renderer: MapDocumentRenderer,
        presenter: MapPresenter,
        policy: MapConversationPolicy | None = None,
    ) -> None:
        self.geocoder = geocoder
        self.renderer = renderer
        self.presenter = presenter
        self.policy = policy or MapConversationPolicy()
        self._pending: dict[str, _PendingMapClarification] = {}
        self._pending_lock = RLock()

    @classmethod
    def is_map_request(cls, text: str) -> bool:
        normalized = " ".join(text.strip().casefold().split())
        if not normalized:
            return False
        if "mapa" in normalized:
            return True
        if "dónde queda" in normalized or "donde queda" in normalized:
            return True
        return "ubicación de" in normalized or "ubicacion de" in normalized

    @classmethod
    def extract_query(cls, text: str) -> str | None:
        compact = " ".join(text.strip().split())
        if not cls.is_map_request(compact):
            return None
        for pattern in cls._QUERY_PATTERNS:
            match = pattern.search(compact)
            if match is not None:
                query = match.group(1).strip(" .,!?")
                if query and query.casefold() not in {"el", "un", "una"}:
                    return query
        return None

    def intercept(
        self,
        request: GovernedConversationPipelineRequest,
        *,
        now: datetime | None,
    ) -> GovernedOperationalInterception | None:
        effective_now = self._effective_now(now)
        follow_up = self._intercept_pending_selection(request, effective_now)
        if follow_up is not None:
            return follow_up
        if not self.is_map_request(request.text):
            return None

        self._discard_pending(request.session_id)
        query = self.extract_query(request.text)
        if query is None:
            return self._reply(
                "Decime qué lugar querés ver en el mapa.",
                "map_conversation_location_required",
            )

        display_request = self._display_request(query)
        try:
            targets = self.geocoder.resolve(display_request)
        except Exception:
            return self._reply(
                "No pude buscar esa ubicación en este momento.",
                "map_conversation_geocoder_failed",
            )
        if not targets:
            return self._reply(
                f"No pude encontrar {query}.",
                "map_conversation_location_not_found",
            )
        if len(targets) > 1:
            choices = tuple(targets[:3])
            self._remember_pending(request.session_id, query, choices, effective_now)
            options = "; ".join(
                f"{index}. {target.label}"
                for index, target in enumerate(choices, start=1)
            )
            return self._reply(
                (
                    f"Encontré varias ubicaciones para {query}: {options}. "
                    "Decime el número o el nombre que querés."
                ),
                "map_conversation_location_ambiguous",
            )
        return self._present_target(display_request, targets[0])

    def _intercept_pending_selection(
        self,
        request: GovernedConversationPipelineRequest,
        now: datetime,
    ) -> GovernedOperationalInterception | None:
        pending = self._pending_for(request.session_id, now)
        if pending is None:
            return None
        normalized = self._normalize_selection(request.text)
        if normalized in self._CANCEL_TERMS:
            self._discard_pending(request.session_id)
            return self._reply(
                "Cancelé la selección del mapa.",
                "map_conversation_clarification_cancelled",
            )
        selected = self._select_target(normalized, pending.targets)
        if selected is None:
            if not self._looks_like_selection(normalized, pending.targets):
                return None
            return self._reply(
                "No pude identificar esa opción. Decime 1, 2, 3 o parte del nombre.",
                "map_conversation_clarification_invalid",
            )
        self._discard_pending(request.session_id)
        return self._present_target(self._display_request(pending.query), selected)

    def _present_target(
        self,
        display_request: MapDisplayRequest,
        target: MapDisplayTarget,
    ) -> GovernedOperationalInterception:
        try:
            document = self.renderer.render(display_request, target)
        except Exception:
            return self._reply(
                f"Encontré {target.label}, pero no pude generar el mapa.",
                "map_conversation_renderer_failed",
            )
        try:
            presentation = self.presenter.present(
                document,
                mode=display_request.presentation_mode,
            )
        except Exception:
            return self._reply(
                (
                    f"Generé el mapa de {target.label}, pero no pude abrirlo "
                    "automáticamente."
                ),
                "map_conversation_presenter_failed",
            )

        if presentation.status is MapPresentationStatus.PRESENTED:
            return self._reply(
                f"Abrí el mapa de {target.label}.",
                "map_conversation_completed",
            )
        if presentation.status is MapPresentationStatus.UNAVAILABLE:
            return self._reply(
                (
                    f"Generé el mapa de {target.label}, pero no pude abrirlo "
                    "automáticamente."
                ),
                "map_conversation_presentation_unavailable",
            )
        return self._reply(
            f"Generé el mapa de {target.label}, pero ocurrió un error al abrirlo.",
            "map_conversation_presentation_failed",
        )

    def _display_request(self, query: str) -> MapDisplayRequest:
        return MapDisplayRequest(
            owner=self.policy.owner,
            query=query,
            presentation_mode=self.policy.presentation_mode,
            explicit_user_request=True,
            zoom=self.policy.zoom,
        )

    def _remember_pending(
        self,
        session_id: str,
        query: str,
        targets: tuple[MapDisplayTarget, ...],
        now: datetime,
    ) -> None:
        pending = _PendingMapClarification(
            query=query,
            targets=targets,
            expires_at=now + timedelta(seconds=self.policy.clarification_ttl_seconds),
        )
        with self._pending_lock:
            self._purge_expired_locked(now)
            if (
                session_id not in self._pending
                and len(self._pending) >= self.policy.maximum_pending_sessions
            ):
                oldest = min(
                    self._pending,
                    key=lambda key: self._pending[key].expires_at,
                )
                self._pending.pop(oldest, None)
            self._pending[session_id] = pending

    def _pending_for(
        self,
        session_id: str,
        now: datetime,
    ) -> _PendingMapClarification | None:
        with self._pending_lock:
            self._purge_expired_locked(now)
            return self._pending.get(session_id)

    def _discard_pending(self, session_id: str) -> None:
        with self._pending_lock:
            self._pending.pop(session_id, None)

    def _purge_expired_locked(self, now: datetime) -> None:
        expired = [
            session_id
            for session_id, pending in self._pending.items()
            if pending.expires_at <= now
        ]
        for session_id in expired:
            self._pending.pop(session_id, None)

    @classmethod
    def _select_target(
        cls,
        normalized: str,
        targets: tuple[MapDisplayTarget, ...],
    ) -> MapDisplayTarget | None:
        index = cls._selection_index(normalized)
        if index is not None:
            return targets[index] if index < len(targets) else None
        name_query = re.sub(
            r"^(?:la|el)?\s*(?:de|del)?\s+",
            "",
            normalized,
        ).strip()
        matches = [
            target
            for target in targets
            if name_query and name_query in target.label.casefold()
        ]
        return matches[0] if len(matches) == 1 else None

    @classmethod
    def _selection_index(cls, normalized: str) -> int | None:
        compact = re.sub(r"\b(?:la|el|opci[oó]n|n[uú]mero)\b", " ", normalized)
        compact = " ".join(compact.split())
        if compact.isdigit():
            number = int(compact)
            return number - 1 if number > 0 else None
        for term, index in cls._ORDINALS.items():
            if re.search(rf"\b{re.escape(term)}\b", compact):
                return index
        return None

    @classmethod
    def _looks_like_selection(
        cls,
        normalized: str,
        targets: tuple[MapDisplayTarget, ...],
    ) -> bool:
        if cls._selection_index(normalized) is not None:
            return True
        if normalized in cls._CANCEL_TERMS:
            return True
        return any(
            word in target.label.casefold()
            for target in targets
            for word in normalized.split()
            if len(word) >= 4
        )

    @staticmethod
    def _normalize_selection(text: str) -> str:
        return " ".join(text.strip(" .,!?").casefold().split())

    @staticmethod
    def _effective_now(now: datetime | None) -> datetime:
        if now is None:
            return datetime.now(timezone.utc)
        if now.tzinfo is None:
            raise ValueError("map conversation timestamp must be timezone-aware")
        return now

    @staticmethod
    def _reply(text: str, rationale: str) -> GovernedOperationalInterception:
        return GovernedOperationalInterception(response_text=text, rationale=rationale)
