from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@dataclass(frozen=True)
class DiagnosticCase:
    case_id: str
    title: str
    prompts: tuple[str, ...]


CASES = (
    DiagnosticCase(
        "D",
        "CORRECTION / UPDATE",
        (
            "La caja está en el garaje.",
            "Corrección: la caja está en el dormitorio.",
            "¿Dónde está la caja?",
        ),
    ),
    DiagnosticCase(
        "E",
        "TEMPORAL DISTINCTION",
        (
            "Ayer Juan estaba en Córdoba.",
            "Hoy Juan está en Rosario.",
            "¿Dónde estaba Juan ayer?",
        ),
    ),
    DiagnosticCase(
        "F",
        "REFERENTIAL CONTINUITY",
        (
            "Marta compró un libro y Elena una lámpara.",
            "¿Qué compró Elena?",
        ),
    ),
    DiagnosticCase(
        "G",
        "EXPLICIT UNCERTAINTY",
        (
            "No sabemos si Pedro tomó el tren o el autobús.",
            "¿Podemos afirmar que tomó el tren?",
        ),
    ),
    DiagnosticCase(
        "H",
        "EVIDENCE REVISION",
        (
            "Pensamos que la ventana se rompió por el viento.",
            "La cámara muestra a una persona golpeándola.",
            "¿Qué explicación tiene ahora más apoyo?",
        ),
    ),
    DiagnosticCase(
        "I",
        "NEGATION PRESERVATION",
        (
            "Pedro no fue a Córdoba.",
            "¿Pedro fue a Córdoba?",
        ),
    ),
    DiagnosticCase(
        "J",
        "ATTRIBUTION / SOURCE DISTINCTION",
        (
            "Ana dice que Luis rompió el vaso.",
            "¿Sabemos que Luis rompió el vaso?",
        ),
    ),
    DiagnosticCase(
        "K",
        "CONDITIONAL PRESERVATION",
        (
            "Si mañana llueve, Marta irá en taxi.",
            "¿Marta fue en taxi?",
        ),
    ),
    DiagnosticCase(
        "L",
        "MULTI-ENTITY STATE UPDATE",
        (
            "La caja roja está en la cocina y la azul en el dormitorio.",
            "Corrección: la caja roja está en el garaje.",
            "¿Dónde está la caja roja?",
            "¿Dónde está la caja azul?",
        ),
    ),
)


def _find_local_adapter(adapter: object) -> object:
    from app.runtime_ui_adapter import LocalConversationUIAdapter

    current = adapter
    visited: set[int] = set()
    while current is not None and id(current) not in visited:
        visited.add(id(current))
        if isinstance(current, LocalConversationUIAdapter):
            return current
        current = getattr(current, "adapter", None)
    raise RuntimeError(
        "LocalConversationUIAdapter not found in desktop adapter chain"
    )


def _runtime_turn_count(runtime: object) -> int:
    history = getattr(runtime, "history", ())
    return len(history)


def _render_messages(messages: Iterable[object]) -> tuple[str, ...]:
    rendered = []
    for message in messages:
        render = getattr(message, "render", None)
        rendered.append(render() if callable(render) else str(message))
    return tuple(rendered)


def _diagnostic_session_id(run_id: str, case_id: str) -> str:
    normalized_run = "-".join(run_id.strip().casefold().split())
    normalized_case = case_id.strip().casefold()
    if not normalized_run or not normalized_case:
        raise ValueError("diagnostic run and case identifiers must not be blank")
    return f"diagnostic-guide-v2-{normalized_run}-{normalized_case}"


def _diagnostic_state_path(session_id: str) -> Path:
    return Path(".roby/diagnostics/runtime_state") / f"{session_id}.json"


