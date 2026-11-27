from __future__ import annotations

import os
import re
import shlex
import time
import unicodedata
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from core.governed_local_music import (
    GovernedLocalMusicCatalogueV1,
    GovernedLocalMusicConfig,
    GovernedLocalMusicPlaybackAuthorizationV1,
    GovernedLocalMusicSelectionV1,
    GovernedMusicSelection,
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



def local_music_command(text: str) -> str | None:
    """Recognize requests for a selection from the local music collection."""
    text = " ".join(text.casefold().strip(" ¡!¿?.,").split())
    text = re.sub(r"^roby[, ]+|[, ]+roby$", "", text)
    if re.fullmatch(r"busc[aá](?:me)? (?:algo de m[uú]sica|m[uú]sica|algo de la pinacoteca)", text):
        return "browse"
    if re.fullmatch(
        r"(?:pon[eé](?:me)?|poneme|pod[eé]|reproduc[ií](?:me)?) "
        r"(?:algo de la pinacoteca|(?:algo de )?m[uú]sica)",
        text,
    ):
        return "play"
    if re.fullmatch(
        r"(?:esto no me gusta[,.; ]+)?(?:busc[aá]|pon[eé]) otra pista", text
    ):
        return "next"
    if text == "esto no me gusta":
        return "dislike"
    return None


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
        "detené el audio",
        "detene el audio",
        "pará el audio",
        "para el audio",
        "cortá la música",
        "corta la musica",
        "dejá de reproducir",
        "deja de reproducir",
        "pará",
        "para",
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
        self._music_options = {}

    @staticmethod
    def _natural_music_query(text: str, verbs: str) -> str | None:
        match = re.fullmatch(
            rf"(?:roby[\s,:]+)?(?:{verbs})\s+(?P<subject>.+)",
            text.strip(" ¡!¿?.,"),
            flags=re.IGNORECASE,
        )
        if match is None:
            return None
        subject = re.sub(r"[, ]+roby$", "", match["subject"], flags=re.IGNORECASE)
        subject = re.sub(
            r"^(?:algo de|una (?:pista|canci[oó]n) de)\s+",
            "",
            subject,
            flags=re.IGNORECASE,
        )
        return subject.strip() or None

    def intercept(self, request: GovernedConversationPipelineRequest, *, now):
        normalized = request.text.strip().casefold()
        key = (request.owner, request.session_id)
        pending = self._music_options.pop(key, None)
        command = local_music_command(request.text)
        if command is not None:
            return self._collection_interception(command, key)
        stop_text = normalized.strip(" ¡!¿?.,")
        stop_text = re.sub(r"^roby[, ]+|[, ]+roby$", "", stop_text)
        if stop_text in self._STOP_PHRASES or stop_text in {"para", "pará"}:
            return self._stop_playback_interception()
        playback_query = self._playback_query(request.text)
        if playback_query is None:
            playback_query = self._natural_music_query(
                request.text,
                r"reproduc[i\u00ed](?:me)?|pon[e\u00e9](?:me)?|escuchemos|quiero escuchar",
            )

        if playback_query is not None:
            return self._playback_interception(playback_query, key=key)
        selection_query = self._prefixed_query(
            request.text,
            self._SELECTION_PREFIXES,
        )
        if selection_query is not None:
            return self._selection_interception(selection_query)
        query = self._search_query(request.text)
        implicit_query = self._natural_music_query(
            request.text, r"busc[aá](?:me)?\s+algo\s+de"
        ) if query is None else None
        if query or implicit_query:
            result = self.catalogue.search(query or implicit_query, max_results=10)
        if query or (implicit_query and result.matches):
            if not result.matches:
                return GovernedOperationalInterception(
                    response_text=(
                        f"No encontré coincidencias para {result.query!r} en "
                        "la colección musical autorizada."
                    ),
                    rationale="local_music_catalogue_no_match",
                )
            rows = self._offer_music_options(key, result.matches)
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

        if pending is not None and pending[0] >= time.monotonic():
            entry = self._pending_music_choice(request.text, pending[1])
            if entry is not None:
                if self.playback_executor is None:
                    return self._playback_interception(entry.relative_path)
                return self._play_authorized_selection(GovernedMusicSelection(
                    query=entry.relative_path,
                    status=GovernedMusicSelectionStatus.SELECTED,
                    selected=entry,
                    candidates=(entry,),
                    rationale="explicit_local_collection_choice",
                ))

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


    def _offer_music_options(self, key, entries):
        entries = tuple(entries)
        now = time.monotonic()
        if len(self._music_options) >= 128:
            self._music_options.pop(next(iter(self._music_options)))
        self._music_options[key] = (now + 300, entries)
        return "\n".join(
            f"{index}. {entry.relative_path}"
            for index, entry in enumerate(entries, start=1)
        )

    @staticmethod
    def _music_choice_key(text):
        text = unicodedata.normalize("NFKD", text.casefold())
        text = "".join(char for char in text if not unicodedata.combining(char))
        return " ".join(re.findall(r"[^\W_]+", text))

    def _pending_music_choice(self, text, entries):
        text = text.strip(" .,¿?¡!")
        text = re.sub(r"^roby[, ]+|[, ]+roby$", "", text, flags=re.IGNORECASE)
        text = re.sub(
            r"^(?:la|el)?\s*(?:opci[oó]n|pista|n[uú]mero)\s+",
            "", text, flags=re.IGNORECASE,
        )
        key = self._music_choice_key(text)
        if re.fullmatch(r"[0-9]{1,2}", key) and 1 <= int(key) <= len(entries):
            return entries[int(key) - 1]
        if not key:
            return None
        matches = tuple(
            item for item in entries
            if key in {
                self._music_choice_key(item.filename),
                self._music_choice_key(item.title_hint),
            }
        )
        if not matches and len(key.split()) >= 2:
            matches = tuple(
                item for item in entries
                if self._music_choice_key(item.title_hint).startswith(key + " ")
            )
        return matches[0] if len(matches) == 1 else None

    def _collection_interception(self, command, key):
        executor = self.playback_executor
        active = executor.active_path if executor is not None else None
        if command == "dislike" and active is None:
            return None

        entries = self.catalogue.catalogue().entries
        if command == "browse":
            if entries:
                rows = self._offer_music_options(key, entries[:5])
                return GovernedOperationalInterception(
                    response_text=f"Encontré estas pistas en la Pinacoteca:\n{rows}",
                    rationale="local_music_catalogue_search_completed",
                )
            message = "No encontré pistas en la Pinacoteca."
        elif executor is None:
            message = "La reproducción local no está configurada."
        elif command == "next" and active is None:
            message = "No hay una pista activa. Podés pedirme que ponga música."
        else:
            paths = tuple(self.catalogue.resolve_entry(entry.relative_path) for entry in entries)
            start = paths.index(active) + 1 if active in paths else 0
            candidates = entries[start:] + entries[:start]
            for entry in candidates:
                if self.catalogue.resolve_entry(entry.relative_path) != active:
                    selection = GovernedMusicSelection(
                        query=entry.relative_path,
                        status=GovernedMusicSelectionStatus.SELECTED,
                        selected=entry,
                        candidates=(entry,),
                        rationale="explicit_local_collection_choice",
                    )
                    return self._play_authorized_selection(selection)
            message = "No encontré otra pista en la Pinacoteca." if active else (
                "No encontré pistas en la Pinacoteca."
            )
        return GovernedOperationalInterception(
            response_text=message, rationale="local_music_collection_unavailable"
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
        query: str, *, key=None,
    ) -> GovernedOperationalInterception:
        if self.playback_executor is None:
            return GovernedOperationalInterception(
                response_text=(
                    "La reproducción local no está configurada. "
                    "El catálogo y la selección siguen disponibles."
                ),
                rationale="local_music_playback_not_configured",
            )
        return self._play_authorized_selection(self.selection.select(query), key=key)

    def _play_authorized_selection(self, selection, *, key=None):
        query = selection.query
        authorization = self.playback_authorization.authorize(
            selection,
            explicit_human_request=True,
        )
        if not authorization.authorized:
            if selection.status is GovernedMusicSelectionStatus.AMBIGUOUS:
                rows = (
                    self._offer_music_options(key, selection.candidates) if key else
                    "\n".join(f"- {item.relative_path}" for item in selection.candidates)
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
        try:
            self.playback_executor.play(path)
        except (OSError, ValueError, RuntimeError):
            return GovernedOperationalInterception(
                response_text="No pude iniciar la pista en VLC.",
                rationale="local_music_playback_failed",
            )
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
    def _playback_query(cls, text: str) -> str | None:
        # Preserve the playback commands already supported.
        query = cls._prefixed_query(text, cls._PLAYBACK_PREFIXES)
        if query is not None:
            return query

        command = (
            re.sub(
                r"^\s*(?:hola\s+)?roby\b[\s,:]*",
                "",
                text,
                count=1,
                flags=re.IGNORECASE,
            )
            .strip()
            .strip("¿")
            .strip()
        )

        match = re.fullmatch(
            r"(?:me\s+)?"
            r"(?:reproduc[íi]|reproducir|pon[eé]|pon[eé]s)"
            r"\s+(?:para\s+escuchar\s+)?"
            r"(?:(?:desde|de|en)\s+mi\s+pinacoteca\s*[:,]?\s*)?"
            r"(?P<track>.+?)"
            r"\s*[?!.]*",
            command,
            flags=re.IGNORECASE,
        )
        if match is None:
            return None

        query = match.group("track").strip()
        if not query:
            return None

        # Support “title de artist” using the catalogue's known format.
        title, separator, artist = query.rpartition(" de ")
        if separator and title.strip() and artist.strip():
            query = f"{artist.strip()} - {title.strip()}"

        return query

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
