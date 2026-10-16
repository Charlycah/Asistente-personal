from __future__ import annotations

import os
import re
import shlex
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from core.governed_local_music import (
    GovernedLocalMusicCatalogueV1,
    GovernedLocalMusicConfig,
    GovernedLocalMusicPlaybackAuthorizationV1,
    GovernedLocalMusicSelectionV1,
    GovernedMusicSelectionStatus,
    governed_local_music_catalogue_read_descriptor,
    governed_local_music_playback_descriptor,
)
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
    GovernedOperationalInterception,
)

from .local_music_playback import LocalCommandMusicPlaybackExecutor
from .runtime_capability_registry import OfficialRuntimeCapabilityRegistry


class GovernedLocalMusicProvisionStatus(str, Enum):
    NOT_PROVISIONED = "not_provisioned"
    INVALID_CONFIGURATION = "invalid_configuration"
    PROVISIONED = "provisioned"


@dataclass(frozen=True)
class GovernedLocalMusicRuntimeWiring:
    status: GovernedLocalMusicProvisionStatus
    configured_root: str | None
    max_catalogue_entries: int
    catalogue: GovernedLocalMusicCatalogueV1 | None = None
    interceptor: "GovernedLocalMusicCatalogueInterceptionPort | None" = None
    selection: GovernedLocalMusicSelectionV1 | None = None
    playback_authorization: GovernedLocalMusicPlaybackAuthorizationV1 | None = None
    playback_executor: LocalCommandMusicPlaybackExecutor | None = None


class GovernedLocalMusicCatalogueInterceptionPort:
    """Expose read-only local music catalogue queries through the official registry."""

    _PLAYBACK_PREFIXES = (
        "reproducí música",
        "reproduci musica",
        "reproducir música",
        "reproducir musica",
        "poné música",
        "pone musica",
    )

    _STOP_PHRASES = (
        "detené la música",
        "detene la musica",
        "pará la música",
        "para la musica",
    )

    _SELECTION_PREFIXES = (
        "seleccioná música",
        "selecciona musica",
        "seleccionar música",
        "seleccionar musica",
        "elegí música",
        "elegi musica",
        "elegir música",
        "elegir musica",
    )

    _SEARCH_PREFIXES = (
        "buscá en mi música",
        "busca en mi musica",
        "buscar en mi música",
        "buscar en mi musica",
        "buscá música",
        "busca musica",
        "buscar música",
        "buscar musica",
    )

    def __init__(
        self,
        catalogue: GovernedLocalMusicCatalogueV1,
        selection: GovernedLocalMusicSelectionV1,
        playback_authorization: GovernedLocalMusicPlaybackAuthorizationV1,
        playback_executor: LocalCommandMusicPlaybackExecutor | None,
    ) -> None:
        self.catalogue = catalogue
        self.selection = selection
        self.playback_authorization = playback_authorization
        self.playback_executor = playback_executor

    def intercept(self, request: GovernedConversationPipelineRequest, *, now):
        normalized = request.text.strip().casefold()
        if normalized in self._STOP_PHRASES:
            return self._stop_playback_interception()
        playback_query = self._prefixed_query(
            request.text,
            self._PLAYBACK_PREFIXES,
        )
        if playback_query is not None:
            return self._playback_interception(playback_query)
        selection_query = self._prefixed_query(
            request.text,
            self._SELECTION_PREFIXES,
        )
        if selection_query is not None:
            return self._selection_interception(selection_query)
        query = self._search_query(request.text)
        if query is not None:
            result = self.catalogue.search(query, max_results=10)
            if not result.matches:
                return GovernedOperationalInterception(
                    response_text=(
                        f"No encontré coincidencias para {result.query!r} en "
                        "la colección musical autorizada."
                    ),
                    rationale="local_music_catalogue_no_match",
                )
            rows = "\n".join(f"- {item.relative_path}" for item in result.matches)
            suffix = (
                "\nLa búsqueda quedó acotada por el límite del catálogo."
                if result.bounded
                else ""
            )
            return GovernedOperationalInterception(
                response_text=(
                    "Encontré estas pistas en la colección musical autorizada:\n"
                    f"{rows}{suffix}"
                ),
                rationale="local_music_catalogue_search_completed",
            )

        catalogue = self.catalogue.catalogue()
        if not any(
            trigger in normalized
            for trigger in (
                "catálogo de música",
                "catalogo de musica",
                "mi música",
                "mi musica",
                "música local",
                "musica local",
            )
        ):
            return None
        return GovernedOperationalInterception(
            response_text=(
                "La colección musical autorizada contiene "
                f"{len(catalogue.entries)} pista(s) catalogada(s)."
                + (
                    " El catálogo está truncado por el límite configurado."
                    if catalogue.truncated
                    else ""
                )
            ),
            rationale="local_music_catalogue_summary_completed",
        )

    def _stop_playback_interception(self) -> GovernedOperationalInterception:
        if self.playback_executor is None:
            return GovernedOperationalInterception(
                response_text="La reproducción local no está configurada.",
                rationale="local_music_playback_stop_not_configured",
            )
        result = self.playback_executor.stop()
        if not result.stopped:
            return GovernedOperationalInterception(
                response_text="No hay una reproducción local activa para detener.",
                rationale="local_music_playback_stop_no_owned_process",
            )
        return GovernedOperationalInterception(
            response_text="Detuve la música local.",
            rationale="local_music_playback_stopped_after_explicit_request",
        )

    def _playback_interception(
        self,
        query: str,
    ) -> GovernedOperationalInterception:
        if self.playback_executor is None:
            return GovernedOperationalInterception(
                response_text=(
                    "La reproducción local no está configurada. "
                    "El catálogo y la selección siguen disponibles."
                ),
                rationale="local_music_playback_not_configured",
            )
        selection = self.selection.select(query)
        authorization = self.playback_authorization.authorize(
            selection,
            explicit_human_request=True,
        )
        if not authorization.authorized:
            if selection.status is GovernedMusicSelectionStatus.AMBIGUOUS:
                rows = "\n".join(
                    f"- {item.relative_path}" for item in selection.candidates
                )
                return GovernedOperationalInterception(
                    response_text=(
                        "No inicié reproducción porque hay varias opciones:\n"
                        f"{rows}\nIndicame cuál querés reproducir."
                    ),
                    rationale="local_music_playback_disambiguation_required",
                )
            return GovernedOperationalInterception(
                response_text=(
                    f"No encontré una pista única para {query!r}; "
                    "no inicié reproducción."
                ),
                rationale="local_music_playback_not_authorized",
            )

        assert selection.selected is not None
        path = self.catalogue.resolve_entry(selection.selected.relative_path)
        self.playback_executor.play(path)
        return GovernedOperationalInterception(
            response_text=f"Reproduciendo {selection.selected.relative_path}.",
            rationale="local_music_playback_started_after_explicit_authorization",
        )

    def _selection_interception(
        self,
        query: str,
    ) -> GovernedOperationalInterception:
        result = self.selection.select(query)
        if result.status is GovernedMusicSelectionStatus.NOT_FOUND:
            return GovernedOperationalInterception(
                response_text=(
                    f"No encontré una pista para {result.query!r} en "
                    "la colección musical autorizada."
                ),
                rationale="local_music_selection_not_found",
            )
        if result.status is GovernedMusicSelectionStatus.AMBIGUOUS:
            rows = "\n".join(f"- {item.relative_path}" for item in result.candidates)
            return GovernedOperationalInterception(
                response_text=(
                    f"Encontré varias opciones. Decime cuál querés seleccionar:\n{rows}"
                ),
                rationale="local_music_selection_requires_disambiguation",
            )
        assert result.selected is not None
        return GovernedOperationalInterception(
            response_text=(
                f"Seleccioné {result.selected.relative_path}. "
                "La selección no autoriza ni inicia reproducción."
            ),
            rationale="local_music_selection_completed_without_playback",
        )

    @classmethod
    def _prefixed_query(
        cls,
        text: str,
        prefixes: tuple[str, ...],
    ) -> str | None:
        normalized = text.strip().casefold()
        for prefix in prefixes:
            index = normalized.find(prefix)
            if index < 0:
                continue
            query = text[index + len(prefix) :]
            query = re.sub(r"^[\s:,-]+", "", query).strip()
            return query or None
        return None

    @classmethod
    def _search_query(cls, text: str) -> str | None:
        return cls._prefixed_query(text, cls._SEARCH_PREFIXES)


