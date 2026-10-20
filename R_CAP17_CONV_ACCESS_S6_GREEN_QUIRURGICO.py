"""S6 surgical patch: classify explicit library recommendation before title search.

Run from the HAL repository root. Fail closed if canonical anchors differ.
"""

from pathlib import Path

path = Path("app/governed_local_library_runtime_wiring.py")
source = path.read_text(encoding="utf-8")
if "_is_library_recommendation_request" in source:
    raise SystemExit("STOP: S6 already present; inspect manually")
anchor = (
    "    def intercept(self, request: GovernedConversationPipelineRequest, *, now):\n"
)
if source.count(anchor) != 1 or "_is_library_capability_question" not in source:
    raise SystemExit("STOP: expected S3 canonical anchors missing")
helper = """    @staticmethod
    def _is_library_recommendation_request(text: str) -> bool:
        normalized = " ".join(text.casefold().strip().split())
        # Explicit search remains the canonical route, including mixed requests.
        if re.search(r"\\b(?:busc[aá]|buscar|consult[aá]|encontr[aá])\\b", normalized):
            return False
        return (
            re.search(r"\\brecomend\\w*", normalized) is not None
            and re.search(
                r"\\b(?:biblioteca|mis libros|mis libros|mi biblioteca)\\b",
                normalized,
            ) is not None
        )

"""
helper = helper.replace(
    "mis libros|mis libros|mi biblioteca", "mis libros|mi biblioteca"
)
source = source.replace(anchor, helper + anchor, 1)
branch_anchor = (
    "        pending = self._active_follow_up(request.session_id, now=now)\n"
)
branch = """        if self._is_library_recommendation_request(request.text):
            return GovernedOperationalInterception(
                response_text=(
                    "Puedo ayudarte a elegir una lectura, pero todavía no "
                    "tengo evidencia suficiente del catálogo para recomendarte "
                    "un libro concreto de tu Biblioteca. Indicame un género, "
                    "autor o tema y puedo intentar buscar coincidencias; "
                    "una búsqueda parcial no garantiza cobertura completa."
                ),
                rationale="local_library_recommendation_evidence_required",
            )
"""
if source.count(branch_anchor) != 1:
    raise SystemExit("STOP: expected follow-up anchor absent or ambiguous")
source = source.replace(branch_anchor, branch + branch_anchor, 1)
compile(source, str(path), "exec")
path.write_text(source, encoding="utf-8")
print("S6 GREEN applied:", path)
