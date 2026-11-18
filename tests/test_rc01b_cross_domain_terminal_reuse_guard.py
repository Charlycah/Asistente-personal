"""Adversarial tests for non-authorizing terminal reuse control."""

from concurrent.futures import ThreadPoolExecutor
from dataclasses import FrozenInstanceError

import pytest

from app.cross_domain_governed_terminal_evidence import (
    GovernedTerminalExecutionEvidence,
    GovernedTerminalStatus,
)
from app.cross_domain_invocation_capture import (
    CrossDomainInvocationCapture,
    InvocationExecutionStatus,
)
from app.cross_domain_terminal_reuse_guard import (
    CrossDomainTerminalReuseGuard,
    TerminalReuseDecision,
    TerminalReuseResult,
)


def scenario(
    *,
    owner="owner",
    session="session",
    execution_id="a" * 64,
    source_id="governed-source",
    item_count=1,
    status=InvocationExecutionStatus.SUCCEEDED,
    observed=True,
):
    capture = CrossDomainInvocationCapture()
    invocation_id = capture.begin(
        owner=owner,
        session_id=session,
    )
    if observed:
        assert capture.observe(
            invocation_id,
            owner=owner,
            session_id=session,
            execution_id=execution_id,
            status=status,
        )

    snapshot = capture.snapshot(
        invocation_id,
        owner=owner,
        session_id=session,
    )
    evidence = GovernedTerminalExecutionEvidence(
        source_id=source_id,
        status=GovernedTerminalStatus(status.value),
        execution_id=execution_id,
        item_count=item_count,
        response_present=True,
    )
    return snapshot, evidence


def reserve(
    guard,
    pair,
    *,
    owner="owner",
    session="session",
):
    snapshot, evidence = pair
    return guard.reserve(
        snapshot=snapshot,
        evidence=evidence,
        owner=owner,
        session_id=session,
    ).decision


def test_first_valid_reservation():
    guard = CrossDomainTerminalReuseGuard()
    assert reserve(guard, scenario()) is TerminalReuseDecision.RESERVED


def test_identical_repetition_is_idempotent():
    guard = CrossDomainTerminalReuseGuard()
    pair = scenario()
    assert reserve(guard, pair) is TerminalReuseDecision.RESERVED
    assert reserve(guard, pair) is TerminalReuseDecision.IDEMPOTENT


def test_execution_reuse_between_invocations_is_conflict():
    guard = CrossDomainTerminalReuseGuard()
    first = scenario()
    second = scenario()
    assert first[0].invocation_id != second[0].invocation_id
    assert reserve(guard, first) is TerminalReuseDecision.RESERVED
    assert reserve(guard, second) is TerminalReuseDecision.CONFLICT


@pytest.mark.parametrize(
    "owner,session",
    (
        ("other", "session"),
        ("owner", "other"),
        ("other", "other"),
    ),
)
def test_cross_identity_execution_reuse_is_conflict(owner, session):
    guard = CrossDomainTerminalReuseGuard()
    first = scenario()
    second = scenario(owner=owner, session=session)
    assert reserve(guard, first) is TerminalReuseDecision.RESERVED
    assert reserve(
        guard, second, owner=owner, session=session
    ) is TerminalReuseDecision.CONFLICT


def test_same_invocation_different_execution_is_conflict():
    guard = CrossDomainTerminalReuseGuard()
    snapshot, evidence = scenario()
    assert reserve(
        guard, (snapshot, evidence)
    ) is TerminalReuseDecision.RESERVED

    # A forged snapshot can be structurally coherent.
    # The guard must still reject a contradictory reservation.
    from dataclasses import replace

    changed_snapshot = replace(
        snapshot, execution_id="b" * 64
    )
    changed_evidence = replace(
        evidence, execution_id="b" * 64
    )
    assert reserve(
        guard, (changed_snapshot, changed_evidence)
    ) is TerminalReuseDecision.CONFLICT


def test_same_execution_changed_source_is_conflict():
    from dataclasses import replace

    guard = CrossDomainTerminalReuseGuard()
    snapshot, evidence = scenario()
    assert reserve(
        guard, (snapshot, evidence)
    ) is TerminalReuseDecision.RESERVED

    changed = replace(evidence, source_id="other-source")
    assert reserve(
        guard, (snapshot, changed)
    ) is TerminalReuseDecision.CONFLICT


