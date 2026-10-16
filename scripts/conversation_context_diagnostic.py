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
    ActiveIdentityRequest,
    BrainQuery,
    build_identity_memory_brain_composition,
)
from core.memory_runtime_integration import (  # noqa: E402
    MemoryRuntimeConfig,
    MemoryRuntimeIntegration,
)
from core.relationship_memory import RelationshipMemoryManager  # noqa: E402
from infrastructure.brain import AtomicJsonBrainRepository  # noqa: E402
from infrastructure.repositories.sqlite_household_goal_repository import (  # noqa: E402
    SQLiteHouseholdGoalRepository,
)
from infrastructure.repositories.sqlite_household_project_repository import (  # noqa: E402
    SQLiteHouseholdProjectRepository,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Diagnóstico del paquete de contexto conversacional de ROBY.",
    )
    parser.add_argument("--owner", required=True, help="Propietario base")
    parser.add_argument("--name", help="Nombre declarado: Carlos o Cristina")
    parser.add_argument("--profile-id", help="Identificador explícito de perfil")
    parser.add_argument(
        "--session-profile-id",
        help="Identificador de perfil asociado a la sesión",
    )
    parser.add_argument("--query", default="", help="Texto a buscar")
    parser.add_argument("--limit", type=int, default=20, help="Máximo de resultados")
    parser.add_argument("--max-items", type=int, default=8)
    parser.add_argument("--max-characters", type=int, default=1600)
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
    storage_root = project_root / ".roby"
    runtime = MemoryRuntimeIntegration(
        MemoryRuntimeConfig(
            root_path=storage_root / "memory",
            enable_learning=False,
        )
    )
    composition = build_identity_memory_brain_composition(
        brain_repository=AtomicJsonBrainRepository(storage_root / "brain"),
        memory_gateway=OfficialMemoryGateway(runtime, owner=args.owner),
        goal_repository=SQLiteHouseholdGoalRepository(
            storage_root / "household_goals.db"
        ),
        project_repository=SQLiteHouseholdProjectRepository(
            storage_root / "household_projects.db"
        ),
        storage_root=storage_root,
        relationship_memory=RelationshipMemoryManager(),
        owner=args.owner,
    )
    report = composition.conversation_context_diagnostic.inspect(
        identity_request=ActiveIdentityRequest(
            declared_name=args.name,
            profile_id=args.profile_id,
            session_profile_id=args.session_profile_id,
        ),
        query=BrainQuery(text=args.query, limit=args.limit),
        max_items=args.max_items,
        max_characters=args.max_characters,
    )
    print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
    return 0 if report.is_healthy else 1


if __name__ == "__main__":
    raise SystemExit(main())
