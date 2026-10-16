from __future__ import annotations

import hashlib
import importlib
import importlib.util
import inspect
from dataclasses import replace
from pathlib import Path

import pytest

from app.positive_same_explanatory_model_continuity_consumer import (
    PositiveSameExplanatoryModelContinuitySelection,
)

ROOT = Path(__file__).resolve().parents[2]
PROJECTION_MODULE = (
    "app.positive_same_explanatory_model_continuity_context_projection"
)
PROTECTED_FILES = {
    "app/governed_reasoning_runtime.py": (
        "f8c96d92c08fff1b9219afd68974b79ba319f087b2fb32fbb20d5856aaa91f2f"
    ),
    "app/governed_explanatory_model_revision.py": (
        "d9d420442c72b588ea7d70000fed821b63b042cd1b83d5fb48f87649d09c92b4"
    ),
    "core/governed_reasoning/longitudinal_intellectual_identity.py": (
        "7f85f0dc41a2ef8bd4d7d09f3b3960b4d4f7d6dbb9844b4311d486d915b576ca"
    ),
}
DI19_CONTRIBUTOR_SHA256 = (
    "36fda61db9c05c1f18812b5c5902173d15b0a4cc76ae045e3af8abe1c5cde513"
)
DI20B_CONTRIBUTOR_SHA256 = (
    "243de22cab660943dbc144638f549468df3bafdae5e19f4387f055ff6fadc022"
)
CONTRIBUTOR_PATH = "core/reasoning_runtime_integration.py"


def _selection() -> PositiveSameExplanatoryModelContinuitySelection:
    return PositiveSameExplanatoryModelContinuitySelection(
        candidate_model_id="model-prior-a",
        assessment_id="assessment-same-a-b",
    )


def _projection_class():
    module = importlib.import_module(PROJECTION_MODULE)
    return module.PositiveSameExplanatoryModelContinuityContextProjectionV1


def test_cih_2di_19_residual_requires_explicit_continuity_context_projection() -> None:
    assert importlib.util.find_spec(PROJECTION_MODULE) is not None, (
        "CIH-2DI.19 RED: no consultative projection exists yet for the certified "
        "SAME continuity selection -> explanatory continuity-context consequence"
    )


@pytest.fixture(autouse=True)
def _require_projection_surface(request: pytest.FixtureRequest):
    if request.node.name == (
        "test_cih_2di_19_residual_requires_explicit_continuity_context_projection"
    ):
        return
    if importlib.util.find_spec(PROJECTION_MODULE) is None:
        pytest.skip(
            "CIH-2DI.19 RED residual projection surface is intentionally absent"
        )


def test_cih_2di_19_projects_only_certified_selection_with_exact_provenance() -> None:
    result = _projection_class()().project(selection=_selection())

    assert result is not None
    assert result.candidate_model_id == "model-prior-a"
    assert result.assessment_id == "assessment-same-a-b"
    assert result.projection_status == "consultative_continuity_context"
    assert result.context_lines()


def test_cih_2di_19_does_not_accept_arbitrary_model_id_as_authority() -> None:
    parameters = inspect.signature(_projection_class().project).parameters

    assert "selection" in parameters
    assert "model_id" not in parameters
    assert "candidate_model_id" not in parameters
    assert "assessment_id" not in parameters


def test_cih_2di_19_invalid_selection_fails_closed() -> None:
    projector = _projection_class()()
    invalid_status = replace(_selection(), selection_status="not_selected")
    revisional = replace(_selection(), authorizes_revision=True)
    persistent = replace(_selection(), persists=True)

    assert projector.project(selection=invalid_status) is None
    assert projector.project(selection=revisional) is None
    assert projector.project(selection=persistent) is None


def test_cih_2di_19_projection_is_consultative_only_and_non_authoritative() -> None:
    result = _projection_class()().project(selection=_selection())

    assert result is not None
    assert result.read_only is True
    assert result.consultative is True
    assert result.transient is True
    assert result.authorizes_revision is False
    assert result.persists is False
    assert result.creates_learning is False
    assert result.modifies_memory is False
    assert result.modifies_world_model is False
    assert result.opens_investigation is False
    assert result.creates_initiative is False
    assert result.authorizes_planning is False
    assert result.executes_actions is False
    assert result.grants_authority is False


def test_cih_2di_19_context_does_not_claim_truth_evidence_or_revision() -> None:
    result = _projection_class()().project(selection=_selection())

    assert result is not None
    rendered = " ".join(result.context_lines()).casefold()
    assert "continuous prior" in rendered
    assert "correct" not in rendered
    assert "confirmed" not in rendered
    assert "new evidence" not in rendered
    assert "should be revised" not in rendered
    assert "authorized" not in rendered


def test_cih_2di_19_projection_owns_no_revision_reentry_or_discovery() -> None:
    projector = _projection_class()()

    for attribute in (
        "revision_authority",
        "revision_registry",
        "reentry",
        "evidence_acquisition",
        "candidate_search",
        "candidate_discovery",
    ):
        assert not hasattr(projector, attribute)


def test_cih_2di_19_preserves_single_owner_and_protected_runtime_surfaces() -> None:
    for relative_path, certified_hash in PROTECTED_FILES.items():
        current_hash = hashlib.sha256((ROOT / relative_path).read_bytes()).hexdigest()
        assert current_hash == certified_hash

    # DI.19 certified the Contributor at DI19_CONTRIBUTOR_SHA256. DI.20B later
    # authorizes only its transient continuity transport/composition surface. Keep
    # the historical hash explicit while requiring the exact authorized successor.
    assert DI19_CONTRIBUTOR_SHA256 == (
        "36fda61db9c05c1f18812b5c5902173d15b0a4cc76ae045e3af8abe1c5cde513"
    )
    contributor_bytes = (ROOT / CONTRIBUTOR_PATH).read_bytes()
    contributor_hash = hashlib.sha256(contributor_bytes).hexdigest()
    assert contributor_hash == DI20B_CONTRIBUTOR_SHA256
