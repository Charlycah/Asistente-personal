from __future__ import annotations

import json
from html import escape

from application.governed_web_panel import (
    GovernedWebPanelSnapshot,
    WebPanelSection,
)

_SECTION_TITLES = {
    "system": "System",
    "residence": "Residence",
    "synchronization": "Synchronization",
    "resources": "Resources",
}


def render_governed_web_panel(snapshot: GovernedWebPanelSnapshot) -> str:
    """Render the admitted M406.1 snapshot without adding domain information."""

    sections = (
        _render_section(snapshot.system),
        _render_section(snapshot.residence),
        _render_section(snapshot.synchronization),
        _render_section(snapshot.resources),
    )
    generated_at = escape(snapshot.generated_at.isoformat())
    return """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>ROBY XI.2 — Local Governed Status</title>
<style>
:root { color-scheme: light dark; font-family: system-ui, sans-serif; }
body { margin: 0; padding: 2rem; max-width: 72rem; margin-inline: auto; }
header { margin-bottom: 1.5rem; }
h1 { margin-bottom: .25rem; }
.meta { opacity: .75; }
.grid { display: grid; gap: 1rem; }
.grid { grid-template-columns: repeat(auto-fit,minmax(18rem,1fr)); }
section { border: 1px solid currentColor; border-radius: .6rem; padding: 1rem; }
section h2 { margin-top: 0; }
.badge { display: inline-block; border: 1px solid currentColor; }
.badge { border-radius: 999px; padding: .1rem .45rem; }
.badge { margin-right: .4rem; font-size: .8rem; }
pre { white-space: pre-wrap; overflow-wrap: anywhere; }
a { color: inherit; }
</style>
</head>
<body>
<header>
<h1>ROBY XI.2</h1>
<p>Local Governed Status</p>
<p class="meta">Generated: """ + generated_at + """</p>
<p><a href="/">Refresh</a></p>
</header>
<main class="grid">
""" + "\n".join(sections) + """
</main>
</body>
</html>
"""


def _render_section(section: WebPanelSection) -> str:
    title = escape(_SECTION_TITLES[section.section_id])
    status = escape(section.status.value)
    classification = escape(section.classification.value)
    payload = json.dumps(
        section.to_dict()["payload"],
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    )
    return (
        "<section>"
        f"<h2>{title}</h2>"
        f'<span class="badge">{status}</span>'
        f'<span class="badge">{classification}</span>'
        f"<pre>{escape(payload)}</pre>"
        "</section>"
    )
