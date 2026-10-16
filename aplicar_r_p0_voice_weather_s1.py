"""Aplicador quirurgico R-P0-VOICE-WEATHER-S1; no requiere Git."""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

ROOT = Path.cwd()
CHANGES = (
    (
        Path("app/voice_output.py"),
        "    return EdgeTTSVoiceOutput(\n        EdgeTTSVoiceConfig(",
        "    output = EdgeTTSVoiceOutput(\n        EdgeTTSVoiceConfig(",
        (
            '            timeout_seconds=float(os.getenv("ROBY_EDGE_TTS_TIMEO'
            'UT_SECONDS", "90")),\n        )\n    )\n\n\nclass VoiceResponseReader'
            ':'
        ),
        (
            '            timeout_seconds=float(os.getenv("ROBY_EDGE_TTS_TIMEO'
            'UT_SECONDS", "90")),\n        )\n    )\n    return SafeVoiceOutput('
            'output)\n\n\nclass VoiceResponseReader:'
        ),
    ),
    (
        Path("app/weather_conversation_runtime.py"),
        r'            r"\b(?:decime|dime|contame|dame|mostrame)\b.*"',
        r'            r"\b(?:decime|dec[ií]s|dime|contame|dame|mostrame)\b.*"',
        None,
        None,
    ),
)


def fail(message: str) -> None:
    raise RuntimeError(message)


def main() -> None:
    if not (ROOT / "main.py").is_file():
        fail("Ejecutar desde la raiz de HAL, junto a main.py.")
    prepared = []
    for rel, old1, new1, old2, new2 in CHANGES:
        path = ROOT / rel
        raw = path.read_bytes()
        if b"\r\n" in raw:
            newline = "\r\n"
        else:
            newline = "\n"
        text = raw.decode("utf-8")
        canonical = text.replace("\r\n", "\n")
        pairs = [(old1, new1)] + ([(old2, new2)] if old2 is not None else [])
        updated = canonical
        for old, new in pairs:
            if updated.count(old) != 1:
                fail(
                    f"{rel}: fragmento esperado ausente o repetido. "
                    "No se modifica nada."
                )
            updated = updated.replace(old, new, 1)
        if rel.name == "voice_output.py" and "class SafeVoiceOutput:" not in canonical:
            fail("SafeVoiceOutput no existe: no se modifica nada.")
        prepared.append((path, raw, updated.replace("\n", newline).encode("utf-8")))
    print("Verificacion de los dos archivos: OK")
    for path, raw, _ in prepared:
        backup = path.with_name(path.name + ".pre-r-p0-vw-s1.bak")
        if backup.exists():
            if backup.read_bytes() != raw:
                fail(f"Backup previo diferente: {backup}. No se modifica nada.")
        else:
            with backup.open("xb") as f:
                f.write(raw)
        print(f"Backup: {backup.relative_to(ROOT)}")
    written = []
    try:
        for path, _, new_raw in prepared:
            fd, tmp_name = tempfile.mkstemp(
                prefix=".r-p0-", suffix=".tmp", dir=path.parent
            )
            try:
                with os.fdopen(fd, "wb") as f:
                    f.write(new_raw)
                os.replace(tmp_name, path)
            finally:
                if os.path.exists(tmp_name):
                    os.unlink(tmp_name)
            written.append(path)
            print(f"Aplicado: {path.relative_to(ROOT)}")
    except Exception:
        for path in reversed(written):
            backup = path.with_name(path.name + ".pre-r-p0-vw-s1.bak")
            path.write_bytes(backup.read_bytes())
        raise
    print("GREEN aplicado. Falta certificacion con Ruff y Pytest.")


if __name__ == "__main__":
    try:
        main()
    except (OSError, UnicodeError, RuntimeError) as exc:
        print(f"ABORTADO: {exc}", file=sys.stderr)
        sys.exit(1)
