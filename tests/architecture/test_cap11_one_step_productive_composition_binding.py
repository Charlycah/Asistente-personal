from __future__ import annotations

import inspect

from app import runtime_root_factory
from app.governed_cap11_one_step_continuation import (
    GovernedCAP11OneStepContinuationCoordinatorV1,
)
from app.productive_reasoning_local_library_bridge_invocation import (
    GovernedProductiveReasoningLibraryBridgeContributorV1,
)


def test_runtime_root_binds_one_source_neutral_cap11_continuation() -> None:
    source = inspect.getsource(runtime_root_factory)

    assert source.count("GovernedCAP11OneStepContinuationCoordinatorV1(") == 1
    assert "capability_registry=capability_registry.manager" in source
    assert "runtime_registry=capability_registry" in source
    assert "reasoning_gateway=governed_reasoning_runtime" in source
    assert (
        "productive_reasoning_library_contributor.bind_cap11_one_step_continuation("
    ) in source


def test_cap17_contributor_hands_off_without_owning_generic_cap11_stages() -> None:
    source = inspect.getsource(GovernedProductiveReasoningLibraryBridgeContributorV1)

    assert "GovernedMultiStepInvestigationPlanningReentryV1(" not in source
    assert "GovernedMultiStepInvestigationAuthorizationReentryV1(" not in source
    assert "GovernedMultiStepInvestigationExecutionReentryV1(" not in source
    assert "GovernedMultiStepInvestigationReasoningClosureV1(" not in source
    assert "_cap11_continuation_coordinator.consume(" in source


def test_coordinator_does_not_derive_or_recurse_next_requirement() -> None:
    source = inspect.getsource(GovernedCAP11OneStepContinuationCoordinatorV1.consume)

    assert "consume_local_reentry(" not in source
    assert "self._admission" not in source
    assert "recursive" not in source.casefold()
    assert source.count("self._planning.consume(") == 1
    assert source.count("self._authorization.consume(") == 1
    assert source.count("self._execution.consume(") == 1
    assert source.count("self._reasoning.consume(") == 1
