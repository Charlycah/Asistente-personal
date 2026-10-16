from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.memory_consolidation import OfficialMemoryGateway  # noqa: E402
from application.brain import (  # noqa: E402
    BrainDiagnostic,
    BrainQuery,
    build_official_memory_brain_composition,
)
from core.memory_runtime_integration import (  # noqa: E402
    MemoryRuntimeConfig,
    MemoryRuntimeIntegration,
)
from infrastructure.brain import AtomicJsonBrainRepository  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Inspección de solo lectura del BRAIN de ROBY.",
    )
    parser.add_argument("--owner", required=True, help="Propietario de la memoria")
    parser.add_argument("--query", default="", help="Texto a buscar")
    parser.add_argument("--limit", type=int, default=20, help="Máximo de resultados")
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path.cwd(),
        help="Raíz del proyecto ROBY",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    project_root = args.project_root.resolve()
    runtime = MemoryRuntimeIntegration(
        MemoryRuntimeConfig(
            root_path=project_root / ".roby" / "memory",
            enable_learning=False,
        )
    )
    composition = build_official_memory_brain_composition(
        brain_repository=AtomicJsonBrainRepository(
            project_root / ".roby" / "brain"
        ),
        memory_gateway=OfficialMemoryGateway(runtime, owner=args.owner),
        owner=args.owner,
    )
    report = BrainDiagnostic(composition.service).inspect(
        BrainQuery(text=args.query, limit=args.limit)
    )
    print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
