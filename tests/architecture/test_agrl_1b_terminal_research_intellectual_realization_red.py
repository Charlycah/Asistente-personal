from __future__ import annotations

import inspect

import app.governed_reasoning_runtime as governed_reasoning_runtime


def test_agrl_1b_terminal_research_intellectual_realization_contract_red():
    """RED: terminal research closure is not yet a productive intellectual result.

    The missing surface must be a read-only projection/binding over existing
    authorities.  It must not become a new reasoning, planning, authorization,
    execution, memory, learning, or background-process authority.
    """
    projection_type = getattr(
        governed_reasoning_runtime,
        "CanonicalProductiveTerminalResearchIntellectualRealization",
        None,
    )
    projection_method = getattr(
        governed_reasoning_runtime.OfficialGovernedReasoningRuntimeGateway,
        "terminal_research_intellectual_realization",
        None,
    )

    assert projection_type is not None, (
        "AGRL-1B RED confirmed: the certified runtime has terminal investigation "
        "closure plus governed reasoning artifacts, but no canonical read-only "
        "terminal research intellectual realization projection."
    )
    assert callable(projection_method), (
        "AGRL-1B RED confirmed: the governed reasoning runtime does not expose "
        "terminal research intellectual realization productively."
    )

    fields = set(getattr(projection_type, "__dataclass_fields__", ()))
    required_lineage = {
        "episode_id",
        "originating_reasoning_id",
        "world_snapshot_id",
        "stopping_reason",
        "terminal_closure",
        "epistemic_assessment",
        "explanatory_model",
        "explanatory_model_revision",
        "rationale_codes",
    }
    assert required_lineage <= fields

    forbidden_authority_flags = {
        "reasons",
        "creates_requirement",
        "invokes_planning",
        "invokes_authorization",
        "invokes_execution",
        "modifies_memory",
        "creates_learning",
        "starts_background_process",
    }
    assert forbidden_authority_flags <= fields

    signature = inspect.signature(projection_method)
    assert "terminal_closure" in signature.parameters
