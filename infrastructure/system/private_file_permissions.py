from __future__ import annotations

import os
import subprocess
from pathlib import Path


def harden_private_path(path: Path, *, directory: bool = False) -> None:
    """Restrict a local secret path to the current account."""
    if os.name == "posix":
        path.chmod(0o700 if directory else 0o600)
        return
    if os.name == "nt":
        _harden_windows_acl(path, directory=directory)


def private_path_is_restrictive(path: Path, *, directory: bool = False) -> bool:
    """Return whether the active platform's private-path contract is met."""
    if os.name == "posix":
        expected = 0o700 if directory else 0o600
        return path.stat().st_mode & 0o777 == expected
    if os.name == "nt":
        return _windows_acl_is_restrictive(path)
    return True


def _harden_windows_acl(path: Path, *, directory: bool) -> None:
    principal = _windows_principal()
    permission = "(OI)(CI)F" if directory else "F"
    _run_icacls(path, "/inheritance:r")
    _run_icacls(path, "/grant:r", f"{principal}:{permission}")


def _windows_acl_is_restrictive(path: Path) -> bool:
    principal = _windows_principal().casefold()
    result = _run_icacls(path)
    output = result.stdout.casefold()
    return principal in output and "(i)" not in output


def _windows_principal() -> str:
    try:
        result = subprocess.run(
            ["whoami"],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise OSError("unable to identify current Windows principal") from exc
    principal = result.stdout.strip()
    if not principal:
        raise OSError("current Windows principal is unavailable")
    return principal


def _run_icacls(path: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            ["icacls", str(path), *arguments],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise OSError(f"unable to secure local path: {path.name}") from exc
