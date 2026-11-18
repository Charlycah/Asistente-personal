from dataclasses import FrozenInstanceError

import pytest

from app.cross_domain_execution_authorization import ExecutionAuthorizationRequest
from app.cross_domain_governed_source_capability_binding import (
    CrossDomainGovernedSourceCapabilityBinding,
    SourceCapabilityAssociation,
    SourceCapabilityBindingDecision,
    SourceCapabilityBindingResult,
)
from app.governed_information_sources import (
    GovernedInformationSource,
    GovernedInformationSources,
    InformationSourceKind,
    InformationSourceStatus,
)
from app.governed_source_query import GovernedSourceQueryContract
from app.personal_interest_center import InterestTopic
from app.runtime_capability_registry import OfficialRuntimeCapabilityRegistry


def setup_binding(
    *,
    source_status=InformationSourceStatus.DECLARED,
    associations=None,
):
    source = GovernedInformationSource(
        source_id="source.test",
        name="Test source",
        kind=InformationSourceKind.OFFICIAL,
        topics=frozenset({InterestTopic.SPACE_EXPLORATION}),
        status=source_status,
    )
    sources = GovernedSourceQueryContract(
        GovernedInformationSources((source,))
    )
    registry = OfficialRuntimeCapabilityRegistry()
    registry.register(
        name="capability.test",
        description="Test capability",
        interceptor=object(),
    )
    if associations is None:
        associations = (
            SourceCapabilityAssociation("source.test", "capability.test"),
        )
    binder = CrossDomainGovernedSourceCapabilityBinding(
        sources, registry, associations
    )
    request = ExecutionAuthorizationRequest(
        owner="owner",
        session_id="session",
        source_id="source.test",
        capability="capability.test",
        invocation_id="invocation",
    )
    return binder, request


def test_explicit_association_is_structurally_bound():
    binder, request = setup_binding()
    result = binder.evaluate(request)
    assert result.decision is SourceCapabilityBindingDecision.BOUND
    assert result.authorized is False


def test_missing_association_is_rejected():
    binder, request = setup_binding(associations=())
    result = binder.evaluate(request)
    assert result.decision is SourceCapabilityBindingDecision.REJECTED
    assert result.reason == "association_not_declared"


def test_unknown_source_is_unresolved():
    binder, request = setup_binding()
    request = ExecutionAuthorizationRequest(
        owner=request.owner,
        session_id=request.session_id,
        source_id="unknown",
        capability=request.capability,
        invocation_id=request.invocation_id,
    )
    assert (
        binder.evaluate(request).decision
        is SourceCapabilityBindingDecision.UNRESOLVED
    )


def test_disabled_source_is_rejected():
    binder, request = setup_binding(
        source_status=InformationSourceStatus.DISABLED
    )
    result = binder.evaluate(request)
    assert result.decision is SourceCapabilityBindingDecision.REJECTED
    assert result.reason == "source_disabled"


def test_unregistered_capability_is_unresolved():
    binder, request = setup_binding()
    request = ExecutionAuthorizationRequest(
        owner=request.owner,
        session_id=request.session_id,
        source_id=request.source_id,
        capability="missing",
        invocation_id=request.invocation_id,
    )
    assert (
        binder.evaluate(request).decision
        is SourceCapabilityBindingDecision.UNRESOLVED
    )


def test_wrong_capability_pair_is_rejected():
    binder, request = setup_binding(
        associations=(
            SourceCapabilityAssociation("source.test", "other.capability"),
        )
    )
    result = binder.evaluate(request)
    assert result.decision is SourceCapabilityBindingDecision.REJECTED


def test_invalid_request_is_rejected():
    binder, _ = setup_binding()
    result = binder.evaluate(object())
    assert result.decision is SourceCapabilityBindingDecision.REJECTED


@pytest.mark.parametrize(
    "source_id,capability",
    [
        ("", "capability.test"),
        ("source.test", ""),
        (" source.test", "capability.test"),
    ],
)
def test_invalid_association_is_rejected(source_id, capability):
    with pytest.raises(ValueError):
        SourceCapabilityAssociation(source_id, capability)


def test_authorized_result_cannot_be_forged():
    with pytest.raises(ValueError):
        SourceCapabilityBindingResult(
            SourceCapabilityBindingDecision.BOUND,
            "forged",
            authorized=True,
        )


def test_binding_result_is_immutable():
    result = SourceCapabilityBindingResult(
        SourceCapabilityBindingDecision.BOUND,
        "structural_only",
    )
    with pytest.raises(FrozenInstanceError):
        result.authorized = True


def test_binding_has_no_execution_methods():
    binder, _ = setup_binding()
    for name in ("execute", "grant", "authorize", "admit"):
        assert not hasattr(binder, name)
