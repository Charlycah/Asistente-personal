"""R-CAP17-O3-S15: diagnostic only, no production/library writes."""
from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter

from app.document_reading import DocumentReadingService
from app.external_retrieval_runtime import OfficialExternalRetrievalRuntimeGateway
from app.governed_local_library_conversation import GovernedLocalLibraryConversationV1
from app.knowledge_runtime import OfficialKnowledgeRuntimeGateway
from app.unified_retrieval_execution_runtime import (
    OfficialUnifiedRetrievalExecutionRuntimeGateway,
)
from core.governed_local_library import (
    GovernedLocalLibraryCatalogueV1,
    GovernedLocalLibraryConfig,
)

RELATIVE = "Robots e Imperio (15050)/Robots e Imperio - Isaac Asimov.epub"
EXPECTED_ROOT = Path(r"D:\Biblioteca")


def main() -> None:
    configured = os.environ.get("ROBY_LOCAL_LIBRARY_ROOT", "").strip()
    if not configured:
        raise SystemExit("STOP: ROBY_LOCAL_LIBRARY_ROOT no esta configurada")
    root = Path(configured).resolve(strict=True)
    if root != EXPECTED_ROOT.resolve(strict=True):
        raise SystemExit("STOP: la raiz configurada no coincide con D:\\Biblioteca")

    library = GovernedLocalLibraryCatalogueV1(
        GovernedLocalLibraryConfig(root=root, max_catalogue_entries=10_000)
    )
    target = root / Path(RELATIVE)
    if not target.is_file():
        raise SystemExit("STOP: el EPUB anidado no existe")

    scan_calls = [0]

    def forbidden_scan():
        scan_calls[0] += 1
        raise AssertionError("S15: se intento enumerar el catalogo")

    # Guard against any catalogue enumeration during the real-world diagnostic.
    library._scan_entries = forbidden_scan
    start = perf_counter()
    entry = library.lookup_explicit_relative_path(RELATIVE)
    lookup_ms = (perf_counter() - start) * 1000

    runtime = OfficialUnifiedRetrievalExecutionRuntimeGateway(
        OfficialExternalRetrievalRuntimeGateway()
    )
    conversation = GovernedLocalLibraryConversationV1(
        knowledge_runtime=OfficialKnowledgeRuntimeGateway(),
        library=library,
        document_reader=DocumentReadingService(),
        unified_runtime=runtime,
    )
    request_text = f'Buscá en la biblioteca "{RELATIVE}"'
    start = perf_counter()
    result = conversation.handle_user_request(
        owner="Owner",
        text=request_text,
        search_query=RELATIVE,
        now=datetime.now(timezone.utc),
    )
    conversation_ms = (perf_counter() - start) * 1000

    artifact = result.artifact
    provenance_ok = bool(
        artifact is not None
        and entry.source_reference == result.source_reference
        and entry.source_reference in artifact.references
    )
    print("S15_DIAGNOSTICO_REAL")
    print(f"status={result.status.value}")
    print(f"lookup_ms={lookup_ms:.2f}")
    print(f"conversation_ms={conversation_ms:.2f}")
    print(f"scan_calls={scan_calls[0]}")
    print(f"selected_relative_path_ok={entry.relative_path == RELATIVE}")
    print(f"provenance_ok={provenance_ok}")
    print(f"safe_label={result.safe_source_label!r}")
    print(f"artifact_chars={len(artifact.content) if artifact else 0}")
    print(f"runtime_evaluations={runtime.snapshot.evaluations}")
    for stage, elapsed_ms in result.stage_elapsed_ms:
        print(f"stage_{stage}_ms={elapsed_ms:.2f}")
    passed = (
        result.status.value == "completed"
        and scan_calls[0] == 0
        and entry.relative_path == RELATIVE
        and provenance_ok
        and bool(artifact and artifact.content)
        and runtime.snapshot.evaluations == 1
    )
    print(f"S15_RESULT={'PASS' if passed else 'FAIL'}")
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
