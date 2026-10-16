from __future__ import annotations

import ast
from pathlib import Path

import pytest

from core.explicit_deliberation_decision_option_adapter import (
    ExplicitDeliberationDecisionOptionAdapter,
)
from core.explicit_human_decision_deliberation import (
    ExplicitHumanDecisionDeliberationEvidenceProducer,
)
from core.explicit_organization_reference_acquisition import (
    ExplicitOrganizationReference,
    ExplicitOrganizationReferenceAcquirer,
    ExplicitOrganizationReferenceAcquisitionKind,
)

ROOT = Path(__file__).resolve().parents[2]


def _adaptation():
    evidence = ExplicitHumanDecisionDeliberationEvidenceProducer().analyze(
        "¿Proyecto ROBY o recordatorio de documentación?"
    )
    return ExplicitDeliberationDecisionOptionAdapter().adapt(evidence)


def test_acquisition_binds_ordinal_to_certified_option_identity() -> None:
    adaptation = _adaptation()
    result = ExplicitOrganizationReferenceAcquirer().acquire(
        adaptation,
        (
            ExplicitOrganizationReference(
                alternative_ordinal=1,
                organization_source_reference="reminder:r1",
            ),
            ExplicitOrganizationReference(
                alternative_ordinal=0,
                organization_item_id="project-1",
                acquisition_kind=(
                    ExplicitOrganizationReferenceAcquisitionKind.UI_STRUCTURED_REFERENCE
                ),
            ),
        ),
    )
    assert tuple(item.alternative_ordinal for item in result.references) == (0, 1)
    assert tuple(item.option_id for item in result.references) == tuple(
        item.option_id for item in adaptation.options
    )
    assert result.references[0].organization_item_id == "project-1"
    assert result.references[1].organization_source_reference == "reminder:r1"


def test_acquisition_is_deterministic_independent_of_input_order() -> None:
    adaptation = _adaptation()
    refs = (
        ExplicitOrganizationReference(0, organization_item_id="project-1"),
        ExplicitOrganizationReference(
            1, organization_source_reference="reminder:r1"
        ),
    )
    acquirer = ExplicitOrganizationReferenceAcquirer()
    first = acquirer.acquire(adaptation, refs)
    second = acquirer.acquire(adaptation, tuple(reversed(refs)))
    assert first == second


def test_partial_and_empty_acquisition_are_valid() -> None:
    adaptation = _adaptation()
    acquirer = ExplicitOrganizationReferenceAcquirer()
    empty = acquirer.acquire(adaptation)
    partial = acquirer.acquire(
        adaptation,
        (ExplicitOrganizationReference(0, organization_item_id="project-1"),),
    )
    assert empty.references == ()
    assert len(partial.references) == 1


@pytest.mark.parametrize(
    "reference",
    (
        pytest.param(
            ExplicitOrganizationReference,
            id="constructor-placeholder",
        ),
    ),
)
def test_reference_type_is_frozen_dataclass(reference) -> None:
    assert reference.__dataclass_params__.frozen is True


def test_reference_requires_exactly_one_identity() -> None:
    with pytest.raises(ValueError):
        ExplicitOrganizationReference(0)
    with pytest.raises(ValueError):
        ExplicitOrganizationReference(
            0,
            organization_item_id="project-1",
            organization_source_reference="project:project-1",
        )


def test_duplicate_and_unknown_ordinals_fail_closed() -> None:
    adaptation = _adaptation()
    acquirer = ExplicitOrganizationReferenceAcquirer()
    with pytest.raises(ValueError):
        acquirer.acquire(
            adaptation,
            (
                ExplicitOrganizationReference(0, organization_item_id="p1"),
                ExplicitOrganizationReference(0, organization_item_id="p2"),
            ),
        )
    with pytest.raises(ValueError):
        acquirer.acquire(
            adaptation,
            (ExplicitOrganizationReference(9, organization_item_id="p1"),),
        )


def test_acquisition_declares_governed_limits() -> None:
    result = ExplicitOrganizationReferenceAcquirer().acquire(_adaptation())
    assert result.read_only is True
    assert result.infers_identity is False
    assert result.queries_organization is False
    assert result.persists_results is False
    assert result.executes_actions is False
    assert result.grants_authority is False


def test_acquisition_has_no_organization_or_advisory_dependencies() -> None:
    path = ROOT / "core" / "explicit_organization_reference_acquisition.py"
    tree = ast.parse(path.read_text(encoding="utf-8"))
    imports = {
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module is not None
    }
    assert "core.intelligent_personal_organization" not in imports
    assert "core.productive_organization_evidence_projection" not in imports
    assert "core.governed_decision_advisory" not in imports
    assert not any("official_conversation_gateway" in item for item in imports)
