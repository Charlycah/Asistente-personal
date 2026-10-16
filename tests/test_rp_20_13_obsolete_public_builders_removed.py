from __future__ import annotations

import ast
from pathlib import Path

OBSOLETE_BUILDERS = {
    "build_official_conversation_gateway": Path("app/official_conversation_gateway.py"),
    "build_runtime_health_readiness": Path("app/runtime_health_readiness.py"),
    "build_runtime_operational_snapshot": Path("app/runtime_operational_snapshot.py"),
    "build_runtime_recovery_plan": Path("app/runtime_recovery_planner.py"),
    "build_unified_runtime_observability_snapshot": Path(
        "app/unified_runtime_observability.py"
    ),
}


def test_obsolete_public_builders_are_no_longer_declared() -> None:
    for name, path in OBSOLETE_BUILDERS.items():
        tree = ast.parse(path.read_text(encoding="utf-8"))
        declarations = {
            node.name
            for node in tree.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        }
        assert name not in declarations


def test_runtime_collaborators_remain_available_as_canonical_api() -> None:
    from app.official_conversation_gateway import OfficialConversationGateway
    from app.runtime_health_readiness import RuntimeHealthReadinessService
    from app.runtime_operational_snapshot import RuntimeOperationalSnapshotBuilder
    from app.runtime_recovery_planner import RuntimeRecoveryPlanner
    from app.unified_runtime_observability import UnifiedRuntimeObservability

    assert OfficialConversationGateway is not None
    assert RuntimeHealthReadinessService is not None
    assert RuntimeOperationalSnapshotBuilder is not None
    assert RuntimeRecoveryPlanner is not None
    assert UnifiedRuntimeObservability is not None
