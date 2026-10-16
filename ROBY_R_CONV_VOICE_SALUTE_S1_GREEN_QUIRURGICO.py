"""ROBY XI.2 — S1 surgical GREEN for visible and spoken desktop greeting.

Run from HAL root. Defaults to inspection; --apply performs guarded edits.
"""
from __future__ import annotations

import argparse
from pathlib import Path

OLD_GREETING = '    greeting: str = "¿Con quien estoy conversando?"'
NEW_GREETING = '    greeting: str = "¿Qué tal, cómo estás?"'
OLD_BLOCK = '''        if self.config.greeting.strip():
            append(
                self.controller.presenter.roby_message(
                    self.config.greeting.strip()
                ).render()
            )
        if self.recovery_message:
'''
NEW_BLOCK = '''        if self.config.greeting.strip():
            greeting = self.config.greeting.strip()
            append(self.controller.presenter.roby_message(greeting).render())
            spoken = self.controller.voice_reader.prosody_formatter.format(greeting)
            if spoken:
                try:
                    self.controller.voice_reader.voice_output.speak(spoken)
                except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                    # A TTS failure must not suppress the visible greeting.
                    pass
        if self.recovery_message:
'''
OLD_TEST = '    assert config.greeting == "¿Con quien estoy conversando?"'
NEW_TEST = '    assert config.greeting == "¿Qué tal, cómo estás?"'


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true', help='Apply guarded edits')
    args = parser.parse_args()
    root = Path.cwd()
    edits = {
        root / 'app' / 'desktop_ui.py': [
            (OLD_GREETING, NEW_GREETING),
            (OLD_BLOCK, NEW_BLOCK),
        ],
        root / 'tests' / 'test_m24_desktop_ui.py': [(OLD_TEST, NEW_TEST)],
    }
    staged = {}
    for path, replacements in edits.items():
        if not path.is_file():
            raise SystemExit(f'STOP: required file missing: {path}')
        original = path.read_bytes()
        # Preserve original newline convention and avoid changing unrelated lines.
        newline = b'\r\n' if b'\r\n' in original else b'\n'
        revised = original
        for before, after in replacements:
            old = before.encode('utf-8').replace(b'\n', newline)
            new = after.encode('utf-8').replace(b'\n', newline)
            if revised.count(old) != 1:
                raise SystemExit(
                    f'STOP: expected exactly one original block in {path.name}, '
                    f'found {revised.count(old)}. No files modified.'
                )
            revised = revised.replace(old, new, 1)
        staged[path] = revised
    for path in staged:
        print(f'{"APPLY" if args.apply else "DRY-RUN"}: {path.relative_to(root)}')
    if not args.apply:
        print('PRECHECK OK — no files modified. Use --apply to perform GREEN.')
        return
    for path, revised in staged.items():
        path.write_bytes(revised)
    print('GREEN APPLIED — run directed tests and Ruff; not Owner-certified.')


if __name__ == '__main__':
    main()
