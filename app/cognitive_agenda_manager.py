from __future__ import annotations

import sqlite3
from collections.abc import Iterable, Sequence
from dataclasses import replace
from datetime import datetime, timezone

from domain.cognitive_agenda import (
    CognitiveAgendaItem,
    CognitiveAgendaKind,
    CognitiveAgendaOperationalHealth,
    CognitiveAgendaOperationalStatus,
    CognitiveAgendaPlanEntry,
    CognitiveAgendaPolicy,
    CognitiveAgendaRepository,
    CognitiveAgendaSignal,
    CognitiveAgendaSnapshot,
    CognitiveAgendaSource,
    CognitiveAgendaStatus,
    CognitiveCommitmentStatus,
    CognitiveMetacognitiveStatus,
)


class CognitiveAgendaManager:
    """Build an ephemeral executive view over authoritative runtime signals."""

    def __init__(
        self,
        sources: Iterable[CognitiveAgendaSource] = (),
        *,
        policy: CognitiveAgendaPolicy | None = None,
        repository: CognitiveAgendaRepository | None = None,
    ) -> None:
        self.sources = tuple(sources)
        self.policy = policy or CognitiveAgendaPolicy()
        self.repository = repository
        self._repository_failures: list[str] = []
        restored = self._repository_load_open()
        restored = tuple(sorted(restored, key=lambda item: (-item.score, item.key)))
        restored = restored[: self.policy.capacity]
        restored_at = datetime.now(timezone.utc)
        plan = self._build_deliberative_queue(restored, restored_at, set())
        primary = plan[0].item if plan else None
        rationale = (
            "agenda_activation:selected:"
            f"{primary.key}:score="
            f"{self._activation_score(primary, restored_at):.3f}"
            if primary is not None
            else "agenda_activation:none:no_eligible_items"
        )
        self._snapshot = CognitiveAgendaSnapshot(
            generated_at=restored_at,
            items=restored,
            primary_focus=restored[0] if restored else None,
            activated_focus=primary,
            activation_rationale=rationale,
            activation_evaluated=True,
            deliberative_queue=plan,
            planning_rationale=self._planning_rationale(plan),
            active_commitment=(
                primary
                if primary is not None
                and primary.commitment_status is CognitiveCommitmentStatus.IN_PROGRESS
                else None
            ),
            execution_rationale="agenda_execution:restored",
            metacognitive_review=(
                primary if primary is not None and primary.review_count else None
            ),
            metacognitive_rationale=self._metacognitive_rationale(primary),
            adaptive_learning=(
                primary
                if primary is not None and primary.learning_event_count
                else None
            ),
            adaptive_learning_rationale=(
                primary.learning_rationale if primary is not None else ""
            ),
        )
        self._snapshot = self._with_operational_health(self._snapshot)

    @property
    def snapshot(self) -> CognitiveAgendaSnapshot:
        return self._snapshot

    def refresh(
        self,
        *,
        now: datetime | None = None,
        context_facts: Iterable[str] = (),
    ) -> CognitiveAgendaSnapshot:
        timestamp = now or datetime.now(timezone.utc)
        signals: list[CognitiveAgendaSignal] = []
        failures: list[str] = []
        successful_sources: set[str] = set()
        source_absence_status: dict[str, CognitiveAgendaStatus] = {}
        facts = {
            self._normalize_condition(fact) for fact in context_facts if fact.strip()
        }
        for source in self.sources:
            try:
                signals.extend(source.collect(now=timestamp))
                successful_sources.add(source.name)
                absence_status = getattr(source, "absence_status", None)
                if absence_status is not None:
                    source_absence_status[source.name] = absence_status
            except (RuntimeError, ValueError, TypeError, OSError):
                failures.append(source.name)

        previous = {item.key: item for item in self._snapshot.items}
        grouped: dict[str, list[CognitiveAgendaSignal]] = {}
        for signal in signals:
            if signal.expires_at is not None and signal.expires_at <= timestamp:
                continue
            persisted_status = (
                self._repository_status_for(signal.key)
                if self.repository is not None
                else None
            )
            if persisted_status in {
                CognitiveAgendaStatus.CLOSED,
                CognitiveAgendaStatus.ARCHIVED,
            }:
                continue
            grouped.setdefault(signal.key, []).append(signal)

        items = []
        for key, group in grouped.items():
            item = self._merge(key, group, previous.get(key), timestamp)
            transitioned = self._apply_context(item, facts)
            if transitioned.status in {
                CognitiveAgendaStatus.CLOSED,
                CognitiveAgendaStatus.ARCHIVED,
            }:
                if self.repository is not None:
                    self._repository_save((transitioned,))
                    self._repository_set_status(key, transitioned.status)
                continue
            items.append(transitioned)
        current_keys = set(grouped)
        for key, item in previous.items():
            if key in current_keys:
                continue
            if item.expires_at is not None and item.expires_at <= timestamp:
                if self.repository is not None:
                    self._repository_set_status(key, CognitiveAgendaStatus.ARCHIVED)
                continue
            absent_statuses = {
                source_absence_status[source]
                for source in item.sources
                if source in successful_sources and source in source_absence_status
            }
            if absent_statuses and all(
                source in successful_sources and source in source_absence_status
                for source in item.sources
            ):
                terminal = (
                    CognitiveAgendaStatus.CLOSED
                    if CognitiveAgendaStatus.CLOSED in absent_statuses
                    else CognitiveAgendaStatus.ARCHIVED
                )
                if self.repository is not None:
                    self._repository_set_status(key, terminal)
                continue
            transitioned = self._apply_context(item, facts)
            if transitioned.status in {
                CognitiveAgendaStatus.CLOSED,
                CognitiveAgendaStatus.ARCHIVED,
            }:
                if self.repository is not None:
                    self._repository_save((transitioned,))
                    self._repository_set_status(key, transitioned.status)
                continue
            items.append(transitioned)
        items.sort(key=lambda item: (-item.score, item.key))
        selected = tuple(
            self._detect_stall(item, timestamp)
            for item in items[: self.policy.capacity]
        )
        plan = self._build_deliberative_queue(selected, timestamp, facts)
        primary = plan[0].item if plan else None
        activation_rationale = (
            "agenda_activation:selected:"
            f"{primary.key}:score="
            f"{self._activation_score(primary, timestamp):.3f}"
            if primary is not None
            else "agenda_activation:none:no_eligible_items"
        )
        if primary is not None:
            selected = tuple(
                replace(
                    item,
                    commitment_status=CognitiveCommitmentStatus.PENDING,
                    last_transition="commitment_suspended",
                )
                if item.key != primary.key
                and item.commitment_status is CognitiveCommitmentStatus.IN_PROGRESS
                else item
                for item in selected
            )
            primary = next(item for item in selected if item.key == primary.key)
            activated = replace(
                primary,
                last_activated_at=timestamp,
                activation_count=primary.activation_count + 1,
            )
            activated = self._start_or_resume_commitment(activated, timestamp)
            selected = tuple(
                activated if item.key == activated.key else item for item in selected
            )
            primary = activated
        if primary is not None:
            primary = next(item for item in selected if item.key == primary.key)
        self._snapshot = CognitiveAgendaSnapshot(
            generated_at=timestamp,
            items=selected,
            primary_focus=selected[0] if selected else None,
            source_failures=tuple(failures),
            activated_focus=primary,
            activation_rationale=activation_rationale,
            activation_evaluated=True,
            deliberative_queue=tuple(
                replace(entry, item=primary)
                if primary is not None and entry.item.key == primary.key
                else entry
                for entry in plan
            ),
            planning_rationale=self._planning_rationale(plan),
            active_commitment=(
                primary
                if primary is not None
                and primary.commitment_status is CognitiveCommitmentStatus.IN_PROGRESS
                else None
            ),
            execution_rationale=self._execution_rationale(primary),
            metacognitive_review=(
                primary if primary is not None and primary.review_count else None
            ),
            metacognitive_rationale=self._metacognitive_rationale(primary),
            adaptive_learning=(
                primary
                if primary is not None and primary.learning_event_count
                else None
            ),
            adaptive_learning_rationale=(
                primary.learning_rationale if primary is not None else ""
            ),
        )
        if self.repository is not None:
            self._repository_save(selected)
        self._snapshot = self._with_operational_health(
            self._snapshot, source_failures=tuple(failures)
        )
        return self._snapshot

    def record_progress(
        self,
        key: str,
        progress: float,
        *,
        now: datetime | None = None,
        note: str = "",
    ) -> bool:
        if not 0.0 <= progress <= 1.0:
            raise ValueError("agenda commitment progress must be between 0 and 1")
        timestamp = now or datetime.now(timezone.utc)
        current = next((item for item in self._snapshot.items if item.key == key), None)
        if current is None or progress < current.progress:
            return False
        status = (
            CognitiveCommitmentStatus.COMPLETED
            if progress >= 1.0
            else CognitiveCommitmentStatus.IN_PROGRESS
        )
        progress_delta = progress - current.progress
        learned = self._learn_adjustments(
            current,
            priority_signal=progress_delta,
            cost_signal=-progress_delta,
            now=timestamp,
            reason="progress",
        )
        updated = replace(
            learned,
            progress=progress,
            last_progress_at=timestamp,
            commitment_started_at=current.commitment_started_at or timestamp,
            commitment_status=status,
            execution_note=note.strip(),
            last_transition=(
                "commitment_completed" if progress >= 1.0 else "commitment_progressed"
            ),
        )
        if progress >= 1.0:
            updated = replace(updated, status=CognitiveAgendaStatus.CLOSED)
            if self.repository is not None:
                self._repository_save((updated,))
                self._repository_set_status(key, CognitiveAgendaStatus.CLOSED)
            self._remove_from_snapshot(key)
            return True
        self._replace_item(updated, timestamp)
        return True

    def review_commitment(
        self,
        key: str,
        *,
        progress_quality: float,
        formulation_clarity: float,
        now: datetime | None = None,
        revised_expected_benefit: float | None = None,
        revised_cognitive_cost: float | None = None,
        note: str = "",
    ) -> bool:
        for name, value in (
            ("progress quality", progress_quality),
            ("formulation clarity", formulation_clarity),
        ):
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"agenda {name} must be between 0 and 1")
        for name, value in (
            ("expected benefit", revised_expected_benefit),
            ("cognitive cost", revised_cognitive_cost),
        ):
            if value is not None and not 0.0 <= value <= 1.0:
                raise ValueError(f"agenda revised {name} must be between 0 and 1")
        timestamp = now or datetime.now(timezone.utc)
        current = next((item for item in self._snapshot.items if item.key == key), None)
        if (
            current is None
            or current.commitment_status is CognitiveCommitmentStatus.COMPLETED
        ):
            return False
        if formulation_clarity < self.policy.formulation_clarity_threshold:
            review_status = CognitiveMetacognitiveStatus.REFORMULATE
            commitment_status = CognitiveCommitmentStatus.PENDING
            transition = "commitment_reformulation_required"
        elif (
            progress_quality < self.policy.progress_quality_threshold
            and current.stall_count
        ):
            review_status = CognitiveMetacognitiveStatus.DEFERRED
            commitment_status = CognitiveCommitmentStatus.STALLED
            transition = "commitment_deferred_by_review"
        else:
            review_status = CognitiveMetacognitiveStatus.SOUND
            commitment_status = current.commitment_status
            transition = "commitment_reviewed_sound"
        priority_signal = (progress_quality - 0.5) * 0.5
        cost_signal = (0.5 - progress_quality) + (0.5 - formulation_clarity)
        learned = self._learn_adjustments(
            current,
            priority_signal=priority_signal,
            cost_signal=cost_signal,
            now=timestamp,
            reason=f"review:{review_status.value}",
        )
        updated = replace(
            learned,
            metacognitive_status=review_status,
            progress_quality=progress_quality,
            formulation_clarity=formulation_clarity,
            review_count=current.review_count + 1,
            last_reviewed_at=timestamp,
            review_note=note.strip(),
            expected_benefit=(
                revised_expected_benefit
                if revised_expected_benefit is not None
                else current.expected_benefit
            ),
            cognitive_cost=(
                revised_cognitive_cost
                if revised_cognitive_cost is not None
                else current.cognitive_cost
            ),
            commitment_status=commitment_status,
            last_transition=transition,
        )
        self._replace_item(updated, timestamp)
        self._snapshot = replace(
            self._snapshot,
            metacognitive_review=updated,
            metacognitive_rationale=self._metacognitive_rationale(updated),
            adaptive_learning=(updated if updated.learning_event_count else None),
            adaptive_learning_rationale=updated.learning_rationale,
        )
        return True

    def _replace_item(self, updated: CognitiveAgendaItem, now: datetime) -> None:
        items = tuple(
            updated if item.key == updated.key else item
            for item in self._snapshot.items
        )
        plan = self._build_deliberative_queue(items, now, set())
        focus = plan[0].item if plan else None
        self._snapshot = replace(
            self._snapshot,
            generated_at=now,
            items=items,
            primary_focus=items[0] if items else None,
            activated_focus=focus,
            deliberative_queue=plan,
            planning_rationale=self._planning_rationale(plan),
            active_commitment=(
                updated
                if updated.commitment_status is CognitiveCommitmentStatus.IN_PROGRESS
                else None
            ),
            execution_rationale=self._execution_rationale(updated),
            metacognitive_review=(
                updated if updated.review_count else self._snapshot.metacognitive_review
            ),
            metacognitive_rationale=self._metacognitive_rationale(updated),
            adaptive_learning=(updated if updated.learning_event_count else None),
            adaptive_learning_rationale=updated.learning_rationale,
        )
        if self.repository is not None:
            self._repository_save(items)
        self._snapshot = self._with_operational_health(
            self._snapshot, source_failures=self._snapshot.source_failures
        )

    def _remove_from_snapshot(self, key: str) -> None:
        retained = tuple(item for item in self._snapshot.items if item.key != key)
        plan = tuple(
            entry
            for entry in self._snapshot.deliberative_queue
            if entry.item.key != key
        )
        self._snapshot = replace(
            self._snapshot,
            generated_at=datetime.now(timezone.utc),
            items=retained,
            primary_focus=retained[0] if retained else None,
            activated_focus=plan[0].item if plan else None,
            deliberative_queue=plan,
            planning_rationale=self._planning_rationale(plan),
            active_commitment=None,
            execution_rationale="agenda_execution:completed",
        )
        self._snapshot = self._with_operational_health(
            self._snapshot, source_failures=self._snapshot.source_failures
        )

    def close(self, key: str) -> bool:
        return self._remove_with_status(key, CognitiveAgendaStatus.CLOSED)

    def archive(self, key: str) -> bool:
        return self._remove_with_status(key, CognitiveAgendaStatus.ARCHIVED)

    def reopen(self, key: str) -> bool:
        if self.repository is None:
            return False
        return self._repository_set_status(key, CognitiveAgendaStatus.ACTIVE)

    def _remove_with_status(self, key: str, status: CognitiveAgendaStatus) -> bool:
        retained = tuple(item for item in self._snapshot.items if item.key != key)
        existed = len(retained) != len(self._snapshot.items)
        persisted = (
            self._repository_set_status(key, status)
            if self.repository is not None
            else False
        )
        if existed:
            self._snapshot = CognitiveAgendaSnapshot(
                generated_at=datetime.now(timezone.utc),
                items=retained,
                primary_focus=retained[0] if retained else None,
                source_failures=self._snapshot.source_failures,
                activated_focus=(
                    self._snapshot.activated_focus
                    if self._snapshot.activated_focus is not None
                    and self._snapshot.activated_focus.key != key
                    else None
                ),
                activation_rationale=(
                    "agenda_activation:none:no_eligible_items"
                    if not retained
                    else self._snapshot.activation_rationale
                ),
                activation_evaluated=self._snapshot.activation_evaluated,
                deliberative_queue=tuple(
                    entry
                    for entry in self._snapshot.deliberative_queue
                    if entry.item.key != key
                ),
                planning_rationale=self._snapshot.planning_rationale,
            )
            self._snapshot = self._with_operational_health(
                self._snapshot, source_failures=self._snapshot.source_failures
            )
        return existed or persisted

    def operational_report(self) -> CognitiveAgendaOperationalHealth:
        return self._with_operational_health(
            self._snapshot, source_failures=self._snapshot.source_failures
        ).operational_health or CognitiveAgendaOperationalHealth(
            CognitiveAgendaOperationalStatus.DEGRADED,
            invariant_violations=("operational_health_unavailable",),
        )

    def _repository_load_open(self) -> tuple[CognitiveAgendaItem, ...]:
        if self.repository is None:
            return ()
        try:
            return self.repository.load_open()
        except (RuntimeError, ValueError, TypeError, OSError, sqlite3.Error):
            self._repository_failures.append("load_open")
            return ()

    def _repository_save(self, items: tuple[CognitiveAgendaItem, ...]) -> bool:
        if self.repository is None:
            return False
        try:
            self.repository.save(items)
            return True
        except (RuntimeError, ValueError, TypeError, OSError, sqlite3.Error):
            self._repository_failures.append("save")
            return False

    def _repository_set_status(self, key: str, status: CognitiveAgendaStatus) -> bool:
        if self.repository is None:
            return False
        try:
            return self.repository.set_status(key, status)
        except (RuntimeError, ValueError, TypeError, OSError, sqlite3.Error):
            self._repository_failures.append("set_status")
            return False

    def _repository_status_for(self, key: str) -> CognitiveAgendaStatus | None:
        if self.repository is None:
            return None
        try:
            return self.repository.status_for(key)
        except (RuntimeError, ValueError, TypeError, OSError, sqlite3.Error):
            self._repository_failures.append("status_for")
            return None

    def _with_operational_health(
        self,
        snapshot: CognitiveAgendaSnapshot,
        *,
        source_failures: tuple[str, ...] = (),
    ) -> CognitiveAgendaSnapshot:
        violations: list[str] = []
        keys = [item.key for item in snapshot.items]
        if len(snapshot.items) > self.policy.capacity:
            violations.append("capacity_exceeded")
        if len(keys) != len(set(keys)):
            violations.append("duplicate_item_keys")
        if any(
            item.status
            in {CognitiveAgendaStatus.CLOSED, CognitiveAgendaStatus.ARCHIVED}
            for item in snapshot.items
        ):
            violations.append("terminal_item_in_open_snapshot")
        in_progress = [
            item
            for item in snapshot.items
            if item.commitment_status is CognitiveCommitmentStatus.IN_PROGRESS
        ]
        if len(in_progress) > 1:
            violations.append("multiple_commitments_in_progress")
        if (
            snapshot.activated_focus is not None
            and snapshot.activated_focus.key not in keys
        ):
            violations.append("activated_focus_not_in_snapshot")
        if (
            snapshot.active_commitment is not None
            and snapshot.active_commitment.key not in keys
        ):
            violations.append("active_commitment_not_in_snapshot")
        repository_failures = tuple(dict.fromkeys(self._repository_failures))
        source_failures = tuple(dict.fromkeys(source_failures))
        status = (
            CognitiveAgendaOperationalStatus.HEALTHY
            if not violations and not repository_failures and not source_failures
            else CognitiveAgendaOperationalStatus.DEGRADED
        )
        return replace(
            snapshot,
            operational_health=CognitiveAgendaOperationalHealth(
                status=status,
                invariant_violations=tuple(violations),
                repository_failures=repository_failures,
                source_failures=source_failures,
            ),
        )

    def _merge(
        self,
        key: str,
        signals: Sequence[CognitiveAgendaSignal],
        previous: CognitiveAgendaItem | None,
        now: datetime,
    ) -> CognitiveAgendaItem:
        lead = max(
            signals,
            key=lambda signal: (
                signal.priority,
                signal.urgency,
                signal.relevance,
                signal.source,
            ),
        )
        priority = max(signal.priority for signal in signals)
        urgency = max(signal.urgency for signal in signals)
        relevance = max(signal.relevance for signal in signals)
        score = (
            priority * self.policy.priority_weight
            + urgency * self.policy.urgency_weight
            + relevance * self.policy.relevance_weight
        )
        continuity_is_current = (
            previous is not None
            and now - previous.last_seen_at <= self.policy.continuity_window
        )
        if continuity_is_current:
            score += self.policy.continuity_bonus
        expirations = [signal.expires_at for signal in signals if signal.expires_at]
        observed = [signal.observed_at for signal in signals if signal.observed_at]
        return CognitiveAgendaItem(
            key=key,
            kind=lead.kind,
            title=lead.title,
            sources=tuple(sorted({signal.source for signal in signals})),
            score=round(score, 6),
            priority=priority,
            urgency=urgency,
            relevance=relevance,
            status=lead.status,
            first_seen_at=(
                previous.first_seen_at
                if previous is not None
                else min(observed, default=now)
            ),
            last_seen_at=max(observed, default=now),
            expires_at=min(expirations) if expirations else None,
            rationale=lead.rationale,
            resume_conditions=tuple(
                dict.fromkeys(
                    condition
                    for signal in signals
                    for condition in signal.resume_conditions
                    if condition.strip()
                )
            ),
            last_activated_at=(
                previous.last_activated_at if previous is not None else None
            ),
            activation_count=previous.activation_count if previous is not None else 0,
            resolution_conditions=tuple(
                dict.fromkeys(
                    condition
                    for signal in signals
                    for condition in signal.resolution_conditions
                    if condition.strip()
                )
            ),
            last_transition=previous.last_transition if previous is not None else "",
            expected_benefit=max(signal.expected_benefit for signal in signals),
            cognitive_cost=min(signal.cognitive_cost for signal in signals),
            dependencies=tuple(
                dict.fromkeys(
                    dependency
                    for signal in signals
                    for dependency in signal.dependencies
                    if dependency.strip()
                )
            ),
            context_tags=tuple(
                dict.fromkeys(
                    tag
                    for signal in signals
                    for tag in signal.context_tags
                    if tag.strip()
                )
            ),
            commitment_status=(
                previous.commitment_status
                if previous is not None
                else CognitiveCommitmentStatus.PENDING
            ),
            commitment_started_at=(
                previous.commitment_started_at if previous is not None else None
            ),
            progress=previous.progress if previous is not None else 0.0,
            last_progress_at=(
                previous.last_progress_at if previous is not None else None
            ),
            execution_note=previous.execution_note if previous is not None else "",
            stall_count=previous.stall_count if previous is not None else 0,
            metacognitive_status=(
                previous.metacognitive_status
                if previous is not None
                else CognitiveMetacognitiveStatus.UNREVIEWED
            ),
            progress_quality=previous.progress_quality if previous is not None else 1.0,
            formulation_clarity=previous.formulation_clarity
            if previous is not None
            else 1.0,
            review_count=previous.review_count if previous is not None else 0,
            last_reviewed_at=previous.last_reviewed_at
            if previous is not None
            else None,
            review_note=previous.review_note if previous is not None else "",
            adaptive_priority_adjustment=(
                previous.adaptive_priority_adjustment if previous is not None else 0.0
            ),
            adaptive_cost_adjustment=(
                previous.adaptive_cost_adjustment if previous is not None else 0.0
            ),
            learning_event_count=(
                previous.learning_event_count if previous is not None else 0
            ),
            last_learned_at=previous.last_learned_at if previous is not None else None,
            learning_rationale=(
                previous.learning_rationale if previous is not None else ""
            ),
        )

    def _select_activation(
        self,
        items: Sequence[CognitiveAgendaItem],
        now: datetime,
    ) -> tuple[CognitiveAgendaItem | None, str]:
        plan = self._build_deliberative_queue(items, now, set())
        if not plan:
            return None, "agenda_activation:none:no_eligible_items"
        return plan[0].item, plan[0].rationale

    def _build_deliberative_queue(
        self,
        items: Sequence[CognitiveAgendaItem],
        now: datetime,
        facts: set[str],
    ) -> tuple[CognitiveAgendaPlanEntry, ...]:
        remaining = [item for item in items if self._is_activation_eligible(item)]
        planned: list[CognitiveAgendaPlanEntry] = []
        active_tags: set[str] = set()
        while remaining:
            candidates = []
            for item in remaining:
                ready = self._dependencies_met(item, facts)
                if not ready:
                    continue
                tags = {self._normalize_condition(tag) for tag in item.context_tags}
                affinity = (
                    (len(tags & active_tags) / len(tags))
                    if tags and active_tags
                    else 0.0
                )
                utility = self._deliberative_utility(item, now, affinity)
                candidates.append((utility, item, affinity))
            if not candidates:
                break
            utility, selected, affinity = sorted(
                candidates, key=lambda row: (-row[0], row[1].key)
            )[0]
            rationale = (
                f"agenda_plan:selected:{selected.key}:utility={utility:.3f}:"
                f"benefit={selected.expected_benefit:.3f}:cost={selected.effective_cognitive_cost:.3f}:"
                f"affinity={affinity:.3f}"
            )
            planned.append(
                CognitiveAgendaPlanEntry(selected, utility, True, affinity, rationale)
            )
            active_tags.update(
                self._normalize_condition(tag) for tag in selected.context_tags
            )
            remaining.remove(selected)
        return tuple(planned)

    def _dependencies_met(self, item: CognitiveAgendaItem, facts: set[str]) -> bool:
        required = {
            self._normalize_condition(f"agenda:resolved:{dependency}")
            for dependency in item.dependencies
            if dependency.strip()
        }
        return not required or required.issubset(facts)

    def _deliberative_utility(
        self, item: CognitiveAgendaItem, now: datetime, affinity: float
    ) -> float:
        return round(
            self._activation_score(item, now)
            + item.adaptive_priority_adjustment * self.policy.priority_weight
            + item.expected_benefit * self.policy.benefit_weight
            - item.effective_cognitive_cost * self.policy.cost_weight
            + affinity * self.policy.context_affinity_bonus
            - (
                self.policy.stalled_utility_penalty
                if item.commitment_status is CognitiveCommitmentStatus.STALLED
                else 0.0
            )
            - (
                self.policy.reformulation_utility_penalty
                if item.metacognitive_status is CognitiveMetacognitiveStatus.REFORMULATE
                else 0.0
            ),
            6,
        )

    @staticmethod
    def _planning_rationale(plan: Sequence[CognitiveAgendaPlanEntry]) -> str:
        if not plan:
            return "agenda_plan:none:no_ready_items"
        return "agenda_plan:queue:" + ",".join(entry.item.key for entry in plan)

    def _is_activation_eligible(self, item: CognitiveAgendaItem) -> bool:
        if (
            item.commitment_status
            in {
                CognitiveCommitmentStatus.STALLED,
                CognitiveCommitmentStatus.COMPLETED,
            }
            or item.metacognitive_status is CognitiveMetacognitiveStatus.DEFERRED
        ):
            return False
        if item.status is CognitiveAgendaStatus.ACTIVE:
            return True
        return (
            item.status is CognitiveAgendaStatus.WATCHING
            and item.urgency >= self.policy.watching_activation_urgency
        )

    def _activation_score(self, item: CognitiveAgendaItem, now: datetime) -> float:
        score = item.score
        if item.last_activated_at is not None:
            since_activation = max(0.0, (now - item.last_activated_at).total_seconds())
            repetition_seconds = self.policy.repetition_window.total_seconds()
            if repetition_seconds > 0 and since_activation < repetition_seconds:
                score -= self.policy.repetition_penalty * (
                    1.0 - since_activation / repetition_seconds
                )
        reference = item.last_activated_at or item.first_seen_at
        waiting_seconds = max(0.0, (now - reference).total_seconds())
        aging_ratio = min(
            1.0,
            waiting_seconds / self.policy.aging_window.total_seconds(),
        )
        score += self.policy.aging_bonus * aging_ratio
        return round(score, 6)

    def _start_or_resume_commitment(
        self, item: CognitiveAgendaItem, now: datetime
    ) -> CognitiveAgendaItem:
        if item.commitment_status is CognitiveCommitmentStatus.COMPLETED:
            return item
        return replace(
            item,
            commitment_status=CognitiveCommitmentStatus.IN_PROGRESS,
            commitment_started_at=item.commitment_started_at or now,
            last_progress_at=item.last_progress_at or now,
            last_transition=(
                "commitment_resumed"
                if item.commitment_status is CognitiveCommitmentStatus.STALLED
                else item.last_transition or "commitment_started"
            ),
        )

    def _detect_stall(
        self, item: CognitiveAgendaItem, now: datetime
    ) -> CognitiveAgendaItem:
        if item.commitment_status is not CognitiveCommitmentStatus.IN_PROGRESS:
            return item
        reference = item.last_progress_at or item.commitment_started_at
        if reference is None or now - reference < self.policy.commitment_stall_window:
            return item
        learned = self._learn_adjustments(
            item,
            priority_signal=-1.0,
            cost_signal=1.0,
            now=now,
            reason="stall",
        )
        return replace(
            learned,
            commitment_status=CognitiveCommitmentStatus.STALLED,
            stall_count=item.stall_count + 1,
            last_transition="commitment_stalled",
        )

    @staticmethod
    def _execution_rationale(item: CognitiveAgendaItem | None) -> str:
        if item is None:
            return "agenda_execution:none:no_active_commitment"
        return (
            f"agenda_execution:{item.commitment_status.value}:{item.key}:"
            f"progress={item.progress:.3f}:stalls={item.stall_count}"
        )

    @staticmethod
    def _metacognitive_rationale(item: CognitiveAgendaItem | None) -> str:
        if item is None or not item.review_count:
            return "agenda_metacognition:none:not_reviewed"
        return (
            f"agenda_metacognition:{item.metacognitive_status.value}:{item.key}:"
            f"quality={item.progress_quality:.3f}:clarity={item.formulation_clarity:.3f}:"
            f"reviews={item.review_count}"
        )

    def reset_adaptation(self, key: str, *, now: datetime | None = None) -> bool:
        timestamp = now or datetime.now(timezone.utc)
        current = next((item for item in self._snapshot.items if item.key == key), None)
        if current is None:
            return False
        updated = replace(
            current,
            adaptive_priority_adjustment=0.0,
            adaptive_cost_adjustment=0.0,
            learning_event_count=0,
            last_learned_at=timestamp,
            learning_rationale="agenda_learning:reset",
            last_transition="adaptive_learning_reset",
        )
        self._replace_item(updated, timestamp)
        self._snapshot = replace(
            self._snapshot,
            adaptive_learning=updated,
            adaptive_learning_rationale=updated.learning_rationale,
        )
        return True

    def _learn_adjustments(
        self,
        item: CognitiveAgendaItem,
        *,
        priority_signal: float,
        cost_signal: float,
        now: datetime,
        reason: str,
    ) -> CognitiveAgendaItem:
        rate = self.policy.adaptive_learning_rate
        limit = self.policy.adaptive_adjustment_limit
        priority = max(
            -limit,
            min(limit, item.adaptive_priority_adjustment + priority_signal * rate),
        )
        cost = max(
            -limit,
            min(limit, item.adaptive_cost_adjustment + cost_signal * rate),
        )
        rationale = (
            f"agenda_learning:{reason}:{item.key}:"
            f"priority_adjustment={priority:.3f}:cost_adjustment={cost:.3f}"
        )
        return replace(
            item,
            adaptive_priority_adjustment=round(priority, 6),
            adaptive_cost_adjustment=round(cost, 6),
            learning_event_count=item.learning_event_count + 1,
            last_learned_at=now,
            learning_rationale=rationale,
        )

    @staticmethod
    def _normalize_condition(value: str) -> str:
        return " ".join(value.casefold().strip().split())

    def _conditions_met(self, conditions: Sequence[str], facts: set[str]) -> bool:
        normalized = {
            self._normalize_condition(condition)
            for condition in conditions
            if condition.strip()
        }
        return bool(normalized) and normalized.issubset(facts)

    def _apply_context(
        self, item: CognitiveAgendaItem, facts: set[str]
    ) -> CognitiveAgendaItem:
        if self._conditions_met(item.resolution_conditions, facts):
            return replace(
                item,
                status=CognitiveAgendaStatus.CLOSED,
                last_transition="resolved_by_context",
            )
        if item.status is CognitiveAgendaStatus.BLOCKED and self._conditions_met(
            item.resume_conditions, facts
        ):
            return replace(
                item,
                status=CognitiveAgendaStatus.ACTIVE,
                last_transition="resumed_by_context",
            )
        return item
__all__ = ("CognitiveAgendaKind", "CognitiveAgendaManager")

