"""Read-only differential inspection of CONV-REAL-01A-S1 against a baseline ZIP.

Usage: python ROBY_CONV_REAL_01A_S1_COMPARE_READONLY.py "path-to-baseline.zip"
Run from HAL root. Writes only a report to the current directory.
"""
from __future__ import annotations

import difflib
import hashlib
import sys
from pathlib import Path
from zipfile import ZipFile

TARGETS = (
    'app/conversation_reliability_observability.py',
    'core/governed_operational_conversation_pipeline/pipeline.py',
)
REPORT = 'CONV_REAL_01A_S1_DIFFERENTIAL_REPORT.txt'


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    if len(sys.argv) != 2:
        print('Usage: python ROBY_CONV_REAL_01A_S1_COMPARE_READONLY.py "baseline.zip"')
        return 2
    root = Path.cwd()
    archive = Path(sys.argv[1]).expanduser().resolve()
    if not archive.is_file():
        print(f'ZIP not found: {archive}')
        return 2
    output = []
    with ZipFile(archive) as z:
        names = z.namelist()
        for target in TARGETS:
            matches = [name for name in names if name.endswith('/' + target) or name == target]
            if len(matches) != 1:
                print(f'Expected exactly one ZIP entry for {target}; found {len(matches)}')
                return 2
            local = root / target
            if not local.is_file():
                print(f'Local file missing: {local}')
                return 2
            old = z.read(matches[0])
            new = local.read_bytes()
            output.extend([
                f'=== {target} ===',
                f'ZIP entry: {matches[0]}',
                f'ZIP SHA256: {digest(old)}',
                f'HAL SHA256: {digest(new)}',
                f'Identical: {old == new}',
                '',
            ])
            old_lines = old.decode('utf-8-sig').splitlines(keepends=True)
            new_lines = new.decode('utf-8-sig').splitlines(keepends=True)
            diff = difflib.unified_diff(
                old_lines, new_lines, fromfile='ZIP/' + target,
                tofile='HAL/' + target, n=5,
            )
            output.extend(line.rstrip('\n') for line in diff)
            output.append('')
    report_path = root / REPORT
    report_path.write_text('\n'.join(output) + '\n', encoding='utf-8')
    print(f'Comparison completed (source files unchanged): {report_path}')
    print('Review the report for unrelated edits before certifying scope.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
