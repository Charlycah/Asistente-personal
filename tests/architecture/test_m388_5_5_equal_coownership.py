from __future__ import annotations

from core.cognitive_maturity import COOWNER_PERMISSION_MATRIX, EQUAL_COOWNERS


def test_m388_5_5_carlos_and_cristina_are_the_only_equal_coowners() -> None:
    assert set(EQUAL_COOWNERS) == {"Carlos", "Cristina"}
    assert len(EQUAL_COOWNERS) == 2


def test_m388_5_5_every_permission_rule_uses_equal_coownership() -> None:
    assert COOWNER_PERMISSION_MATRIX
    assert all(
        rule.authorized_coowners == EQUAL_COOWNERS
        for rule in COOWNER_PERMISSION_MATRIX
    )


def test_m388_5_5_no_permission_rule_creates_a_primary_owner() -> None:
    representation = repr(COOWNER_PERMISSION_MATRIX).casefold()
    assert "primary_owner" not in representation
    assert "owner_priority" not in representation


def test_m388_5_5_technical_familia_identity_is_not_a_coowner() -> None:
    assert "Familia" not in EQUAL_COOWNERS
    assert all(
        "Familia" not in rule.authorized_coowners
        for rule in COOWNER_PERMISSION_MATRIX
    )
