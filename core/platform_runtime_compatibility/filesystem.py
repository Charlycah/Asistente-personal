from __future__ import annotations

import os
import stat
from pathlib import Path


def apply_private_file_permissions(path: Path | str) -> None:
    """Apply the strongest portable owner-only file mode available.

    POSIX provides exact 0600 semantics. Windows' Python mode bits do not model
    NTFS ACLs, so chmod is limited to ensuring the file remains owner writable;
    access control is inherited from the user's private runtime directory.
    """

    target = Path(path)
    if os.name == "nt":
        os.chmod(target, stat.S_IREAD | stat.S_IWRITE)
        return
    os.chmod(target, 0o600)


def private_file_is_protected(path: Path | str) -> bool:
    """Return whether ROBY applied the platform's private-file policy."""

    target = Path(path)
    if not target.is_file():
        return False
    if os.name == "nt":
        # Windows does not expose NTFS ACLs through st_mode. A writable regular
        # file beneath ROBY's per-user data directory is the portable invariant.
        return os.access(target, os.R_OK | os.W_OK)
    return target.stat().st_mode & 0o777 == 0o600
