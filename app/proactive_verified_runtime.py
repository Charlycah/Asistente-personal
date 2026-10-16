from __future__ import annotations

import hashlib
import json
import os
import re
import threading
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Protocol

from app.current_affairs_router import CurrentAffairsItem, GoogleNewsRSSClient
from app.response_presenter import ResponsePresentation, ResponsePresenter


class NewsSearchPort(Protocol):
    def search(
        self,
        query: str,
        *,
        limit: int = 5,
    ) -> tuple[CurrentAffairsItem, ...]: ...


class GmailAnnouncementPort(Protocol):
    def announce(self): ...


class SourceConstraintPort(Protocol):
    def allows_external_sources(self) -> bool: ...


@dataclass(frozen=True)
class ProactiveVerifiedPolicy:
    poll_interval: timedelta = timedelta(minutes=15)
    max_news_age: timedelta = timedelta(hours=18)
    max_news_per_cycle: int = 1
    spontaneous_news_enabled: bool = True
    quiet_start_hour: int = 23
    quiet_end_hour: int = 8
    state_path: Path = Path(".roby/proactive_verified_state.json")

    def __post_init__(self) -> None:
        if self.poll_interval.total_seconds() <= 0:
            raise ValueError("proactive poll interval must be positive")
        if self.max_news_age.total_seconds() <= 0:
            raise ValueError("proactive news age must be positive")
        if self.max_news_per_cycle <= 0:
            raise ValueError("proactive news limit must be positive")


@dataclass(frozen=True)
class ProactiveVerifiedSnapshot:
    cycles: int
    notifications: int
    failures: int
    running: bool


class ProactiveVerifiedRuntime:
    """Periodically surfaces only fresh, sourced and previously unseen information."""

    NEWS_QUERY = (
        'Argentina (urgente OR "último momento" OR política OR economía OR '
        "ciencia OR NASA OR salud OR Boca OR River OR fútbol OR tormenta OR "
        "terremoto) when:1d"
    )
    _HIGH_VALUE = re.compile(
        r"\b(urgente|último momento|ultima hora|alerta|evacuaci[oó]n|"
        r"terremoto|sismo|tormenta|temporal|inundaci[oó]n|incendio|"
        r"nasa|descubrimiento|boca|river|partido|f[uú]tbol|gobierno|"
        r"presidente|congreso|senado|diputados|inflaci[oó]n|d[oó]lar|"
        r"salud|hospital|brote|vacuna)\b",
        re.IGNORECASE,
    )
    _IMPORTANT_MAIL = re.compile(
        r"\b(turno|consulta|consultorio|m[eé]dic[oa]|doctor|doctora|"
        r"hospital|estudio|laboratorio|resultado|receta|medicamento|"
        r"vencimiento|vence|pago|factura|deuda|tr[aá]mite|cancelad[oa]|"
        r"reprogramad[oa]|confirmaci[oó]n|urgente|seguridad|alerta)\b",
        re.IGNORECASE,
    )

    def __init__(
        self,
        *,
        notify: Callable[[str], None],
        news_client: NewsSearchPort | None = None,
        gmail_announcer: GmailAnnouncementPort | None = None,
        policy: ProactiveVerifiedPolicy | None = None,
        now: Callable[[], datetime] | None = None,
        source_constraint: SourceConstraintPort | None = None,
    ) -> None:
        self.notify = notify
        self.news_client = news_client or GoogleNewsRSSClient(timeout_seconds=8.0)
        self.gmail_announcer = gmail_announcer
        self.policy = policy or ProactiveVerifiedPolicy()
        self._now = now or (lambda: datetime.now(timezone.utc))
        self._source_constraint = source_constraint
        self._seen = self._load_seen()
        self._cycles = 0
        self._notifications = 0
        self._failures = 0
        self._running = False
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None

    @property
    def snapshot(self) -> ProactiveVerifiedSnapshot:
        return ProactiveVerifiedSnapshot(
            cycles=self._cycles,
            notifications=self._notifications,
            failures=self._failures,
            running=self._running,
        )

    def start(self) -> None:
        if self._running:
            return
        self._stop.clear()
        self._running = True
        self._thread = threading.Thread(
            target=self._run,
            name="roby-proactive-verified-runtime",
            daemon=True,
        )
        self._thread.start()

    def stop(self) -> None:
        if not self._running:
            return
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=2.0)
        self._thread = None
        self._running = False

    def tick(self) -> tuple[str, ...]:
        now = self._now()
        self._cycles += 1
        messages: list[str] = []
        messages.extend(self._important_mail_messages())
        if (
            self.policy.spontaneous_news_enabled
            and not self._quiet_hours(now)
            and self._external_sources_allowed()
        ):
            messages.extend(self._fresh_news_messages(now))
        for message in messages:
            self.notify(message)
            self._notifications += 1
        if messages:
            self._save_seen()
        return tuple(messages)


    def _external_sources_allowed(self) -> bool:
        if self._source_constraint is None:
            return True
        return bool(self._source_constraint.allows_external_sources())

    def _run(self) -> None:
        # A short initial pause lets startup and greeting finish first.
        if self._stop.wait(20.0):
            return
        interval = self.policy.poll_interval.total_seconds()
        while not self._stop.is_set():
            try:
                self.tick()
            except (OSError, RuntimeError, ValueError, TypeError, json.JSONDecodeError):
                self._failures += 1
            self._stop.wait(interval)

    def _important_mail_messages(self) -> list[str]:
        if self.gmail_announcer is None:
            return []
        result = self.gmail_announcer.announce()
        subjects = tuple(getattr(result, "subjects", ()))
        messages: list[str] = []
        for subject in subjects:
            clean = " ".join(str(subject).split()).strip()
            if not clean or not self._IMPORTANT_MAIL.search(clean):
                continue
            key = self._key("mail", clean.casefold())
            if key in self._seen:
                continue
            self._seen.add(key)
            messages.append(f"Te aviso algo relevante que llegó por correo: {clean}.")
            break
        return messages

    def _fresh_news_messages(self, now: datetime) -> list[str]:
        items = self.news_client.search(self.NEWS_QUERY, limit=10)
        accepted: list[CurrentAffairsItem] = []
        current = _aware_utc(now)
        for item in items:
            if item.published_at is None or not item.source.strip() or not item.url:
                continue
            published = _aware_utc(item.published_at)
            age = current - published
            if age < timedelta() or age > self.policy.max_news_age:
                continue
            if not self._HIGH_VALUE.search(item.title):
                continue
            key = self._key("news", f"{item.title.casefold()}|{item.source.casefold()}")
            if key in self._seen:
                continue
            self._seen.add(key)
            accepted.append(item)
            if len(accepted) >= self.policy.max_news_per_cycle:
                break
        return [self._render_news(item) for item in accepted]

    @staticmethod
    def _render_news(item: CurrentAffairsItem) -> str:
        published = _aware_utc(item.published_at).astimezone(
            timezone(timedelta(hours=-3))
        )
        stamp = published.strftime("%d/%m/%Y a las %H:%M")
        body = (
            f"Te comento una novedad actual que puede interesarte: {item.title}. "
            f"Publicado el {stamp}. Fuente: {item.source}."
        )
        return ResponsePresenter().present(
            ResponsePresentation(
                body=body,
                source=item.source,
                link=item.url,
            )
        )

    def _quiet_hours(self, now: datetime) -> bool:
        local = _aware_utc(now).astimezone(timezone(timedelta(hours=-3)))
        start = self.policy.quiet_start_hour
        end = self.policy.quiet_end_hour
        if start == end:
            return False
        if start < end:
            return start <= local.hour < end
        return local.hour >= start or local.hour < end

    @staticmethod
    def _key(kind: str, value: str) -> str:
        digest = hashlib.sha256(value.encode("utf-8")).hexdigest()
        return f"{kind}:{digest}"

    def _load_seen(self) -> set[str]:
        path = self.policy.state_path
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (FileNotFoundError, OSError, json.JSONDecodeError):
            return set()
        values = payload.get("seen", ()) if isinstance(payload, dict) else ()
        return {str(value) for value in values}

    def _save_seen(self) -> None:
        path = self.policy.state_path
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(path.suffix + ".tmp")
        temporary.write_text(
            json.dumps({"seen": sorted(self._seen)[-1000:]}, indent=2),
            encoding="utf-8",
        )
        temporary.replace(path)


