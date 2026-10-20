"""S4-D7-C.5: guarded, test-only reconciliation of historical CAP-17 contracts.

Run from HAL root. All three test files are validated before any write.
No production code, docs, or other test files are modified.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

SAFE = Path(
    "tests/architecture/test_cap17_safe_document_source_presentation_contract_red.py"
)
S2 = Path("tests/architecture/test_r_cap17_conv_access_s2_contract_red.py")
S5 = Path("tests/architecture/test_r_cap17_conv_access_s5_contract_red.py")
files = {path: path.read_text(encoding="utf-8-sig") for path in (SAFE, S2, S5)}


def replace_once(source: str, old: str, new: str, label: str) -> str:
    count = source.count(old)
    if count != 1:
        raise SystemExit(f"STOP: {label}: expected one anchor, found {count}")
    return source.replace(old, new, 1)


# Keep the original presentation/security assertions intact. Only the default
# request operation changes from locating to explicitly reading content.
safe = files[SAFE]
safe, count = re.subn(
    r'(def _request\(text=)["\'].*?["\'](\):)',
    r'\1"Leé el libro atlas de mi biblioteca"\2',
    safe,
    count=1,
)
if count != 1:
    raise SystemExit("STOP: safe presentation request default not found")
safe, count = re.subn(
    r'(def _intercept\(result, text=)["\'].*?["\'](\):)',
    r'\1"Leé el libro atlas de mi biblioteca"\2',
    safe,
    count=1,
)
if count != 1:
    raise SystemExit("STOP: safe presentation interceptor default not found")
files[SAFE] = safe

# S2 and S5: retain historical retrieval stubs, add the new public location
# operation to the doubles, and assert that only this operation is invoked.
for path, test_name, search_text in (
    (S2, "test_explicit_search_still_enters_existing_governed_path", "Fundación"),
    (
        S5,
        "test_explicit_book_search_preserves_governed_search_path",
        "robots e imperio",
    ),
):
    source = files[path]
    anchor = "    def handle_admitted_request(self, **kwargs):"
    addition = (
        "    def locate_admitted_request(self, **kwargs):\n"
        '        self.calls.append(("locate", kwargs))\n'
        "        return SimpleNamespace(\n"
        '            status=SimpleNamespace(value="no_match"),\n'
        "            bounded=True,\n"
        '            query=kwargs["search_query"],\n'
        "        )\n\n"
    )
    source = replace_once(source, anchor, addition + anchor, f"{path} double")
    tree = ast.parse(source)
    node = next(
        (
            n
            for n in tree.body
            if isinstance(n, ast.FunctionDef) and n.name == test_name
        ),
        None,
    )
    if node is None or node.end_lineno is None:
        raise SystemExit(f"STOP: {path}: test function not found")
    lines = source.splitlines(keepends=True)
    segment = "".join(lines[node.lineno - 1 : node.end_lineno])
    if path == S2:
        old = (
            "    assert len(conversation.calls) == 1\n"
            '    assert conversation.calls[0]["search_query"] == "Fundación"'
        )
        new = (
            "    assert len(conversation.calls) == 1\n"
            "    operation, kwargs = conversation.calls[0]\n"
            '    assert operation == "locate"\n'
            '    assert kwargs["search_query"] == "Fundación"'
        )
    else:
        old = (
            "    assert len(conversation.calls) == 1\n"
            '    assert "robots e imperio" in '
            'conversation.calls[0]["search_query"].casefold()'
        )
        new = (
            "    assert len(conversation.calls) == 1\n"
            "    operation, kwargs = conversation.calls[0]\n"
            '    assert operation == "locate"\n'
            '    assert "robots e imperio" in kwargs["search_query"].casefold()'
        )
    segment = replace_once(segment, old, new, f"{path} expectations")
    lines[node.lineno - 1 : node.end_lineno] = [segment]
    files[path] = "".join(lines)

for path, source in files.items():
    ast.parse(source, filename=str(path))

# Validate all edits before writing; keep the pre-existing files recoverable
# via git diff, without touching unrelated local modifications.
for path, source in files.items():
    path.write_text(source, encoding="utf-8")
    print("S4_D7_C5_TEST_CONTRACT_UPDATED:", path)
