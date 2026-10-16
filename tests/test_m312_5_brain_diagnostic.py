from __future__ import annotations

import json
from datetime import datetime, timezone

from app.memory_consolidation import OfficialMemoryGateway
from application.brain import (
    BrainDiagnostic,
    BrainQuery,
    BrainService,
    build_official_memory_brain_composition,
)
from core.memory_runtime_integration import (
    MemoryRuntimeConfig,
    MemoryRuntimeIntegration,
)
from domain.brain import BrainMemory, BrainMemoryType
from infrastructure.brain import AtomicJsonBrainRepository
from scripts.brain_diagnostic import main


def build_runtime(tmp_path):
    return MemoryRuntimeIntegration(
        MemoryRuntimeConfig(root_path=tmp_path / ".roby" / "memory")
    )


def test_m312_5_reports_local_and_official_memories(tmp_path):
    runtime = build_runtime(tmp_path)
    runtime.store_explicit(owner="Carlos", text="La memoria oficial está activa.")
    composition = build_official_memory_brain_composition(
        brain_repository=AtomicJsonBrainRepository(tmp_path / ".roby" / "brain"),
        memory_gateway=OfficialMemoryGateway(runtime, owner="Carlos"),
        owner="Carlos",
    )
    composition.service.remember(
        BrainMemory(
            content="El diagnóstico local está listo.",
            memory_type=BrainMemoryType.WORKING,
            subject="Carlos",
            source="brain_local",
        )
    )

    report = BrainDiagnostic(composition.service).inspect(BrainQuery(limit=10))

    assert report.total_count == 2
    assert report.local_count == 1
    assert report.official_count == 1
    assert {entry.source for entry in report.entries} == {
        "brain_local",
        "official_memory",
    }


def test_m312_5_respects_query_filters(tmp_path):
    repository = AtomicJsonBrainRepository(tmp_path / ".roby" / "brain")
    service = BrainService(repository)
    service.remember(
        BrainMemory(
            content="Carlos prefiere respuestas breves.",
            memory_type=BrainMemoryType.PROFILE,
            subject="Carlos",
        )
    )
    service.remember(
        BrainMemory(
            content="Revisar el calendario mañana.",
            memory_type=BrainMemoryType.WORKING,
            subject="Carlos",
        )
    )

    report = BrainDiagnostic(service).inspect(
        BrainQuery(text="breves", memory_type=BrainMemoryType.PROFILE)
    )

    assert report.total_count == 1
    assert report.entries[0].content == "Carlos prefiere respuestas breves."


def test_m312_5_marks_official_entries_as_read_only(tmp_path):
    runtime = build_runtime(tmp_path)
    runtime.store_explicit(owner="Carlos", text="Dato histórico oficial.")
    composition = build_official_memory_brain_composition(
        brain_repository=AtomicJsonBrainRepository(tmp_path / ".roby" / "brain"),
        memory_gateway=OfficialMemoryGateway(runtime, owner="Carlos"),
        owner="Carlos",
    )

    report = BrainDiagnostic(composition.service).inspect(BrainQuery())

    assert report.entries[0].read_only is True
    assert report.entries[0].memory_id.startswith("official:")


def test_m312_5_report_is_json_serializable(tmp_path):
    service = BrainService(AtomicJsonBrainRepository(tmp_path / "brain"))
    service.remember(
        BrainMemory(
            content="Prueba JSON.",
            memory_type=BrainMemoryType.LEARNING,
            subject="ROBY",
            created_at=datetime(2026, 7, 23, tzinfo=timezone.utc),
            updated_at=datetime(2026, 7, 23, tzinfo=timezone.utc),
        )
    )

    payload = BrainDiagnostic(service).inspect(BrainQuery()).to_dict()

    assert json.loads(json.dumps(payload))["summary"]["total"] == 1


def test_m312_5_cli_is_read_only_and_prints_json(tmp_path, capsys):
    brain_root = tmp_path / ".roby" / "brain"
    repository = AtomicJsonBrainRepository(brain_root)
    service = BrainService(repository)
    service.remember(
        BrainMemory(
            content="Recuerdo local para diagnóstico.",
            memory_type=BrainMemoryType.WORKING,
            subject="Carlos",
        )
    )
    before = repository.memories_path.read_bytes()

    result = main(
        [
            "--owner",
            "Carlos",
            "--query",
            "diagnóstico",
            "--project-root",
            str(tmp_path),
        ]
    )

    output = json.loads(capsys.readouterr().out)
    assert result == 0
    assert output["summary"]["local"] == 1
    assert repository.memories_path.read_bytes() == before
