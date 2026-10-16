"""Apply the reconciled M25/R-P0 voice GREEN without Git.

Run from the HAL project root. Fails closed on unexpected source changes.
"""

import sys
from pathlib import Path

ROOT = Path.cwd()
VOICE = ROOT / "app" / "voice_output.py"
BOOT = ROOT / "app" / "desktop_bootstrap.py"


def replace_once(source: str, old: str, new: str, label: str) -> str:
    count = source.count(old)
    if count != 1:
        raise ValueError(f"{label}: se esperaban 1 coincidencia; hay {count}")
    return source.replace(old, new, 1)


def main() -> int:
    paths = (VOICE, BOOT)
    for path in paths:
        if not path.is_file():
            raise ValueError(f"Archivo inexistente: {path}")

    originals = {path: path.read_bytes() for path in paths}
    sources = {path: originals[path].decode("utf-8") for path in paths}

    # Exact changes only; preserve newline conventions and all other source.
    voice = sources[VOICE]
    voice = replace_once(
        voice,
        "    return SafeVoiceOutput(output)",
        "    return output",
        "Retorno de fabrica M25",
    )
    boot = sources[BOOT]
    boot = replace_once(
        boot,
        "from app.voice_output import build_voice_output_from_environment",
        (
            'from app.voice_output import SafeVoiceOutput, build_voice_output'
            '_from_environment'
        ),
        "Import de proteccion en bootstrap",
    )
    boot = replace_once(
        boot,
        "        voice_output=build_voice_output_from_environment(),",
        "        voice_output=SafeVoiceOutput(build_voice_output_from_environment()),",
        "Inyeccion protegida en escritorio",
    )
    changes = {VOICE: voice.encode("utf-8"), BOOT: boot.encode("utf-8")}
    backups = {path: path.with_name(path.name + ".pre-m25-green.bak") for path in paths}
    for backup in backups.values():
        if backup.exists():
            raise ValueError(f"Backup ya existente, sin cambios: {backup}")

    # Verify first, then back up, then write. Restore originals on write error.
    for path, backup in backups.items():
        backup.write_bytes(originals[path])
        print(f"Backup: {backup.relative_to(ROOT)}")
    written = []
    try:
        for path in paths:
            path.write_bytes(changes[path])
            written.append(path)
            print(f"Aplicado: {path.relative_to(ROOT)}")
    except Exception:
        for path in written:
            path.write_bytes(originals[path])
        raise
    print("GREEN reconciliado aplicado. Pendiente de Ruff y Pytest.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"ABORTADO: {exc}", file=sys.stderr)
        sys.exit(1)
