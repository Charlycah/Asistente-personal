from __future__ import annotations

import re
from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256

_SCHEMA_VERSION = "cih-2e-explicit-turn-proposition-grounding-v1"


class ExplicitTurnPropositionGroundingStatus(StrEnum):
    GROUNDED = "grounded"
    AMBIGUOUS = "ambiguous"
    UNSUPPORTED = "unsupported"
    INSUFFICIENT = "insufficient"


@dataclass(frozen=True)
class ExplicitTurnProposition:
    subject: str
    predicate: str
    object_value: str
    source_text: str
    start_offset: int
    end_offset: int
    source_fingerprint: str

    def __post_init__(self) -> None:
        for value, label in (
            (self.subject, "subject"),
            (self.predicate, "predicate"),
            (self.object_value, "object"),
            (self.source_text, "source text"),
        ):
            if not value.strip():
                raise ValueError(f"explicit proposition {label} must not be blank")
        if self.start_offset < 0 or self.end_offset <= self.start_offset:
            raise ValueError("explicit proposition source span is invalid")
        if len(self.source_fingerprint) != 64:
            raise ValueError("explicit proposition fingerprint must be SHA-256")


@dataclass(frozen=True)
class GovernedExplicitTurnPropositionGrounding:
    status: ExplicitTurnPropositionGroundingStatus | str
    propositions: tuple[ExplicitTurnProposition, ...]
    source_reference: str
    scope_reference: str
    source_fingerprint: str
    rationale_codes: tuple[str, ...]
    schema_version: str = _SCHEMA_VERSION
    canonical_authority: str = "governed_reasoning"
    read_only: bool = True
    session_local: bool = True
    transient: bool = True
    persists_results: bool = False
    creates_memory: bool = False
    modifies_memory: bool = False
    creates_learning_candidate: bool = False
    modifies_learning: bool = False
    modifies_world_model: bool = False
    establishes_truth: bool = False
    establishes_falsity: bool = False
    authorizes_inference: bool = False
    authorizes_action: bool = False
    registers_claims: bool = False
    registers_rule: bool = False
    uses_provider: bool = False
    uses_retrieval: bool = False
    executes_actions: bool = False
    grants_authority: bool = False
    starts_background_process: bool = False

    def __post_init__(self) -> None:
        status = ExplicitTurnPropositionGroundingStatus(self.status)
        if self.canonical_authority != "governed_reasoning":
            raise ValueError(
                "explicit-turn grounding must preserve governed reasoning authority"
            )
        if not self.source_reference.strip() or not self.scope_reference.strip():
            raise ValueError("explicit-turn grounding requires provenance and scope")
        if len(self.source_fingerprint) != 64:
            raise ValueError("explicit-turn grounding fingerprint must be SHA-256")
        if not self.rationale_codes or any(
            not code.strip() for code in self.rationale_codes
        ):
            raise ValueError("explicit-turn grounding requires rationale codes")
        if any(
            (
                not self.read_only,
                not self.session_local,
                not self.transient,
                self.persists_results,
                self.creates_memory,
                self.modifies_memory,
                self.creates_learning_candidate,
                self.modifies_learning,
                self.modifies_world_model,
                self.establishes_truth,
                self.establishes_falsity,
                self.authorizes_inference,
                self.authorizes_action,
                self.registers_claims,
                self.registers_rule,
                self.uses_provider,
                self.uses_retrieval,
                self.executes_actions,
                self.grants_authority,
                self.starts_background_process,
            )
        ):
            raise ValueError("explicit-turn grounding violates governed limits")
        if status is ExplicitTurnPropositionGroundingStatus.GROUNDED:
            if not self.propositions:
                raise ValueError("grounded explicit-turn result requires propositions")
        elif self.propositions:
            raise ValueError(
                "non-grounded explicit-turn result cannot expose propositions"
            )
        object.__setattr__(self, "status", status)


