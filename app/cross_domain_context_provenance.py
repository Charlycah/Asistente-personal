"""In-memory, non-authorizing provenance for cross-domain context."""

from dataclasses import dataclass

from app.cross_domain_context_resolver import (
    ContextAntecedent,
    ContextDomain,
)


@dataclass(frozen=True)
class ContextProvenanceRecord:
    turn_id: str
    owner: str
    session_id: str
    domain: ContextDomain
    sequence: int
    provenance: str

    def __post_init__(self) -> None:
        for name in ("turn_id", "owner", "session_id", "provenance"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a nonempty string")
        if not isinstance(self.domain, ContextDomain):
            raise ValueError("domain must be a ContextDomain")
        if type(self.sequence) is not int or self.sequence <= 0:
            raise ValueError("sequence must be a positive integer")


class CrossDomainContextProvenance:
    """Stores explicit provenance, never permissions or capabilities."""

    def __init__(self) -> None:
        self._records: dict[str, ContextProvenanceRecord] = {}

    def register(self, record: ContextProvenanceRecord) -> None:
        previous = self._records.get(record.turn_id)
        if previous is not None and previous != record:
            raise ValueError("conflicting provenance for turn_id")
        self._records[record.turn_id] = record

    def authorized_antecedents(
        self,
        turns: tuple[object, ...],
        *,
        owner: str,
        session_id: str,
    ) -> tuple[ContextAntecedent, ...]:
        if not isinstance(owner, str) or not owner.strip():
            return ()
        if not isinstance(session_id, str) or not session_id.strip():
            return ()

        selected: list[ContextAntecedent] = []
        seen: set[str] = set()

        for turn in turns:
            turn_id = getattr(turn, "turn_id", None)
            if not isinstance(turn_id, str) or turn_id in seen:
                continue

            record = self._records.get(turn_id)
            if record is None:
                continue

            if (
                record.owner != owner
                or record.session_id != session_id
                or getattr(turn, "owner", None) != owner
                or getattr(turn, "session_id", None) != session_id
                or getattr(turn, "sequence", None) != record.sequence
            ):
                continue

            selected.append(
                ContextAntecedent(
                    turn_id=record.turn_id,
                    owner=record.owner,
                    session_id=record.session_id,
                    domain=record.domain,
                    sequence=record.sequence,
                    provenance=record.provenance,
                    authorized=True,
                )
            )
            seen.add(turn_id)

        return tuple(selected)
