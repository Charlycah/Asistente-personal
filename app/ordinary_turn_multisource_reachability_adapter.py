from __future__ import annotations

from datetime import datetime


class OrdinaryTurnMultisourceReachabilityAdapterV1:
    """Transport explicit ordinary-turn selections to the certified convergence seam."""

    def __init__(self, *, same_episode_adapter: object) -> None:
        if not callable(getattr(same_episode_adapter, "admit_and_reason", None)):
            raise TypeError(
                "ordinary-turn reachability requires same-episode convergence authority"
            )
        self._same_episode_adapter = same_episode_adapter

    def admit_and_reason(
        self,
        *,
        text: str,
        owner: str,
        explicit_document_ids: tuple[str, ...],
        explicit_sources: tuple[object, ...],
        explicit_evidence_references: tuple[object, ...],
        visual_context_contribution: object | None,
        now: datetime,
    ):
        """Delegate one explicit-evidence turn without discovery or reinterpretation."""
        if not (
            explicit_document_ids
            or explicit_sources
            or explicit_evidence_references
        ):
            return None

        return self._same_episode_adapter.admit_and_reason(
            text=text,
            owner=owner,
            explicit_document_ids=explicit_document_ids,
            explicit_sources=explicit_sources,
            explicit_evidence_references=explicit_evidence_references,
            visual_context_contribution=visual_context_contribution,
            now=now,
        )
