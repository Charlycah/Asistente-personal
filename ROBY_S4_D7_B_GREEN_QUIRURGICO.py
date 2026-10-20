# ruff: noqa: E501
"""S4-D7-B: guarded surgical patch for the existing CAP-17 interceptor.

Run from the ROBY repository root. Never silently overwrite unexpected code.
"""

from __future__ import annotations

import ast
from pathlib import Path

TARGET = Path("app/governed_local_library_runtime_wiring.py")
source = TARGET.read_text(encoding="utf-8")

anchor = """        if admitted:
            result = self.conversation.handle_user_request(
"""
if source.count(anchor) != 1:
    raise SystemExit("STOP: productive interception anchor changed; no files written")

addition = """        # S4-D7-B: a location request must not invoke document retrieval.
        # Use the already-authoritative catalogue and conversational selector.
        if admitted and self._is_location_only(request.text):
            from core.governed_local_library.conversation_selection import (
                GovernedLibrarySelectionDisposition,
            )

            if "/" in query or "\\\\" in query:
                entry = self.conversation.library.lookup_explicit_relative_path(query)
                decision = self.conversation._selector.decide_explicit(
                    query=query, entry=entry
                )
                matches = (entry,)
            else:
                search = self.conversation.library.search(
                    query, max_results=self.conversation.max_results
                )
                decision = self.conversation._selector.decide(search)
                matches = search.matches
            self._pending_follow_ups.pop(request.session_id, None)
            if decision.disposition is GovernedLibrarySelectionDisposition.NO_MATCH:
                if decision.bounded:
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
                decision.disposition
                is GovernedLibrarySelectionDisposition.NEEDS_DISAMBIGUATION
            ):
                self._remember_follow_up(request.session_id, now=now)
                names = "\\n".join(
                    f"- {safe_local_document_filename(item.filename)}"
                    for item in decision.candidates
                )
                return GovernedOperationalInterception(
                    response_text=(
                        "Encontré varias coincidencias en la Biblioteca. "
                        "Indicame cuál querés consultar:\\n" + names
                    ),
                    rationale="local_library_disambiguation_required",
                )
            selected = decision.selection
            entry = next(
                (
                    item for item in matches
                    if selected is not None and item.entry_id == selected.entry_id
                ),
                None,
            )
            if entry is None:
                raise RuntimeError("canonical library selection lost entry identity")
            label = safe_local_document_filename(entry.filename)
            return GovernedOperationalInterception(
                response_text=f"Encontré en tu Biblioteca: {label}.",
                rationale="local_library_location_completed",
            )

"""
source = source.replace(anchor, addition + anchor, 1)

anchor2 = """    @classmethod
    def _search_query(cls, text: str) -> str:
"""
if source.count(anchor2) != 1:
    raise SystemExit("STOP: search query anchor changed; no files written")

helper = """    @staticmethod
    def _is_location_only(text: str) -> bool:
        normalized = text.casefold()
        # Explicit prohibition takes precedence over a reading verb.
        if re.search(r"\\b(?:pero\\s+)?no\\s+lo\\s+leas\\b", normalized):
            return True
        return not bool(
            re.search(
                r"\\b(?:le[eé]|lee|leelo|léelo|narr[aá]melo|narramelo|"
                r"leer|narrar|escucharlo|resum[ií]|analiz[aá]|"
                r"revis[aá]\\s+el\\s+contenido)\\b",
                normalized,
            )
        )

"""
source = source.replace(anchor2, helper + anchor2, 1)

anchor3 = """        # Only the residual explicit-search path needs title cleanup.
"""
if source.count(anchor3) != 1:
    raise SystemExit("STOP: title-cleanup anchor changed; no files written")

cleanup = """        # Strip compound operation and negation clauses before title matching.
        query = re.sub(
            r"\\s*,?\\s*pero\\s+no\\s+lo\\s+leas\\s*[.?!]*$",
            "",
            query,
            flags=re.IGNORECASE,
        )
        query = re.sub(
            r"\\s+y\\s+(?:leelo|léelo|narr[aá]melo|narramelo)\\s*[.?!]*$",
            "",
            query,
            flags=re.IGNORECASE,
        )
        query = re.sub(
            r"^(?:le[eé]|lee|léeme|leeme)\\s+(?:el\\s+)?libro\\s+",
            "",
            query,
            count=1,
            flags=re.IGNORECASE,
        )
        query = re.sub(
            r"\\s+de\\s+mi\\s+biblioteca\\s*[.?!]*$",
            "",
            query,
            flags=re.IGNORECASE,
        )
"""
source = source.replace(anchor3, cleanup + anchor3, 1)

ast.parse(source, filename=str(TARGET))
# Avoid accidental second application.
if source.count("S4-D7-B: a location request") != 1:
    raise SystemExit("STOP: duplicate S4-D7-B marker; no files written")
TARGET.write_text(source, encoding="utf-8")
print("S4_D7_B_PATCH_APPLIED:", TARGET)
print("NEXT: pytest contract + historical tests, ruff, git diff --check")
