"""Guarded S4-D7-B fix for direct 'Leé el libro ... de mi biblioteca' requests."""

from __future__ import annotations

import ast
from pathlib import Path

TARGET = Path("app/governed_local_library_runtime_wiring.py")
source = TARGET.read_text(encoding="utf-8-sig")
anchor = """    def _search_query(cls, text: str) -> str:
        query = text.strip()
        normalized = query.casefold()
"""
if source.count(anchor) != 1:
    raise SystemExit("STOP: search query structure differs; no file written")
replacement = (
    anchor
    + """        # A direct reading command can contain a trailing library locator.
        # Extract the named book before scanning generic library prefixes.
        direct_read = re.fullmatch(
            r"(?:le[eé]|lee)\\s+(?:el\\s+)?libro\\s+(.+?)"
            r"\\s+de\\s+mi\\s+biblioteca\\s*[.?!]*",
            query,
            flags=re.IGNORECASE,
        )
        if direct_read is not None:
            return direct_read.group(1).strip()
"""
)
updated = source.replace(anchor, replacement, 1)
ast.parse(updated, filename=str(TARGET))
TARGET.write_text(updated, encoding="utf-8")
print("S4_D7_B_DIRECT_READ_FIX_APPLIED:", TARGET)
