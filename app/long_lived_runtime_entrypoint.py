from __future__ import annotations

import os
from datetime import timedelta

from core.end_to_end_local_conversation import EndToEndLocalConversation
from core.long_lived_runtime_lifecycle import (
    LongLivedRuntimeConfig,
    LongLivedRuntimeLifecycle,
)


def build_long_lived_lifecycle_from_environment(
    runtime: EndToEndLocalConversation,
) -> LongLivedRuntimeLifecycle:
    interval = float(os.getenv("ROBY_RUNTIME_HEARTBEAT_SECONDS", "30"))
    stale = float(os.getenv("ROBY_RUNTIME_STALE_SECONDS", "120"))
    return LongLivedRuntimeLifecycle(
        bootstrap=runtime.bootstrap,
        config=LongLivedRuntimeConfig(
            lease_path=os.getenv("ROBY_RUNTIME_LEASE_PATH", ".roby/runtime.lease"),
            heartbeat_path=os.getenv(
                "ROBY_RUNTIME_HEARTBEAT_PATH",
                ".roby/runtime_heartbeat.json",
            ),
            heartbeat_interval=timedelta(seconds=interval),
            stale_after=timedelta(seconds=stale),
        ),
    )