def build_proactive_verified_runtime_from_environment(
    *,
    notify: Callable[[str], None],
    gmail_announcer=None,
    source_constraint: SourceConstraintPort | None = None,
) -> ProactiveVerifiedRuntime | None:
    if not _env_bool("ROBY_PERSONAL_RUNTIME_ENABLED", True):
        return None
    if not _env_bool("ROBY_PROACTIVE_VERIFIED_ENABLED", True):
        return None
    return ProactiveVerifiedRuntime(
        notify=notify,
        gmail_announcer=gmail_announcer,
        source_constraint=source_constraint,
        policy=ProactiveVerifiedPolicy(
            poll_interval=timedelta(
                seconds=_env_float("ROBY_PROACTIVE_VERIFIED_POLL_SECONDS", 900.0)
            ),
            max_news_age=timedelta(
                hours=_env_float("ROBY_PROACTIVE_VERIFIED_MAX_NEWS_HOURS", 18.0)
            ),
            max_news_per_cycle=_env_int("ROBY_PROACTIVE_VERIFIED_MAX_NEWS", 1),
            spontaneous_news_enabled=False,
            quiet_start_hour=_env_int("ROBY_PROACTIVE_QUIET_START_HOUR", 23),
            quiet_end_hour=_env_int("ROBY_PROACTIVE_QUIET_END_HOUR", 8),
            state_path=Path(
                os.getenv(
                    "ROBY_PROACTIVE_VERIFIED_STATE_PATH",
                    ".roby/proactive_verified_state.json",
                )
            ),
        ),
    )


def _aware_utc(value: datetime | None) -> datetime:
    if value is None:
        return datetime.now(timezone.utc)
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name, "").strip()
    return default if not raw else raw.casefold() in {"1", "true", "yes", "on"}


def _env_float(name: str, default: float) -> float:
    raw = os.getenv(name, "").strip()
    return default if not raw else float(raw)


def _env_int(name: str, default: int) -> int:
    raw = os.getenv(name, "").strip()
    return default if not raw else int(raw)