def build_governed_local_music_runtime_from_environment(
    capability_registry: OfficialRuntimeCapabilityRegistry,
) -> GovernedLocalMusicRuntimeWiring:
    root_value = os.getenv("ROBY_LOCAL_MUSIC_ROOT", "").strip()
    max_entries = _max_catalogue_entries_from_environment()
    if not root_value:
        return GovernedLocalMusicRuntimeWiring(
            status=GovernedLocalMusicProvisionStatus.NOT_PROVISIONED,
            configured_root=None,
            max_catalogue_entries=max_entries,
        )

    configured_root = str(Path(root_value).expanduser())
    try:
        catalogue = GovernedLocalMusicCatalogueV1(
            GovernedLocalMusicConfig(
                root=Path(configured_root),
                max_catalogue_entries=max_entries,
            )
        )
    except (OSError, PermissionError, ValueError):
        return GovernedLocalMusicRuntimeWiring(
            status=GovernedLocalMusicProvisionStatus.INVALID_CONFIGURATION,
            configured_root=configured_root,
            max_catalogue_entries=max_entries,
        )

    selection = GovernedLocalMusicSelectionV1(catalogue)
    playback_authorization = GovernedLocalMusicPlaybackAuthorizationV1()
    playback_command = _playback_command_from_environment()
    playback_executor = (
        LocalCommandMusicPlaybackExecutor(playback_command)
        if playback_command
        else None
    )
    interceptor = GovernedLocalMusicCatalogueInterceptionPort(
        catalogue,
        selection,
        playback_authorization,
        playback_executor,
    )
    capability_registry.register_descriptor(
        governed_local_music_catalogue_read_descriptor(),
        interceptor=interceptor,
    )
    if playback_executor is not None:
        capability_registry.register_descriptor(
            governed_local_music_playback_descriptor(),
            interceptor=interceptor,
        )
    return GovernedLocalMusicRuntimeWiring(
        status=GovernedLocalMusicProvisionStatus.PROVISIONED,
        configured_root=configured_root,
        max_catalogue_entries=max_entries,
        catalogue=catalogue,
        interceptor=interceptor,
        selection=selection,
        playback_authorization=playback_authorization,
        playback_executor=playback_executor,
    )


def _playback_command_from_environment() -> tuple[str, ...]:
    raw = os.getenv("ROBY_LOCAL_MUSIC_PLAYBACK_COMMAND", "").strip()
    if not raw:
        return ()
    return tuple(shlex.split(raw, posix=os.name != "nt"))


def _max_catalogue_entries_from_environment() -> int:
    raw = os.getenv("ROBY_LOCAL_MUSIC_MAX_CATALOGUE_ENTRIES", "").strip()
    if not raw:
        return 20_000
    try:
        value = int(raw)
    except ValueError:
        return 20_000
    return value if value > 0 else 20_000