def _build_isolated_local_conversation(session_id: str):
    from app.local_conversation_factory import build_local_conversation_from_environment
    from app.local_runtime_entrypoint import build_local_runtime_from_environment
    from core.local_runtime_bootstrap import (
        LocalRuntimeBootstrap,
        LocalRuntimeBootstrapConfig,
    )

    source_bootstrap = build_local_runtime_from_environment()
    isolated_bootstrap = LocalRuntimeBootstrap(
        root=source_bootstrap.root,
        config=LocalRuntimeBootstrapConfig(
            owner=source_bootstrap.config.owner,
            session_id=session_id,
            state_path=_diagnostic_state_path(session_id),
        ),
    )
    return build_local_conversation_from_environment(bootstrap=isolated_bootstrap)


def _default_run_id() -> str:
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S-%f")


def _activate_runtime_environment() -> None:
    from app.credentials import activate_credentials
    from app.roby_config import activate_roby_config, resolve_roby_config_path

    config_path = resolve_roby_config_path()
    activate_roby_config(config_path, override_existing=True)
    activate_credentials()


def run_diagnostics(
    *,
    output_path: Path,
    reveal_prompt: bool = True,
    run_id: str | None = None,
) -> Path:
    from app.desktop_bootstrap import build_unified_desktop_app
    from core.development_console_observability import (
        DevelopmentConsoleObserver,
        DevelopmentConsoleRenderer,
    )

    effective_run_id = run_id or _default_run_id()
    _activate_runtime_environment()
    lines = [
        "ROBY XI.2 — Conversational Reality Evaluation Guide v2",
        "Read-Only Isolated Desktop Diagnostic Harness",
        f"diagnostic_run={effective_run_id}",
        "",
        (
            "NOTE: observer is read-only; prompts still traverse the normal "
            "desktop conversation path."
        ),
        (
            "NOTE: each case uses a pre-composition diagnostic session; "
            "coowners-main is not modified."
        ),
        "NOTE: prompt/message contents are written only to this local diagnostic file.",
        "",
    ]

    for case in CASES:
        session_id = _diagnostic_session_id(effective_run_id, case.case_id)
        local_conversation = _build_isolated_local_conversation(session_id)
        app = build_unified_desktop_app(local_conversation=local_conversation)
        local_adapter = _find_local_adapter(app.adapter)
        runtime = local_adapter.runtime
        observer = DevelopmentConsoleObserver(runtime)
        renderer = DevelopmentConsoleRenderer()
        started = False
        try:
            if app.on_start is not None:
                app.on_start()
                started = True
            lines.extend(
                (
                    f"=== TEST {case.case_id} — {case.title} ===",
                    f"diagnostic_session={session_id}",
                )
            )
            lines.extend(renderer.render_runtime(observer.runtime_observation()))
            lines.append("")

            for index, prompt in enumerate(case.prompts, start=1):
                before = _runtime_turn_count(runtime)
                messages = app.controller.submit(prompt)
                after = _runtime_turn_count(runtime)
                lines.append(f"STEP {index}")
                lines.append(f"INPUT: {prompt}")
                lines.extend(_render_messages(messages))
                lines.append(f"runtime_turn_delta={after - before}")

                if after == before:
                    lines.append(
                        "INTERCEPTION: desktop pre-runtime handler consumed the input; "
                        "no OfficialConversationGateway turn was created."
                    )
                else:
                    observed = observer.last_turn()
                    if observed is None:
                        lines.append(
                            "TRACE: runtime turn created but observer returned none"
                        )
                    else:
                        lines.extend(
                            renderer.render_turn(observed, reveal_prompt=reveal_prompt)
                        )
                lines.append("")
            lines.append("")
        finally:
            if started and app.on_stop is not None:
                app.on_stop()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return output_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run controlled ROBY conversational Guide v2 diagnostics."
    )
    parser.add_argument(
        "--output",
        default="roby_conversational_guide_v2_trace.txt",
        help="local diagnostic TXT destination",
    )
    parser.add_argument(
        "--run-id",
        default=None,
        help="stable run label; defaults to a UTC timestamp",
    )
    parser.add_argument(
        "--metadata-only",
        action="store_true",
        help="omit prompt and structured-message contents from the output",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    path = run_diagnostics(
        output_path=Path(args.output),
        reveal_prompt=not args.metadata_only,
        run_id=args.run_id,
    )
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
