from __future__ import annotations

from pathlib import Path

from infrastructure.system import private_file_permissions as permissions


def test_windows_file_acl_removes_inheritance_and_grants_current_user(
    monkeypatch,
) -> None:
    calls: list[tuple[Path, tuple[str, ...]]] = []
    path = Path("token.json")
    monkeypatch.setattr(permissions, "_windows_principal", lambda: "HOST\\Carlos")
    monkeypatch.setattr(
        permissions,
        "_run_icacls",
        lambda target, *arguments: calls.append((target, arguments)),
    )

    permissions._harden_windows_acl(path, directory=False)

    assert calls == [
        (path, ("/inheritance:r",)),
        (path, ("/grant:r", "HOST\\Carlos:F")),
    ]


def test_windows_directory_acl_grant_inherits_to_children(monkeypatch) -> None:
    calls: list[tuple[Path, tuple[str, ...]]] = []
    path = Path("vault")
    monkeypatch.setattr(permissions, "_windows_principal", lambda: "HOST\\Carlos")
    monkeypatch.setattr(
        permissions,
        "_run_icacls",
        lambda target, *arguments: calls.append((target, arguments)),
    )

    permissions._harden_windows_acl(path, directory=True)

    assert calls[-1] == (
        path,
        ("/grant:r", "HOST\\Carlos:(OI)(CI)F"),
    )
