# ruff: noqa: E501
from pathlib import Path

path = Path("app/governed_local_library_runtime_wiring.py")
if not path.is_file():
    raise SystemExit("STOP: canonical interceptor missing")
source = path.read_text(encoding="utf-8")
needle = """    def intercept(self, request: GovernedConversationPipelineRequest, *, now):
        pending = self._active_follow_up(request.session_id, now=now)
"""
replacement = """    @staticmethod
    def _is_library_capability_question(text: str) -> bool:
        normalized = " ".join(text.casefold().strip().split())
        normalized = normalized.lstrip("¿").rstrip("?!. ")
        # Match a bounded capability question, not a document-search request.
        return re.fullmatch(
            r"(?:roby[, ]+)?(?:"
            r"(?:pod[eé]s|puedes|puede|podr[ií]as|podr[ií]a)\\s+"
            r"(?:tener\\s+)?acceso\\s+a\\s+"
            r"(?:la|mi)\\s+biblioteca"
            r"|(?:pod[eé]s|puedes|puede|podr[ií]as|podr[ií]a)\\s+"
            r"acceder\\s+a\\s+(?:la|mi)\\s+biblioteca"
            r"|(?:ten[eé]s|tienes|tiene)\\s+acceso\\s+a\\s+"
            r"(?:mis\\s+libros|mi\\s+biblioteca|la\\s+biblioteca)"
            r")",
            normalized,
        ) is not None

    def intercept(self, request: GovernedConversationPipelineRequest, *, now):
        if self._is_library_capability_question(request.text):
            return GovernedOperationalInterception(
                response_text=(
                    "La Biblioteca local está configurada para consultas "
                    "gobernadas en esta sesión. Puedo intentar buscar un libro "
                    "o documento si me indicás cuál; eso no confirma que "
                    "cada archivo sea legible ni que una búsqueda sea completa."
                ),
                rationale="local_library_capability_status",
            )
        pending = self._active_follow_up(request.session_id, now=now)
"""
# Replacement uses raw regex backslashes in source; adjust escaped literals.
replacement = replacement.replace("\\\\s", "\\s")
if source.count(needle) != 1:
    raise SystemExit("STOP: expected interception anchor absent or ambiguous")
if "_is_library_capability_question" in source:
    raise SystemExit("STOP: capability guard already exists")
updated = source.replace(needle, replacement, 1)
compile(updated, str(path), "exec")
path.write_text(updated, encoding="utf-8")
print("S3 GREEN applied:", path)
