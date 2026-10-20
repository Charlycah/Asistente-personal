# ruff: noqa: E501
"""S4-D7-C.3: surgical CAP-17 location boundary repair.

Run from HAL root. Validate all anchors before writing either file.
No historical tests, other production files, or governance docs are changed.
"""

from __future__ import annotations

import ast
from pathlib import Path

CONVERSATION = Path("app/governed_local_library_conversation.py")
WIRING = Path("app/governed_local_library_runtime_wiring.py")
original_conversation = CONVERSATION.read_text(encoding="utf-8")
original_wiring = WIRING.read_text(encoding="utf-8")

conversation_anchor = """    def handle_user_request(
"""
if original_conversation.count(conversation_anchor) != 1:
    raise SystemExit("STOP: canonical conversation anchor absent or duplicated")
if "def locate_admitted_request(" in original_conversation:
    raise SystemExit("STOP: location operation already exists; inspect manually")

method = '''    def locate_admitted_request(
        self,
        *,
        owner: str,
        search_query: str,
        now: datetime,
    ) -> GovernedLocalLibraryConversationResult:
        """Locate via the existing catalogue/selector; never read content."""
        if now.tzinfo is None:
            raise ValueError("library conversation time must be timezone-aware")
        query = search_query.strip()
        if not query:
            raise ValueError("library search query must not be blank")
        if "/" in query or "\\\\" in query:
            entry = self.library.lookup_explicit_relative_path(query)
            decision = self._selector.decide_explicit(query=query, entry=entry)
            candidates = (entry,) if entry is not None else ()
        else:
            search = self.library.search(query, max_results=self.max_results)
            decision = self._selector.decide(search)
            candidates = search.matches
        if decision.disposition is GovernedLibrarySelectionDisposition.NO_MATCH:
            return GovernedLocalLibraryConversationResult(
                status=GovernedLocalLibraryConversationStatus.NO_MATCH,
                query=query,
                bounded=decision.bounded,
                last_completed_stage="selection",
            )
        if (
            decision.disposition
            is GovernedLibrarySelectionDisposition.NEEDS_DISAMBIGUATION
        ):
            return GovernedLocalLibraryConversationResult(
                status=GovernedLocalLibraryConversationStatus.NEEDS_DISAMBIGUATION,
                query=query,
                candidates=decision.candidates,
                bounded=decision.bounded,
                last_completed_stage="selection",
            )
        selection = decision.selection
        if selection is None:
            raise RuntimeError("selected library disposition requires a selection")
        entry = next(
            (
                item
                for item in candidates
                if item is not None
                and item.entry_id == selection.entry_id
                and item.source_reference == selection.source_reference
            ),
            None,
        )
        if entry is None:
            raise RuntimeError("canonical library selection lost entry identity")
        return GovernedLocalLibraryConversationResult(
            status=GovernedLocalLibraryConversationStatus.COMPLETED,
            query=query,
            source_reference=selection.source_reference,
            safe_source_label=safe_local_document_filename(entry.filename),
            last_completed_stage="selection",
        )

'''

start = (
    """        # S4-D7-B: a location request must not invoke document retrieval.\n"""
)
end = (
    "        if admitted:\n"
    "            result = self.conversation.handle_user_request(\n"
)
if original_wiring.count(start) != 1 or original_wiring.count(end) != 1:
    raise SystemExit("STOP: S4-D7-B location anchors absent or duplicated")
i = original_wiring.index(start)
j = original_wiring.index(end, i)
if j <= i:
    raise SystemExit("STOP: unexpected interceptor ordering")
replacement = """        # LOCALIZAR is owned by the canonical conversation, not this adapter.
        if admitted and self._is_location_only(request.text):
            locate = getattr(self.conversation, "locate_admitted_request", None)
            if locate is None:
                # Historical doubles cannot establish catalogue evidence.
                # Fail closed; never fall back to document content retrieval.
                return GovernedOperationalInterception(
                    response_text=(
                        "No puedo verificar la ubicación de ese documento "
                        "con la interfaz de Biblioteca disponible."
                    ),
                    rationale="local_library_location_unavailable",
                )
            result = locate(
                owner=request.owner,
                search_query=query,
                now=now,
            )
            self._pending_follow_ups.pop(request.session_id, None)
            if result.status is GovernedLocalLibraryConversationStatus.NO_MATCH:
                if result.bounded:
                    return GovernedOperationalInterception(
                        response_text=(
                            f"La búsqueda de {query!r} en la Biblioteca autorizada "
                            "fue incompleta por un límite del catálogo. "
                            "No puedo confirmar que el documento no exista."
                        ),
                        rationale="local_library_incomplete_no_match",
                    )
                return GovernedOperationalInterception(
                    response_text=(
                        f"No encontré coincidencias para {query!r} "
                        "en la Biblioteca autorizada."
                    ),
                    rationale="local_library_no_match",
                )
            if (
                result.status
                is GovernedLocalLibraryConversationStatus.NEEDS_DISAMBIGUATION
            ):
                self._remember_follow_up(request.session_id, now=now)
                names = "\\n".join(
                    f"- {safe_local_document_filename(item.filename)}"
                    for item in result.candidates
                )
                return GovernedOperationalInterception(
                    response_text=(
                        "Encontré varias coincidencias en la Biblioteca. "
                        "Indicame cuál querés consultar:\\n" + names
                    ),
                    rationale="local_library_disambiguation_required",
                )
            if result.status is GovernedLocalLibraryConversationStatus.COMPLETED:
                label = safe_local_document_filename(result.safe_source_label)
                if label is None:
                    return GovernedOperationalInterception(
                        response_text="Encontré un documento en tu Biblioteca.",
                        rationale="local_library_location_completed",
                    )
                return GovernedOperationalInterception(
                    response_text=f"Encontré en tu Biblioteca: {label}.",
                    rationale="local_library_location_completed",
                )
            return GovernedOperationalInterception(
                response_text="No pude completar la búsqueda gobernada.",
                rationale="local_library_location_failed",
            )

"""

new_conversation = original_conversation.replace(
    conversation_anchor, method + conversation_anchor, 1
)
new_wiring = original_wiring[:i] + replacement + original_wiring[j:]
for path, source in ((CONVERSATION, new_conversation), (WIRING, new_wiring)):
    ast.parse(source, filename=str(path))

CONVERSATION.write_text(new_conversation, encoding="utf-8")
WIRING.write_text(new_wiring, encoding="utf-8")
print("S4_D7_C3_GREEN_APPLIED:", CONVERSATION, WIRING)
