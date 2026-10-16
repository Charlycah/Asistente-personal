from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app.governed_reasoning_runtime import (
    CanonicalProductiveReasoningSource,
    OfficialGovernedReasoningRuntimeGateway,
)
from core.cognitive_maturity.epistemic import EpistemicLevel
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
    build_governed_conversation_turn_identity,
)
from core.governed_reasoning.explicit_hypothesis_source import (
    ExplicitHypothesisSourceKind,
    GovernedExplicitHypothesisSource,
)
from core.persistent_world_model import (
    PersistentWorldDomain,
    PersistentWorldFact,
    PersistentWorldModelView,
)

NOW = datetime(2026, 8, 28, 15, 0, tzinfo=timezone.utc)
OWNER = "Carlos"
SESSION = "ordinary-multi-hypothesis"


def _world():
    return PersistentWorldModelView().build(
        (
            PersistentWorldFact(
                fact_id="fact-heating",
                domain=PersistentWorldDomain.HOUSEHOLD,
                fact_key="heating:state",
                value="on",
                source_authority="household_memory",
                source_reference="household-1",
                epistemic_level=EpistemicLevel.FACT,
                evidence_codes=("household:observed",),
                persisted_by_source=True,
                active=True,
            ),
        )
    )


def _scenario(number: int, *, value: str, proposition: str):
    return GovernedExplicitHypothesisSource(
        source_id=f"explicit-hypothesis-source-scenario-{number}",
        kind=ExplicitHypothesisSourceKind.SCENARIO,
        proposition=proposition,
        world_domain="household",
        fact_key="heating:state",
        assumed_value=value,
        temporal_scope="current",
        source_reference=f"ordinary-structured-source-{number}",
        source_fingerprint=f"{number:x}" * 64,
        evidence_codes=(f"source:ordinary:{number}",),
    )



def _causal(number: int, *, effect_key: str, proposition: str):
    return GovernedExplicitHypothesisSource(
        source_id=f"explicit-hypothesis-source-causal-{number}",
        kind=ExplicitHypothesisSourceKind.CAUSAL,
        proposition=proposition,
        cause_domain="household",
        cause_key="heating:state",
        cause_value="on",
        effect_domain="household",
        effect_key=effect_key,
        effect_value="high",
        temporal_scope="future",
        source_reference=f"ordinary-causal-source-{number}",
        source_fingerprint=f"{number + 8:x}" * 64,
        evidence_codes=(f"source:ordinary:causal:{number}",),
    )

def _bind(
    gateway: OfficialGovernedReasoningRuntimeGateway,
    source: GovernedExplicitHypothesisSource,
    minute: int,
    *,
    session_id: str = SESSION,
):
    now = NOW + timedelta(minutes=minute)
    text = f"Evaluar hipótesis explícita {minute}"
    request = GovernedConversationPipelineRequest(
        owner=OWNER,
        session_id=session_id,
        text=text,
    )
    turn_id = build_governed_conversation_turn_identity(request, now).turn_id
    episode = gateway.evaluate_productive_episode(
        owner=OWNER,
        session_id=session_id,
        text=text,
        now=now,
        turn_id=turn_id,
        scope_reference=session_id,
        observe_productive_intake=False,
    )
    gateway.bind_productive_epistemic_assessment(
        episode,
        source,
        world=_world(),
    )
    return turn_id, text, now


def test_two_distinct_ordinary_sources_form_explanatory_model() -> None:
    gateway = OfficialGovernedReasoningRuntimeGateway()
    first_turn, _, _ = _bind(
        gateway,
        _scenario(1, value="on", proposition="La calefacción está encendida."),
        0,
    )
    assert gateway.productive_explanatory_model_consumption(
        owner=OWNER,
        session_id=SESSION,
        turn_id=first_turn,
    ) is None

    second_turn, _, _ = _bind(
        gateway,
        _scenario(2, value="off", proposition="La calefacción está apagada."),
        1,
    )
    consumption = gateway.productive_explanatory_model_consumption(
        owner=OWNER,
        session_id=SESSION,
        turn_id=second_turn,
    )
    assert consumption is not None
    assert len(consumption.model.components) == 2
    assert consumption.model.canonical_authority == "governed_reasoning"


