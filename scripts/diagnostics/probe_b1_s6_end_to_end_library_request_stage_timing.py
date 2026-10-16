from __future__ import annotations

import os
import time
from datetime import datetime, timezone
from pathlib import Path

from app.document_reading import DocumentReadingService
from app.external_retrieval_runtime import OfficialExternalRetrievalRuntimeGateway
from app.governed_local_library_conversation import GovernedLocalLibraryConversationV1
from app.governed_local_library_runtime_wiring import (
    GovernedLocalLibraryConversationInterceptionPort,
)
from app.knowledge_runtime import OfficialKnowledgeRuntimeGateway
from app.roby_config import activate_roby_config, resolve_roby_config_path
from app.unified_retrieval_execution_runtime import (
    OfficialUnifiedRetrievalExecutionRuntimeGateway,
)
from core.governed_local_library import (
    GovernedLocalLibraryCatalogueV1,
    GovernedLocalLibraryConfig,
)
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
)

REQUEST_TEXT = (
    "Roby, busca en la biblioteca el libro Robots e Imperio "
    "y decime cuando lo encontras"
)


class TimingCatalogue(GovernedLocalLibraryCatalogueV1):
    def __init__(self, config: GovernedLocalLibraryConfig) -> None:
        super().__init__(config)
        self.catalogue_calls = 0

    def catalogue(self):
        self.catalogue_calls += 1
        call = self.catalogue_calls
        started = time.perf_counter()
        print(f"B1-S6 catalogue[{call}] START", flush=True)
        result = super().catalogue()
        print(
            f"B1-S6 catalogue[{call}] END {time.perf_counter() - started:.3f}s "
            f"entries={len(result.entries)} truncated={result.truncated}",
            flush=True,
        )
        return result

    def search(self, query: str, *, max_results: int):
        started = time.perf_counter()
        print(f"B1-S6 search START query={query!r}", flush=True)
        result = super().search(query, max_results=max_results)
        print(
            f"B1-S6 search END {time.perf_counter() - started:.3f}s "
            f"matches={len(result.matches)} bounded={result.bounded}",
            flush=True,
        )
        return result


class TimingDocumentReader(DocumentReadingService):
    def read_text(self, path: Path) -> str:
        started = time.perf_counter()
        print(f"B1-S6 document_read START filename={path.name!r}", flush=True)
        try:
            content = super().read_text(path)
        finally:
            print(
                f"B1-S6 document_read END {time.perf_counter() - started:.3f}s",
                flush=True,
            )
        print(f"B1-S6 document_read chars={len(content)}", flush=True)
        return content


class TimingUnifiedRuntime(OfficialUnifiedRetrievalExecutionRuntimeGateway):
    def execute(self, request, *, now=None, execution_retrievers=None):
        started = time.perf_counter()
        print("B1-S6 unified_execute START", flush=True)
        try:
            return super().execute(
                request,
                now=now,
                execution_retrievers=execution_retrievers,
            )
        finally:
            print(
                f"B1-S6 unified_execute END {time.perf_counter() - started:.3f}s",
                flush=True,
            )


def main() -> int:
    config_path = resolve_roby_config_path()
    activate_roby_config(config_path)
    root_value = os.getenv("ROBY_LOCAL_LIBRARY_ROOT", "").strip()
    if not root_value:
        print("B1-S6 STOP: ROBY_LOCAL_LIBRARY_ROOT is not configured.")
        return 2
    root = Path(root_value).expanduser().resolve(strict=False)
    max_entries = int(os.getenv("ROBY_LOCAL_LIBRARY_MAX_CATALOGUE_ENTRIES", "10000"))
    print(f"B1-S6 config={config_path}", flush=True)
    print(f"B1-S6 root={root}", flush=True)
    print(f"B1-S6 max_catalogue_entries={max_entries}", flush=True)
    print(f"B1-S6 request={REQUEST_TEXT!r}", flush=True)

    catalogue = TimingCatalogue(
        GovernedLocalLibraryConfig(root=root, max_catalogue_entries=max_entries)
    )
    unified = TimingUnifiedRuntime(OfficialExternalRetrievalRuntimeGateway())
    conversation = GovernedLocalLibraryConversationV1(
        knowledge_runtime=OfficialKnowledgeRuntimeGateway(),
        library=catalogue,
        document_reader=TimingDocumentReader(),
        unified_runtime=unified,
    )
    interceptor = GovernedLocalLibraryConversationInterceptionPort(conversation)
    request = GovernedConversationPipelineRequest(
        owner=os.getenv("ROBY_RUNTIME_OWNER", "Carlos"),
        session_id="probe-b1-s6-diagnostic",
        text=REQUEST_TEXT,
    )

    started = time.perf_counter()
    print("B1-S6 interceptor START", flush=True)
    result = interceptor.intercept(request, now=datetime.now(timezone.utc))
    print(f"B1-S6 interceptor END {time.perf_counter() - started:.3f}s", flush=True)
    if result is None:
        print("B1-S6 result=None", flush=True)
    else:
        print(f"B1-S6 rationale={result.rationale}", flush=True)
        print(f"B1-S6 response_chars={len(result.response_text)}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
