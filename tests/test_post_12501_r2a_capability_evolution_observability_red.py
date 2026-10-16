from app.runtime_compatibility import RUNTIME_COMPATIBILITY_REGISTRY
from app.unified_runtime_observability import UnifiedRuntimeObservability


def test_r2a_observability_projects_existing_capability_status_authorities(
    tmp_path,
    monkeypatch,
):
    """RED: observability must project existing status owners without replacing them."""
    monkeypatch.setenv("ROBY_RUNTIME_STATE_PATH", str(tmp_path / "runtime.json"))
    monkeypatch.setenv(
        "ROBY_RUNTIME_ROOT_FACTORY",
        "app.runtime_root_factory:build_runtime_root",
    )

    from app.official_runtime_composition import build_official_runtime_from_environment

    runtime = build_official_runtime_from_environment()
    service = UnifiedRuntimeObservability()

    registry = runtime.root.dependencies.official_capability_registry
    before_registry = registry.interface_snapshot()
    before_cognitive = runtime.conversation.cognitive_inventory.capabilities
    before_compatibility = RUNTIME_COMPATIBILITY_REGISTRY

    snapshot = service.snapshot(runtime)

    # R2A requires one read-only projection, not another registry and not a
    # synthetic lifecycle enum that destroys the semantics of existing owners.
    projection = snapshot.capability_evolution

    assert projection.operational == before_registry
    assert projection.cognitive == before_cognitive
    assert projection.compatibility == before_compatibility

    # Observability must remain non-authoritative: taking the snapshot cannot
    # mutate, register, enable, retire, or otherwise change any source owner.
    assert registry.interface_snapshot() == before_registry
    assert runtime.conversation.cognitive_inventory.capabilities == before_cognitive
    assert RUNTIME_COMPATIBILITY_REGISTRY == before_compatibility

    # Future roadmap items remain documentary/future; R2A must not manufacture
    # them as current runtime state.
    assert not hasattr(projection, "future")
