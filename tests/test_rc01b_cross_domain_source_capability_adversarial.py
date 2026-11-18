"""Adversarial characterization of non-authorizing source-capability binding."""

from dataclasses import replace

import pytest

from app.cross_domain_execution_authorization import ExecutionAuthorizationRequest
from app.cross_domain_governed_source_capability_binding import (
    CrossDomainGovernedSourceCapabilityBinding,
    SourceCapabilityAssociation,
    SourceCapabilityBindingDecision,
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


def make_fixture(associations):
    source = GovernedInformationSource(
        source_id="source.test",
        name="Test source",
        kind=InformationSourceKind.OFFICIAL,
        topics=frozenset({InterestTopic.SPACE_EXPLORATION}),
    )
    sources = GovernedInformationSources((source,))
    contract = GovernedSourceQueryContract(sources)
    registry = OfficialRuntimeCapabilityRegistry()
    registry.register(
        name="capability.test",
        description="Test capability",
        interceptor=object(),
    )
    binder = CrossDomainGovernedSourceCapabilityBinding(
        contract,
        registry,
        associations,
    )
    request = ExecutionAuthorizationRequest(
        owner="owner",
        session_id="session",
        source_id="source.test",
        capability="capability.test",
        invocation_id="invocation-1",
    )
    return sources, binder, request


def test_casefolded_source_association_is_recognized():
    _, binder, request = make_fixture(
        (SourceCapabilityAssociation("SOURCE.TEST", "capability.test"),)
    )
    result = binder.evaluate(request)
    assert result.decision is SourceCapabilityBindingDecision.BOUND
    assert result.authorized is False


def test_duplicate_associations_are_rejected():
    pair = SourceCapabilityAssociation("source.test", "capability.test")
    with pytest.raises(ValueError, match="duplicate source capability association"):
        make_fixture((pair, pair))


def test_unrelated_association_cannot_bind():
    _, binder, request = make_fixture(
        (SourceCapabilityAssociation("other.source", "capability.test"),)
    )
    result = binder.evaluate(request)
    assert result.decision is SourceCapabilityBindingDecision.REJECTED


def test_source_state_change_is_observed():
    sources, binder, request = make_fixture(
        (SourceCapabilityAssociation("source.test", "capability.test"),)
    )
    assert binder.evaluate(request).decision is SourceCapabilityBindingDecision.BOUND

    source = sources.source_for("source.test")
    sources._sources["source.test"] = replace(
        source,
        status=InformationSourceStatus.DISABLED,
    )

    result = binder.evaluate(request)
    assert result.decision is SourceCapabilityBindingDecision.REJECTED
    assert result.authorized is False


def test_identity_variations_do_not_create_execution_authority():
    _, binder, request = make_fixture(
        (SourceCapabilityAssociation("source.test", "capability.test"),)
    )
    variations = (
        replace(request, owner="other-owner"),
        replace(request, session_id="other-session"),
        replace(request, invocation_id="other-invocation"),
    )
    for variant in variations:
        result = binder.evaluate(variant)
        assert result.authorized is False


def test_repeated_evaluation_never_authorizes():
    _, binder, request = make_fixture(
        (SourceCapabilityAssociation("source.test", "capability.test"),)
    )
    first = binder.evaluate(request)
    second = binder.evaluate(request)
    assert first.authorized is False
    assert second.authorized is False