class GovernedBoundedExplicitTurnPropositionGrounder:
    """Ground only certified explicit proposition families from the current turn."""

    _VISITOR_RE = re.compile(
        r"\bmañana\s+viene\s+alguien\s+a\s+casa\b",
        re.IGNORECASE,
    )
    _PENDING_ORGANIZATION_RE = re.compile(
        r"\b(?:todavía\s+)?me\s+falta\s+organizar\s+(?P<object>[^.!?]+?)"
        r"(?=\s*(?:[.!?]|$))",
        re.IGNORECASE,
    )
    _AMBIGUOUS_PERSON_RE = re.compile(
        r"^\s*(?:ella|él|ellos|ellas)\b",
        re.IGNORECASE,
    )
    _SUPPOSITION_RE = re.compile(
        r"^\s*(?:supongamos|supone|suponé|imagina|imaginemos)\b",
        re.IGNORECASE,
    )

    def ground(
        self,
        text: str,
        *,
        source_reference: str,
        scope_reference: str,
    ) -> GovernedExplicitTurnPropositionGrounding:
        if not source_reference.strip() or not scope_reference.strip():
            raise ValueError("explicit-turn grounding requires provenance and scope")
        source = text if isinstance(text, str) else str(text)
        fingerprint = sha256(source.encode("utf-8")).hexdigest()
        if not source.strip():
            return self._result(
                ExplicitTurnPropositionGroundingStatus.INSUFFICIENT,
                source_reference,
                scope_reference,
                fingerprint,
                ("explicit_turn:blank_or_empty",),
            )
        if self._is_question(source):
            return self._result(
                ExplicitTurnPropositionGroundingStatus.UNSUPPORTED,
                source_reference,
                scope_reference,
                fingerprint,
                ("explicit_turn:question_not_assertion",),
            )
        if self._SUPPOSITION_RE.search(source):
            return self._result(
                ExplicitTurnPropositionGroundingStatus.UNSUPPORTED,
                source_reference,
                scope_reference,
                fingerprint,
                ("explicit_turn:supposition_not_assertion",),
            )
        if self._AMBIGUOUS_PERSON_RE.search(source):
            return self._result(
                ExplicitTurnPropositionGroundingStatus.AMBIGUOUS,
                source_reference,
                scope_reference,
                fingerprint,
                ("explicit_turn:ambiguous_person_reference",),
            )

        propositions: list[ExplicitTurnProposition] = []
        visitor = self._VISITOR_RE.search(source)
        if visitor is not None:
            propositions.append(
                self._proposition(
                    subject="alguien",
                    predicate="viene_a_casa",
                    object_value="mañana",
                    source=source,
                    start=visitor.start(),
                    end=visitor.end(),
                )
            )
        pending = self._PENDING_ORGANIZATION_RE.search(source)
        if pending is not None:
            object_value = " ".join(pending.group("object").strip().split())
            propositions.append(
                self._proposition(
                    subject="interlocutor",
                    predicate="falta_organizar",
                    object_value=object_value,
                    source=source,
                    start=pending.start(),
                    end=pending.end(),
                )
            )
        if not propositions:
            return self._result(
                ExplicitTurnPropositionGroundingStatus.UNSUPPORTED,
                source_reference,
                scope_reference,
                fingerprint,
                ("explicit_turn:no_certified_explicit_proposition_family",),
            )
        return self._result(
            ExplicitTurnPropositionGroundingStatus.GROUNDED,
            source_reference,
            scope_reference,
            fingerprint,
            (
                "explicit_turn:certified_current_turn_proposition",
                "explicit_turn:source_spans_preserved",
                "explicit_turn:non_authoritative_grounding",
            ),
            propositions=tuple(propositions),
        )

    @staticmethod
    def _is_question(text: str) -> bool:
        clean = text.strip()
        return clean.startswith("¿") or clean.endswith("?")

    @staticmethod
    def _proposition(
        *,
        subject: str,
        predicate: str,
        object_value: str,
        source: str,
        start: int,
        end: int,
    ) -> ExplicitTurnProposition:
        source_text = source[start:end]
        fingerprint = sha256(
            repr(
                (
                    subject,
                    predicate,
                    object_value,
                    source_text,
                    start,
                    end,
                )
            ).encode("utf-8")
        ).hexdigest()
        return ExplicitTurnProposition(
            subject=subject,
            predicate=predicate,
            object_value=object_value,
            source_text=source_text,
            start_offset=start,
            end_offset=end,
            source_fingerprint=fingerprint,
        )

    @staticmethod
    def _result(
        status: ExplicitTurnPropositionGroundingStatus,
        source_reference: str,
        scope_reference: str,
        source_fingerprint: str,
        rationale_codes: tuple[str, ...],
        *,
        propositions: tuple[ExplicitTurnProposition, ...] = (),
    ) -> GovernedExplicitTurnPropositionGrounding:
        return GovernedExplicitTurnPropositionGrounding(
            status=status,
            propositions=propositions,
            source_reference=source_reference,
            scope_reference=scope_reference,
            source_fingerprint=source_fingerprint,
            rationale_codes=rationale_codes,
        )
