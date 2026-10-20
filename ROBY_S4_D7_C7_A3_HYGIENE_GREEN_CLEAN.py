"""S4-D7-C.7-A2: guarded hygiene of six historical patch scripts only.

Run from HAL root. Does NOT execute any historical patch script.
Four multiline template scripts get a file-scoped E501 exemption, because
reflowing the embedded generated source would change its contractual bytes.
Four ordinary one-line string literals are split without changing their values.
"""

from __future__ import annotations

import ast
import hashlib
from pathlib import Path

# Hashes are computed from the six exact files supplied for this operation.
EXPECTED = {
    "ROBY_CONV_REAL_01A_S1_GREEN_QUIRURGICO.py": (
        "533bbd97ca2832a00cdbfc783475c831791fe09c3b47300dbf19f6d774e5c781"
    ),
    "ROBY_CONV_REAL_01C_S2_GREEN_QUIRURGICO.py": (
        "daced029f2d83b986ed5f48eaee969a23538864800fda1bced4ec1c236fc0f7e"
    ),
    "ROBY_S4_D7_B_GREEN_QUIRURGICO.py": (
        "c2664e717ff14c491fe18b2a241aa8599bdda095e1884363aadcc3ba0b2029f5"
    ),
    "ROBY_S4_D7_C3_GREEN_QUIRURGICO.py": (
        "436f33dd1ed68f4c733655f1ea0da8a77f7b5b355e67311ae406de55918a280d"
    ),
    "ROBY_S4_D7_C5_CONTRACT_RECONCILIATION.py": (
        "15c4d8d456f602044d3e835d286b275b1850825cee10a9f3b8fdf3605bfb4978"
    ),
    "R_CAP17_CONV_ACCESS_S3_GREEN.py": (
        "d7ccd4089b2ff56e4146c3cc8730cef274cca940ce422d6725df61d0a9021b50"
    ),
}

MULTILINE = {
    "ROBY_CONV_REAL_01A_S1_GREEN_QUIRURGICO.py",
    "ROBY_S4_D7_B_GREEN_QUIRURGICO.py",
    "ROBY_S4_D7_C3_GREEN_QUIRURGICO.py",
    "R_CAP17_CONV_ACCESS_S3_GREEN.py",
}

# Exact literal content, including its original escape sequences.
SPLITS = {
    "ROBY_CONV_REAL_01C_S2_GREEN_QUIRURGICO.py": [
        (
            (
                "        '        messages.append"
                '(ConversationMessage("system", i'
                "nference_request.system_prompt))"
                "\\n'\n"
            ),
            "        '        messages.append(ConversationMessage(\"system\", '\n"
            "        'inference_request.system_prompt))\\n'\n",
            2,
        ),
    ],
    "ROBY_S4_D7_C3_GREEN_QUIRURGICO.py": [
        (
            (
                'end = """        if admitted:\\n '
                "           result = self.convers"
                'ation.handle_user_request(\\n"""\n'
            ),
            "end = (\n"
            '    "        if admitted:\\n"\n'
            '    "            result = self.conversation.handle_user_request(\\n"\n'
            ")\n",
            1,
        ),
    ],
    "ROBY_S4_D7_C5_CONTRACT_RECONCILIATION.py": [
        (
            (
                "            '    assert \"robots "
                'e imperio" in conversation.calls'
                '[0]["search_query"].casefold()\'\n'
            ),
            "            '    assert \"robots e imperio\" in '\n"
            "            'conversation.calls[0][\"search_query\"].casefold()'\n",
            1,
        ),
    ],
}


def literal_assignments(source: str) -> dict[str, object]:
    values = {}
    for node in ast.walk(ast.parse(source)):
        if not isinstance(node, (ast.Assign, ast.AnnAssign)):
            continue
        try:
            value = ast.literal_eval(node.value)
        except (ValueError, TypeError, SyntaxError, RecursionError):
            continue
        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
        for target in targets:
            if isinstance(target, ast.Name):
                values[target.id] = value
    return values


def main() -> None:
    pending = {}
    for name, expected_hash in EXPECTED.items():
        path = Path(name)
        if not path.is_file():
            raise SystemExit(f"STOP: missing {name}")
        raw = path.read_bytes()
        normalized = raw.replace(b"\r\n", b"\n")
        if hashlib.sha256(normalized).hexdigest() != expected_hash:
            raise SystemExit(f"STOP: baseline differs: {name}")
        if raw.startswith(b"\xef\xbb\xbf"):
            raise SystemExit(f"STOP: unexpected BOM: {name}")
        newline = "\r\n" if b"\r\n" in raw else "\n"
        source = raw.decode("utf-8").replace("\r\n", "\n")
        changed = source
        if name in MULTILINE:
            changed = "# ruff: noqa: E501\n" + changed
        for old, new, count in SPLITS.get(name, []):
            if changed.count(old) != count:
                raise SystemExit(f"STOP: changed string anchor: {name}")
            changed = changed.replace(old, new)
        ast.parse(changed, filename=name)
        if literal_assignments(source) != literal_assignments(changed):
            raise SystemExit(f"STOP: literal assignment changed: {name}")
        if changed == source:
            raise SystemExit(f"STOP: no change produced: {name}")
        pending[path] = changed.replace("\n", newline).encode("utf-8")
    for path, data in pending.items():
        path.write_bytes(data)
        print(f"HYGIENE_APPLIED: {path}")
    print("S4_D7_C7_A2_HYGIENE_APPLIED: 6 files")
    print("NEXT: ruff check .; ruff format --check; git diff --check")


if __name__ == "__main__":
    main()
