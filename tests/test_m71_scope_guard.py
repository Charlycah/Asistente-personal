from pathlib import Path

import pytest

from core.cognitive_memory_integration import CognitiveMemoryIntegration
from core.cognitive_memory_store import CognitiveMemoryStore, CognitiveMemoryStoreConfig
from core.cognitive_pipeline import CognitivePipeline
from core.scope_guard import (
    ScopeDomain,
    ScopeGuardDecision,
    ScopeGuardManager,
    ScopeGuardPolicy,
    ScopeGuardSignal,
    ScopeGuardSnapshot,
    ScopeGuardStatus,
)


def test_scope_guard_policy_rejects_invalid_audit_limit():
    with pytest.raises(ValueError, match="audit"):
        ScopeGuardPolicy(max_audit_records=0)

    policy = ScopeGuardPolicy()

    assert ScopeDomain.BANKING in policy.normalized_forbidden_domains
    assert ScopeDomain.HOUSEHOLD_MEMORY in policy.normalized_allowed_domains


def test_scope_guard_policy_rejects_conflicting_domains():
    with pytest.raises(ValueError, match="forbidden"):
        ScopeGuardPolicy(
            forbidden_domains=(ScopeDomain.BANKING,),
            allowed_domains=(ScopeDomain.BANKING,),
        )


def test_scope_guard_decision_forbids_continuing_out_of_scope():
    with pytest.raises(ValueError, match="must not continue"):
        ScopeGuardDecision(
            ScopeGuardStatus.OUT_OF_SCOPE,
            (ScopeDomain.BANKING,),
            (),
            (),
            (ScopeDomain.BANKING,),
            "fuera de alcance",
            can_continue=True,
        )


def test_scope_guard_snapshot_exposes_contract_lines():
    decision = ScopeGuardDecision(
        ScopeGuardStatus.OUT_OF_SCOPE,
        (ScopeDomain.PURCHASE,),
        (),
        (),
        (ScopeDomain.PURCHASE,),
        "compras excluidas",
        can_continue=False,
    )
    snapshot = ScopeGuardSnapshot(
        (
            ScopeGuardSignal.SCOPE_GUARD_READY,
            ScopeGuardSignal.FORBIDDEN_DOMAIN_DETECTED,
        ),
        ScopeGuardStatus.OUT_OF_SCOPE,
        decision,
        ("audit:1",),
        ("ROBY no opera compras.",),
    )

    prompt = "\n".join(snapshot.system_prompt_lines())

    assert "Scope Guard M71:" in prompt
    assert "Dominio bloqueado: purchase" in prompt
    assert "ROBY no opera compras" in prompt


def test_manager_allows_household_memory_request():
    manager = ScopeGuardManager()

    snapshot = manager.observe_turn("ROBY, recordá la garantía del lavarropas")

    assert snapshot.normalized_status is ScopeGuardStatus.IN_SCOPE
    assert ScopeDomain.HOUSEHOLD_MEMORY in snapshot.decision.normalized_detected_domains
    assert snapshot.decision.blocked_domains == ()
    assert snapshot.decision.can_continue is True


def test_manager_blocks_banking_wallet_and_purchase_requests():
    manager = ScopeGuardManager()

    banking = manager.observe_turn("ROBY, hacé una transferencia bancaria")
    wallet = manager.observe_turn("ROBY, pagá con Mercado Pago")
    purchase = manager.observe_turn("ROBY, comprá este producto")

    assert banking.normalized_status is ScopeGuardStatus.OUT_OF_SCOPE
    assert ScopeDomain.BANKING in banking.decision.normalized_detected_domains
    assert wallet.normalized_status is ScopeGuardStatus.OUT_OF_SCOPE
    assert ScopeDomain.WALLET in wallet.decision.normalized_detected_domains
    assert purchase.normalized_status is ScopeGuardStatus.OUT_OF_SCOPE
    assert ScopeDomain.PURCHASE in purchase.decision.normalized_detected_domains


def test_manager_requires_review_for_medical_and_external_actions():
    manager = ScopeGuardManager()

    medical = manager.observe_turn("ROBY, decidí la dosis de esta medicación")
    external = manager.observe_turn("ROBY, enviá este mensaje por mí")

    assert medical.normalized_status is ScopeGuardStatus.REVIEW_REQUIRED
    assert medical.decision.human_approval_required is True
    assert ScopeDomain.MEDICAL_DECISION in medical.decision.review_required_domains
    assert external.normalized_status is ScopeGuardStatus.REVIEW_REQUIRED
    assert ScopeDomain.EXTERNAL_ACTION in external.decision.review_required_domains


def test_manager_applies_most_restrictive_policy_when_mixed_request():
    manager = ScopeGuardManager()

    snapshot = manager.observe_turn(
        "ROBY, anotá este trámite y después pagá la factura desde el banco"
    )

    assert snapshot.normalized_status is ScopeGuardStatus.OUT_OF_SCOPE
    assert ScopeDomain.HOUSEHOLD_MEMORY in snapshot.decision.allowed_domains
    assert ScopeDomain.BANKING in snapshot.decision.blocked_domains
    assert snapshot.decision.can_continue is False


def test_manager_keeps_bounded_audit_history():
    manager = ScopeGuardManager(ScopeGuardPolicy(max_audit_records=2))

    first = manager.observe_turn("ROBY, conversemos")
    second = manager.observe_turn("ROBY, recordá el turno")
    third = manager.observe_turn("ROBY, comprá algo")

    assert manager.history == (second, third)
    assert first not in manager.history
    assert manager.last_snapshot is third


def test_scope_guard_system_prompt_uses_last_snapshot():
    manager = ScopeGuardManager()
    manager.observe_turn("ROBY, pagá la factura")

    prompt = "\n".join(manager.system_prompt_lines())

    assert "Scope Guard M71:" in prompt
    assert "Dominio bloqueado" in prompt
    assert "bancos, billeteras, pagos ni compras" in prompt


def test_cognitive_pipeline_includes_m71_scope_guard(tmp_path: Path):
    store = CognitiveMemoryStore(
        CognitiveMemoryStoreConfig(db_path=tmp_path / "brain.sqlite")
    )
    scope_guard = ScopeGuardManager()
    pipeline = CognitivePipeline(
        CognitiveMemoryIntegration(store),
        scope_guard=scope_guard,
    )

    result = pipeline.process_turn(
        "ROBY, comprá este producto por internet",
        call_llm=False,
    )

    assert result.scope_guard is scope_guard
    assert scope_guard.last_snapshot is not None
    assert scope_guard.last_snapshot.normalized_status is ScopeGuardStatus.OUT_OF_SCOPE
    assert "Scope Guard M71:" in result.system_prompt
    assert "Dominio bloqueado: purchase" in result.system_prompt
