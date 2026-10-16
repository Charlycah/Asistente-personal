from __future__ import annotations

import os

_LIVE_GMAIL_ENABLED = os.getenv("ROBY_GMAIL_ACCEPTANCE_ENABLED", "").lower() in {
    "1",
    "true",
    "yes",
    "on",
}

collect_ignore = (
    [] if _LIVE_GMAIL_ENABLED else ["acceptance/test_m227_5_live_gmail_account.py"]
)
