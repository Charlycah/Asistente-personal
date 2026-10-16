from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from core.personal_identity_and_session_profiles import (
    PersonalIdentityProfile,
    RuntimeSessionProfile,
)

from .household_always_on_bootstrap import bootstrap_household


@dataclass(frozen=True)
class SelectedRuntimeIdentity:
    profile: PersonalIdentityProfile
    session: RuntimeSessionProfile
    state_path: Path


def select_runtime_identity_from_environment() -> SelectedRuntimeIdentity:
    """Return ROBY's permanent household identity without user-visible selection."""
    base_path = Path(os.getenv("ROBY_PROFILE_DATA_PATH", ".roby/identity"))
    result = bootstrap_household(base_path=base_path, project_root=Path.cwd())
    return SelectedRuntimeIdentity(
        profile=result.profile,
        session=result.session,
        state_path=result.state_path,
    )
