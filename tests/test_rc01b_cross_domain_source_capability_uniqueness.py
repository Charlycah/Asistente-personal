"""Adversarial uniqueness checks for non-authorizing source-capability binding."""

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
)
from app.governed_source_query import GovernedSourceQueryContract
from app.personal_interest_center import InterestTopic
from app.runtime_capability_registry import OfficialRuntimeCapabilityRegistry


def make_binding(associations):
    source = GovernedInformationSource(
        source_id="source.test",
        name="Test source",
        kind=InformationSourceKind.OFFICIAL,
        topics=frozenset({InterestTopic.SPACE_EXPLORATION}),
    )
    contract = GovernedSourceQueryContract(
        GovernedInformationSources((source,))
    )
    registry = OfficialRuntimeCapabilityRegistry()
    for capability in ("capability.one", "capability.two"):
        registry.register(
            name=capability,
            description="Test capability",
            interceptor=object(),
        )
    return CrossDomainGovernedSourceCapabilityBinding(
        contract,
        registry,
        associations,
    )


def request_for(capability):
    return ExecutionAuthorizationRequest(
        owner="owner",
        session_id="session",
        source_id="source.test",
        capability=capability,
        invocation_id="invocation-1",
    )


def test_casefold_equivalent_duplicate_is_rejected():
    associations = (
        SourceCapabilityAssociation("source.test", "capability.one"),
        SourceCapabilityAssociation("SOURCE.TEST", "capability.one"),
    )
    with pytest.raises(
        ValueError,
        match="duplicate source capability association",
    ):
        make_binding(associations)


def test_multiple_distinct_capabilities_are_structurally_supported():
    associations = (
        SourceCapabilityAssociation("source.test", "capability.one"),
        SourceCapabilityAssociation("source.test", "capability.two"),
    )
    binding = make_binding(associations)

    for capability in ("capability.one", "capability.two"):
        result = binding.evaluate(request_for(capability))
        assert result.decision is SourceCapabilityBindingDecision.BOUND
        assert result.authorized is False


def test_capability_names_remain_case_sensitive():
    associations = (
        SourceCapabilityAssociation("source.test", "capability.one"),
        SourceCapabilityAssociation("source.test", "CAPABILITY.ONE"),
    )
    binding = make_binding(associations)

    result = binding.evaluate(request_for("capability.one"))
    assert result.decision is SourceCapabilityBindingDecision.BOUND
    assert result.authorized is False


def test_empty_associations_never_bind():
    binding = make_binding(())
    result = binding.evaluate(request_for("capability.one"))
    assert result.decision is SourceCapabilityBindingDecision.REJECTED
    assert result.authorized is False