def test_same_execution_changed_item_count_is_conflict():
    from dataclasses import replace

    guard = CrossDomainTerminalReuseGuard()
    snapshot, evidence = scenario()
    assert reserve(
        guard, (snapshot, evidence)
    ) is TerminalReuseDecision.RESERVED

    changed = replace(evidence, item_count=2)
    assert reserve(
        guard, (snapshot, changed)
    ) is TerminalReuseDecision.CONFLICT


def test_unobserved_invocation_does_not_reserve():
    guard = CrossDomainTerminalReuseGuard()
    pending = scenario(observed=False)
    assert reserve(
        guard, pending
    ) is TerminalReuseDecision.UNRESOLVED

    assert reserve(
        guard, scenario()
    ) is TerminalReuseDecision.RESERVED


def test_failed_execution_does_not_reserve():
    guard = CrossDomainTerminalReuseGuard()
    failed = scenario(
        status=InvocationExecutionStatus.FAILED,
        item_count=0,
    )
    assert reserve(
        guard, failed
    ) is TerminalReuseDecision.UNRESOLVED

    assert reserve(
        guard, scenario()
    ) is TerminalReuseDecision.RESERVED


def test_empty_execution_does_not_reserve():
    guard = CrossDomainTerminalReuseGuard()
    empty = scenario(
        status=InvocationExecutionStatus.EMPTY,
        item_count=0,
    )
    assert reserve(
        guard, empty
    ) is TerminalReuseDecision.UNRESOLVED

    assert reserve(
        guard, scenario()
    ) is TerminalReuseDecision.RESERVED


def test_invalid_identity_is_rejected():
    guard = CrossDomainTerminalReuseGuard()
    pair = scenario()
    assert reserve(
        guard, pair, owner="other"
    ) is TerminalReuseDecision.REJECTED


@pytest.mark.parametrize(
    "invalid",
    (None, object(), {}, "forged"),
)
def test_invalid_snapshot_is_rejected(invalid):
    guard = CrossDomainTerminalReuseGuard()
    _, evidence = scenario()
    assert reserve(
        guard, (invalid, evidence)
    ) is TerminalReuseDecision.REJECTED


@pytest.mark.parametrize(
    "invalid",
    (None, object(), {}, "forged"),
)
def test_invalid_evidence_is_rejected(invalid):
    guard = CrossDomainTerminalReuseGuard()
    snapshot, _ = scenario()
    assert reserve(
        guard, (snapshot, invalid)
    ) is TerminalReuseDecision.REJECTED


def test_concurrent_identical_requests_are_atomic():
    guard = CrossDomainTerminalReuseGuard()
    pair = scenario()

    with ThreadPoolExecutor(max_workers=12) as executor:
        results = list(
            executor.map(
                lambda _: reserve(guard, pair),
                range(60),
            )
        )

    assert results.count(TerminalReuseDecision.RESERVED) == 1
    assert results.count(TerminalReuseDecision.IDEMPOTENT) == 59


def test_concurrent_conflicting_requests_have_one_winner():
    guard = CrossDomainTerminalReuseGuard()
    pairs = [scenario() for _ in range(40)]

    with ThreadPoolExecutor(max_workers=12) as executor:
        results = list(
            executor.map(
                lambda pair: reserve(guard, pair),
                pairs,
            )
        )

    assert results.count(TerminalReuseDecision.RESERVED) == 1
    assert results.count(TerminalReuseDecision.CONFLICT) == 39


def test_separate_registries_are_isolated():
    pair = scenario()
    first = CrossDomainTerminalReuseGuard()
    second = CrossDomainTerminalReuseGuard()

    assert reserve(first, pair) is TerminalReuseDecision.RESERVED
    assert reserve(second, pair) is TerminalReuseDecision.RESERVED


def test_result_is_immutable():
    result = TerminalReuseResult(TerminalReuseDecision.RESERVED)
    with pytest.raises(FrozenInstanceError):
        result.decision = TerminalReuseDecision.CONFLICT


def test_invalid_result_decision_is_rejected():
    with pytest.raises(ValueError):
        TerminalReuseResult("reserved")


def test_result_does_not_disclose_identity():
    guard = CrossDomainTerminalReuseGuard()
    pair = scenario()
    result = guard.reserve(
        snapshot=pair[0],
        evidence=pair[1],
        owner="owner",
        session_id="session",
    )
    assert not hasattr(result, "owner")
    assert not hasattr(result, "session_id")
    assert not hasattr(result, "execution_id")
    assert not hasattr(result, "invocation_id")


def test_guard_has_no_authorization_api():
    guard = CrossDomainTerminalReuseGuard()
    assert not hasattr(guard, "admit")
    assert not hasattr(guard, "register_provenance")
    assert not hasattr(guard, "authorize")
