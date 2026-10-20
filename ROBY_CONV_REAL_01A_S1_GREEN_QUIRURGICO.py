# ruff: noqa: E501
"""CONV-REAL-01A-S1: minimal diagnostic propagation via official observability.

Run from the HAL project root. Only two canonical files are modified.
The operation checks exact source anchors and is idempotent.
"""

from pathlib import Path

ROOT = Path.cwd()
PIPELINE = ROOT / "core/governed_operational_conversation_pipeline/pipeline.py"
OBSERVABILITY = ROOT / "app/conversation_reliability_observability.py"


def replace_once(path: Path, old: str, new: str) -> bool:
    source = path.read_text(encoding="utf-8")
    if new in source:
        return False
    if source.count(old) != 1:
        raise RuntimeError(f"Expected exactly one canonical anchor in {path}")
    path.write_text(source.replace(old, new, 1), encoding="utf-8")
    return True


def main() -> None:
    if not PIPELINE.is_file() or not OBSERVABILITY.is_file():
        raise RuntimeError("Run from HAL root; canonical files not found")
    old_observability = """    def complete_turn(
        self,
        result: GovernedConversationPipelineResult,
"""
    new_observability = '''    def record_failure(
        self, request: GovernedConversationPipelineRequest, exc: Exception
    ) -> None:
        """Retain only the exception class in the existing pending official trace."""
        from dataclasses import replace

        key = (request.owner.casefold(), request.session_id)
        with self._lock:
            pending = self._pending.get(key)
            if pending is not None:
                self._pending[key] = replace(pending, error=type(exc).__name__)

    def complete_turn(
        self,
        result: GovernedConversationPipelineResult,
'''
    old_pipeline = """        except Exception:
            preparation = None
            provider_execution = None
            retrieval_execution = None
"""
    new_pipeline = """        except Exception as exc:
            record_failure = getattr(self.conversation_execution, "record_failure", None)
            if callable(record_failure):
                try:
                    record_failure(request, exc)
                except Exception:
                    pass  # Diagnostics must not defeat safe failure containment.
            preparation = None
            provider_execution = None
            retrieval_execution = None
"""
    # Preflight both anchors before any write.
    for path, old, new in (
        (OBSERVABILITY, old_observability, new_observability),
        (PIPELINE, old_pipeline, new_pipeline),
    ):
        content = path.read_text(encoding="utf-8")
        if new not in content and content.count(old) != 1:
            raise RuntimeError(f"Preflight failed: {path}")
    for path, old, new in (
        (OBSERVABILITY, old_observability, new_observability),
        (PIPELINE, old_pipeline, new_pipeline),
    ):
        changed = replace_once(path, old, new)
        print(f"{'PATCHED' if changed else 'UNCHANGED'}: {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
