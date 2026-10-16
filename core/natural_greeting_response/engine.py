from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256

from .models import (
    GreetingPeriod,
    InMemoryNaturalGreetingRepository,
    NaturalGreetingAction,
    NaturalGreetingConfig,
    NaturalGreetingRepository,
    NaturalGreetingRequest,
    NaturalGreetingResult,
    NaturalGreetingStatus,
    entry_allows_greeting,
)


class NaturalGreetingResponder:
    """Realizes a natural greeting without calling an external model."""

    _NEUTRAL_VARIANTS = (
        ("neutral_how_are_you", "Hola. Como estas?"),
        ("neutral_all_good", "Hola. Todo bien?"),
        ("neutral_plans", "Hola. Que vas a hacer hoy?"),
        ("neutral_listening", "Hola. Te escucho."),
        ("neutral_day", "Buenas. Como viene el dia?"),
    )
    _PERIOD_VARIANTS = {
        GreetingPeriod.MORNING: (
            ("morning_good_day", "Buen dia. Como estas?"),
            ("morning_plans", "Buen dia. Que vas a hacer hoy?"),
            ("morning_today", "Buen dia. Como estas hoy?"),
        ),
        GreetingPeriod.AFTERNOON: (
            ("afternoon_hello", "Hola. Como viene la tarde?"),
            ("afternoon_how_are_you", "Buenas tardes. Como estas?"),
            ("afternoon_listening", "Hola. Te escucho."),
        ),
        GreetingPeriod.EVENING: (
            ("evening_hello", "Buenas. Como estuvo el dia?"),
            ("evening_all_good", "Hola. Todo bien?"),
            ("evening_tomorrow", "Buenas. Que vas a hacer manana?"),
        ),
        GreetingPeriod.NIGHT: (
            ("night_hello", "Buenas noches. Como estas?"),
            ("night_late", "Hola. Todavia despierto?"),
            ("night_listening", "Buenas noches. Te escucho."),
        ),
    }

    def __init__(
        self,
        *,
        config: NaturalGreetingConfig | None = None,
        repository: NaturalGreetingRepository | None = None,
    ) -> None:
        self.config = config or NaturalGreetingConfig()
        self.repository = repository or InMemoryNaturalGreetingRepository()

    @property
    def last_greeting(self) -> NaturalGreetingResult | None:
        items = self.repository.list_all()
        return items[-1] if items else None

    def respond(
        self,
        request: NaturalGreetingRequest,
        *,
        now: datetime | None = None,
    ) -> NaturalGreetingResult:
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError("natural greeting timestamp must be timezone-aware")
        result = self._respond(request, timestamp)
        self.repository.add(result)
        return result

    def _respond(
        self,
        request: NaturalGreetingRequest,
        timestamp: datetime,
    ) -> NaturalGreetingResult:
        if not request.greeting_requested:
            return self._inactive(
                request,
                timestamp,
                NaturalGreetingStatus.NOT_APPLICABLE,
                NaturalGreetingAction.NONE,
                "natural_greeting_not_requested",
            )
        if not entry_allows_greeting(request.entry_result):
            return self._inactive(
                request,
                timestamp,
                NaturalGreetingStatus.WITHHELD,
                NaturalGreetingAction.WITHHOLD,
                "conversation_entry_is_not_a_greeting",
            )

        period = self._period(timestamp)
        variants = self._variants(period)
        selected_key, selected_text, repeated = self._select(
            request,
            timestamp,
            variants,
        )
        if self.config.use_owner_name and selected_key.endswith("whats_up"):
            selected_text = selected_text.replace("Hola.", f"Hola, {request.owner}.")
        if len(selected_text) > self.config.max_response_length:
            raise ValueError("natural greeting exceeds configured maximum length")
        return NaturalGreetingResult(
            request=request,
            status=NaturalGreetingStatus.GENERATED,
            action=NaturalGreetingAction.DELIVER,
            response_text=selected_text,
            period=period,
            variant_key=selected_key,
            natural=True,
            repeated_recent_response=repeated,
            provider_call_allowed=False,
            network_access_allowed=False,
            platform_mutation_allowed=False,
            rationale=("natural_greeting_generated",),
            created_at=timestamp,
        )

    def _variants(self, period: GreetingPeriod) -> tuple[tuple[str, str], ...]:
        if not self.config.allow_time_aware_greetings:
            return self._NEUTRAL_VARIANTS
        return self._PERIOD_VARIANTS.get(period, self._NEUTRAL_VARIANTS)

    def _select(
        self,
        request: NaturalGreetingRequest,
        timestamp: datetime,
        variants: tuple[tuple[str, str], ...],
    ) -> tuple[str, str, bool]:
        recent = set(request.recent_responses[-self.config.recent_response_window :])
        available = tuple(item for item in variants if item[1] not in recent)
        pool = available or variants
        payload = "|".join(
            (
                request.owner.casefold(),
                request.session_id,
                request.entry_result.entry_id,
                timestamp.date().isoformat(),
                str(timestamp.hour),
            )
        )
        index = int(sha256(payload.encode()).hexdigest(), 16) % len(pool)
        key, text = pool[index]
        return key, text, text in recent

    @staticmethod
    def _period(timestamp: datetime) -> GreetingPeriod:
        hour = timestamp.hour
        if 5 <= hour < 12:
            return GreetingPeriod.MORNING
        if 12 <= hour < 18:
            return GreetingPeriod.AFTERNOON
        if 18 <= hour < 23:
            return GreetingPeriod.EVENING
        return GreetingPeriod.NIGHT

    @staticmethod
    def _inactive(
        request: NaturalGreetingRequest,
        timestamp: datetime,
        status: NaturalGreetingStatus,
        action: NaturalGreetingAction,
        rationale: str,
    ) -> NaturalGreetingResult:
        return NaturalGreetingResult(
            request=request,
            status=status,
            action=action,
            response_text="",
            period=GreetingPeriod.NEUTRAL,
            variant_key="",
            natural=False,
            repeated_recent_response=False,
            provider_call_allowed=False,
            network_access_allowed=False,
            platform_mutation_allowed=False,
            rationale=(rationale,),
            created_at=timestamp,
        )
