"""Structural, non-authorizing cross-domain operation evidence."""

from dataclasses import dataclass

from app.cross_domain_context_resolver import ContextDomain


@dataclass(frozen=True)
class CrossDomainOperationEvidence:
    """Describes an operation; does not prove execution or grant authority."""

    owner: str
    session_id: str
    domain: ContextDomain
    operation: str
    execution_id: str
    outcome: str

    def __post_init__(self) -> None:
        for name in (
            "owner",
            "session_id",
            "operation",
            "execution_id",
            "outcome",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a nonempty string")
            if value != value.strip():
                raise ValueError(f"{name} must be normalized")

        if not isinstance(self.domain, ContextDomain):
            raise ValueError("domain must be a ContextDomain")