def test_linguistic_duplicate_does_not_fabricate_second_hypothesis() -> None:
    gateway = OfficialGovernedReasoningRuntimeGateway()
    source = _scenario(
        1,
        value="on",
        proposition="La calefacción está encendida.",
    )
    _bind(gateway, source, 0)
    duplicate = GovernedExplicitHypothesisSource(
        source_id="explicit-hypothesis-source-scenario-2",
        kind=source.kind,
        proposition=source.proposition,
        world_domain=source.world_domain,
        fact_key=source.fact_key,
        assumed_value=source.assumed_value,
        temporal_scope=source.temporal_scope,
        source_reference="another-reference",
        source_fingerprint="2" * 64,
        evidence_codes=("source:ordinary:2",),
    )
    turn_id, _, _ = _bind(gateway, duplicate, 1)
    assert gateway.productive_explanatory_model_consumption(
        owner=OWNER,
        session_id=SESSION,
        turn_id=turn_id,
    ) is None


def test_multi_hypothesis_history_is_session_isolated() -> None:
    gateway = OfficialGovernedReasoningRuntimeGateway()
    _bind(
        gateway,
        _scenario(1, value="on", proposition="La calefacción está encendida."),
        0,
    )
    turn_id, _, _ = _bind(
        gateway,
        _scenario(2, value="off", proposition="La calefacción está apagada."),
        1,
        session_id="other-session",
    )
    assert gateway.productive_explanatory_model_consumption(
        owner=OWNER,
        session_id="other-session",
        turn_id=turn_id,
    ) is None


def test_explanatory_model_reaches_same_turn_reasoning_source() -> None:
    gateway = OfficialGovernedReasoningRuntimeGateway()
    source_view = CanonicalProductiveReasoningSource(gateway)
    _bind(
        gateway,
        _scenario(1, value="on", proposition="La calefacción está encendida."),
        0,
    )
    turn_id, text, now = _bind(
        gateway,
        _scenario(2, value="off", proposition="La calefacción está apagada."),
        1,
    )
    lines = source_view.explanatory_model_context_lines(
        owner=OWNER,
        session_id=SESSION,
        text=text,
        now=now,
    )
    refs = source_view.reference_ids(
        owner=OWNER,
        session_id=SESSION,
        text=text,
        now=now,
    )
    consumption = gateway.productive_explanatory_model_consumption(
        owner=OWNER,
        session_id=SESSION,
        turn_id=turn_id,
    )
    assert consumption is not None
    assert "Modelo explicativo gobernado disponible" in lines[0]
    assert "no establece verdad ni causalidad" in lines[1]
    assert consumption.model.model_id in refs
    assert consumption.model.source_fingerprint in refs


def test_productive_model_preserves_non_authoritative_boundaries() -> None:
    gateway = OfficialGovernedReasoningRuntimeGateway()
    _bind(
        gateway,
        _scenario(1, value="on", proposition="La calefacción está encendida."),
        0,
    )
    turn_id, _, _ = _bind(
        gateway,
        _scenario(2, value="off", proposition="La calefacción está apagada."),
        1,
    )
    consumption = gateway.productive_explanatory_model_consumption(
        owner=OWNER,
        session_id=SESSION,
        turn_id=turn_id,
    )
    assert consumption is not None
    model = consumption.model
    assert model.read_only is True
    assert model.consultative is True
    assert model.persists_results is False
    assert model.creates_facts is False
    assert model.establishes_truth is False
    assert model.establishes_causality is False
    assert model.creates_learning is False
    assert model.modifies_memory is False
    assert model.modifies_world_model is False
    assert model.executes_transfer is False
    assert model.executes_actions is False
    assert model.grants_authority is False


def test_two_distinct_ordinary_causal_sources_also_form_model() -> None:
    gateway = OfficialGovernedReasoningRuntimeGateway()
    _bind(
        gateway,
        _causal(1, effect_key="humidity:state", proposition="Aumenta humedad."),
        0,
    )
    turn_id, _, _ = _bind(
        gateway,
        _causal(2, effect_key="energy:use", proposition="Aumenta consumo."),
        1,
    )
    consumption = gateway.productive_explanatory_model_consumption(
        owner=OWNER,
        session_id=SESSION,
        turn_id=turn_id,
    )
    assert consumption is not None
    assert len(consumption.model.components) == 2
