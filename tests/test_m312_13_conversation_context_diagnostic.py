from __future__ import annotations

from application.brain import (
    ConversationContextDiagnostic,
    ConversationContextItem,
    ConversationContextPackage,
)


def _item(
    memory_id: str = "memory-1",
    *,
    subject: str = "Carlos",
    text: str = "Carlos prefiere respuestas breves.",
) -> ConversationContextItem:
    return ConversationContextItem(
        memory_id=memory_id,
        subject=subject,
        memory_type="preference",
        text=text,
        source="brain",
    )


def _package(
    *items: ConversationContextItem,
    character_count: int | None = None,
    max_items: int = 8,
    max_characters: int = 1600,
    omitted_count: int = 0,
) -> ConversationContextPackage:
    actual_characters = sum(len(item.text) for item in items)
    return ConversationContextPackage(
        identity_status="resolved",
        active_subject="Carlos",
        allowed_subjects=("Carlos", "Familia"),
        private_context_enabled=True,
        items=items,
        omitted_count=omitted_count,
        character_count=(
            actual_characters if character_count is None else character_count
        ),
        max_items=max_items,
        max_characters=max_characters,
    )


def test_m312_13_reports_healthy_package_integrity() -> None:
    report = ConversationContextDiagnostic.inspect_package(_package(_item()))

    assert report.is_healthy is True
    assert report.actual_item_count == 1
    assert report.findings[0].code == "package_integrity_ok"
    assert report.to_dict()["status"] == {
        "healthy": True,
        "finding_count": 1,
    }


def test_m312_13_detects_declared_character_count_mismatch() -> None:
    report = ConversationContextDiagnostic.inspect_package(
        _package(_item(), character_count=1)
    )

    assert report.is_healthy is False
    assert "character_count_mismatch" in {
        finding.code for finding in report.findings
    }


def test_m312_13_detects_limit_violations() -> None:
    report = ConversationContextDiagnostic.inspect_package(
        _package(
            _item("memory-1", text="12345"),
            _item("memory-2", text="67890"),
            max_items=1,
            max_characters=8,
        )
    )

    codes = {finding.code for finding in report.findings}
    assert report.is_healthy is False
    assert "item_limit_exceeded" in codes
    assert "character_limit_exceeded" in codes


def test_m312_13_detects_duplicate_ids_and_disallowed_subjects() -> None:
    report = ConversationContextDiagnostic.inspect_package(
        _package(
            _item("same"),
            _item("same", subject="Cristina"),
        )
    )

    assert report.duplicate_memory_ids == ("same",)
    assert report.disallowed_subjects == ("Cristina",)
    assert {finding.code for finding in report.findings} >= {
        "duplicate_memory_ids",
        "disallowed_subjects",
    }


def test_m312_13_diagnostic_does_not_mutate_package() -> None:
    package = _package(_item())
    before = package.to_dict()

    ConversationContextDiagnostic.inspect_package(package)

    assert package.to_dict() == before
