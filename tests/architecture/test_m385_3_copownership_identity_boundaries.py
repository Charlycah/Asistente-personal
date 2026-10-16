from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from application.brain import (
    ActiveIdentityRequest,
    ActiveIdentityResolver,
    ActiveIdentityStatus,
)
from application.reminders import ReminderConversationService
from core.identity import ROBYIdentity
from core.local_identity_profile import (
    LocalIdentityProfile,
    LocalIdentityProfileStore,
)
from core.personal_identity_and_session_profiles import (
    JsonIdentityProfileStore,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PRODUCTION_PACKAGES = (
    "app",
    "application",
    "core",
    "domain",
    "infrastructure",
)
LEGACY_FREEFORM_MEMORY_OWNER_FILE = "app/memory_consolidation.py"
NOW = datetime(2026, 8, 5, 12, 0, tzinfo=timezone.utc)


def _production_python_files() -> tuple[Path, ...]:
    files: list[Path] = []
    for package in PRODUCTION_PACKAGES:
        files.extend((PROJECT_ROOT / package).rglob("*.py"))
    return tuple(sorted(files))


def _relative(path: Path) -> str:
    return path.relative_to(PROJECT_ROOT).as_posix()


def _resolver_with_only_the_two_coowners(tmp_path: Path) -> ActiveIdentityResolver:
    local_store = LocalIdentityProfileStore(tmp_path / "profile.toml")
    local_store.save(
        LocalIdentityProfile(owner_name="Carlos", partner_name="Cristina")
    )
    profile_path = tmp_path / "identity" / "profiles.json"
    profile_path.parent.mkdir(parents=True)
    profile_path.write_text(
        json.dumps(
            {
                "profiles": [
                    {
                        "profile_id": "carlos",
                        "display_name": "Carlos",
                        "owner": "Carlos",
                        "scope": "private",
                        "participants": [],
                    },
                    {
                        "profile_id": "cristina",
                        "display_name": "Cristina",
                        "owner": "Cristina",
                        "scope": "private",
                        "participants": [],
                    },
                ]
            }
        ),
        encoding="utf-8",
    )
    return ActiveIdentityResolver(
        local_profile_store=local_store,
        identity_profile_store=JsonIdentityProfileStore(profile_path),
    )


def test_roby_recognizes_exactly_carlos_and_cristina_as_people() -> None:
    identity = ROBYIdentity()

    assert identity.member_names == ("Carlos", "Cristina")
    assert len(set(identity.member_names)) == 2
    assert "Familia" not in identity.member_names


def test_retired_joint_identity_markers_are_absent_from_production() -> None:
    markers = ('"Familia"', '"family-shared"', '"household-main"')
    observed = {
        _relative(path)
        for path in _production_python_files()
        if any(marker in path.read_text(encoding="utf-8") for marker in markers)
    }

    assert observed == set()


def test_no_persistence_schema_names_familia_as_a_person_or_owner() -> None:
    persistence_roots = (
        PROJECT_ROOT / "infrastructure" / "persistence",
        PROJECT_ROOT / "infrastructure" / "repositories",
    )
    sources = "\n".join(
        path.read_text(encoding="utf-8")
        for root in persistence_roots
        for path in root.rglob("*.py")
    )

    assert '"Familia"' not in sources
    assert "'Familia'" not in sources
    assert "family-shared" not in sources


def test_active_identity_resolver_needs_explicit_non_biometric_evidence(
    tmp_path: Path,
) -> None:
    resolver = _resolver_with_only_the_two_coowners(tmp_path)

    unknown = resolver.resolve(ActiveIdentityRequest())
    carlos = resolver.resolve(ActiveIdentityRequest(declared_name="Carlos"))
    cristina = resolver.resolve(ActiveIdentityRequest(declared_name="Cristina"))

    assert unknown.status is ActiveIdentityStatus.UNKNOWN
    assert unknown.subject is None
    assert carlos.status is ActiveIdentityStatus.RESOLVED
    assert carlos.subject == "Carlos"
    assert cristina.status is ActiveIdentityStatus.RESOLVED
    assert cristina.subject == "Cristina"


def test_conflicting_interlocutor_evidence_is_never_guessed(tmp_path: Path) -> None:
    resolver = _resolver_with_only_the_two_coowners(tmp_path)

    result = resolver.resolve(
        ActiveIdentityRequest(
            profile_id="carlos",
            declared_name="Cristina",
        )
    )

    assert result.status is ActiveIdentityStatus.CONFLICT
    assert result.may_use_private_preferences is False


def test_reminders_keep_joint_access_without_a_private_owner_boundary(
    tmp_path: Path,
) -> None:
    service = ReminderConversationService(tmp_path / "reminders.db")
    service.handle(
        owner="Carlos",
        text="recordame comprar pan mañana a las 10",
        now=NOW,
    )

    listed = service.handle(
        owner="Cristina",
        text="qué recordatorios tengo",
        now=NOW,
    )

    assert "comprar pan" in listed.response_text


def test_health_surfaces_name_people_individually_not_as_familia() -> None:
    health_modules = (
        "app/allergy_registry.py",
        "app/chronic_condition_registry.py",
        "app/emergency_contacts.py",
        "app/secure_health_checkups.py",
        "app/secure_medication_registry.py",
        "app/structured_symptom_registry.py",
        "app/vital_sign_history.py",
    )

    for relative in health_modules:
        source = (PROJECT_ROOT / relative).read_text(encoding="utf-8")
        assert '"carlos": "Carlos"' in source
        assert '"cristina": "Cristina"' in source
        assert '"familia": "Familia"' not in source


def test_freeform_memory_owner_creation_is_quarantined_to_one_legacy_gateway() -> None:
    markers = ("_PROFILE_PREFIXES", "explicit_profile_conversation")
    observed = {
        _relative(path)
        for path in _production_python_files()
        if any(marker in path.read_text(encoding="utf-8") for marker in markers)
    }

    assert observed == {LEGACY_FREEFORM_MEMORY_OWNER_FILE}


def test_household_scope_is_not_modelled_as_a_third_person_in_goals_projects() -> None:
    for relative in (
        "core/household_goals.py",
        "core/household_projects.py",
    ):
        source = (PROJECT_ROOT / relative).read_text(encoding="utf-8")
        assert 'owner: str' not in source
        assert '"Familia"' not in source
        assert '"family-shared"' not in source


def test_m236_records_equal_joint_reminder_access() -> None:
    document = (
        PROJECT_ROOT / "docs" / "milestones" / "M236_HOUSEHOLD_IDENTITY_RUNTIME.md"
    ).read_text(encoding="utf-8")

    assert "Carlos and Cristina as one shared household identity" in document
    assert "There is no private owner boundary between them" in document
    assert "Legacy owner fields" in document
