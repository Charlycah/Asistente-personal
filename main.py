from __future__ import annotations

import argparse
from pathlib import Path

from app.credentials import activate_credentials
from app.development_console import (
    onboarding_message,
    render_doctor,
    run_doctor,
)
from app.roby_config import (
    activate_roby_config,
    load_roby_config,
    resolve_roby_config_path,
    save_roby_config,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ROBY",
        description="ROBY XI.2 personal desktop assistant",
    )
    parser.add_argument(
        "--doctor",
        action="store_true",
        help="validate configuration",
    )
    parser.add_argument(
        "--desktop",
        action="store_true",
        help="start the desktop interface (default)",
    )
    parser.add_argument(
        "--setup",
        action="store_true",
        help="create or validate .roby/config.json",
    )
    parser.add_argument(
        "--model",
        default="",
        help="set the local provider model during setup",
    )
    parser.add_argument(
        "--config",
        default=".roby/config.json",
        help="ROBY configuration file path",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    config_path = Path(args.config)

    if args.setup:
        try:
            result = load_roby_config(config_path)
            if args.model.strip():
                result.data["providers"]["local"]["model"] = args.model.strip()
                save_roby_config(result.data, config_path)
            print(f"Configuración lista: {config_path}")
            return 0
        except (OSError, ValueError) as exc:
            for line in onboarding_message(exc):
                print(line)
            return 2

    try:
        runtime_config_path = resolve_roby_config_path(config_path)
        activate_roby_config(runtime_config_path)
        activate_credentials()
    except (OSError, ValueError) as exc:
        for line in onboarding_message(exc):
            print(line)
        return 2

    if args.doctor:
        checks = run_doctor()
        for line in render_doctor(checks):
            print(line)
        return 0 if all(item.passed for item in checks if item.required) else 2

    try:
        from app.desktop_bootstrap import build_unified_desktop_app

        build_unified_desktop_app().run()
    except (RuntimeError, ValueError) as exc:
        for line in onboarding_message(exc):
            print(line)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
