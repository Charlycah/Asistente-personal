from datetime import datetime, timedelta, timezone
from pathlib import Path

from app.current_affairs_router import CurrentAffairsItem
from app.proactive_verified_runtime import (
    ProactiveVerifiedPolicy,
    ProactiveVerifiedRuntime,
)


class NewsClient:
    def __init__(self, items):
        self.items = items

    def search(self, query, *, limit=5):
        return tuple(self.items[:limit])


class GmailResult:
    subjects = ("Recuerde su turno médico agendado para mañana", "Promoción")


class GmailAnnouncer:
    def announce(self):
        return GmailResult()


def item(now):
    return CurrentAffairsItem(
        title="Boca juega hoy y confirmó el horario del partido",
        source="Medio Deportivo",
        url="https://example.com/boca",
        published_at=now - timedelta(minutes=30),
    )


def test_m310_announces_relevant_mail_and_sourced_fresh_news(tmp_path: Path):
    now = datetime(2026, 7, 23, 18, tzinfo=timezone.utc)
    delivered = []
    runtime = ProactiveVerifiedRuntime(
        notify=delivered.append,
        news_client=NewsClient([item(now)]),
        gmail_announcer=GmailAnnouncer(),
        now=lambda: now,
        policy=ProactiveVerifiedPolicy(state_path=tmp_path / "state.json"),
    )

    messages = runtime.tick()

    assert len(messages) == 2
    assert "turno médico" in messages[0]
    assert "Fuente: Medio Deportivo" in messages[1]
    assert "23/07/2026" in messages[1]
    assert "https://example.com/boca" not in messages[1]
    assert "Enlace:" not in messages[1]


def test_m310_does_not_repeat_the_same_information(tmp_path: Path):
    now = datetime(2026, 7, 23, 18, tzinfo=timezone.utc)
    delivered = []
    runtime = ProactiveVerifiedRuntime(
        notify=delivered.append,
        news_client=NewsClient([item(now)]),
        gmail_announcer=GmailAnnouncer(),
        now=lambda: now,
        policy=ProactiveVerifiedPolicy(state_path=tmp_path / "state.json"),
    )

    assert len(runtime.tick()) == 2
    assert runtime.tick() == ()


def test_m310_rejects_old_or_undated_news(tmp_path: Path):
    now = datetime(2026, 7, 23, 18, tzinfo=timezone.utc)
    old = CurrentAffairsItem(
        title="Boca juega un partido",
        source="Medio Deportivo",
        url="https://example.com/old",
        published_at=now - timedelta(days=3),
    )
    undated = CurrentAffairsItem(
        title="River confirmó un partido",
        source="Medio Deportivo",
        url="https://example.com/undated",
        published_at=None,
    )
    runtime = ProactiveVerifiedRuntime(
        notify=lambda text: None,
        news_client=NewsClient([old, undated]),
        now=lambda: now,
        policy=ProactiveVerifiedPolicy(state_path=tmp_path / "state.json"),
    )

    assert runtime.tick() == ()
