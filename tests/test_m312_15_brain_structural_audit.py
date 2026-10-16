from application.brain import BrainStructuralAudit


def test_m312_15_structural_audit_maps_expected_pipeline() -> None:
    report = BrainStructuralAudit().inspect()

    names = {item.name for item in report.components}
    assert report.component_count == 9
    assert "brain_service" in names
    assert "conversation_context_preparer" in names
    assert "conversation_context_diagnostic" in names


def test_m312_15_structural_audit_identifies_write_points() -> None:
    report = BrainStructuralAudit().inspect()

    assert report.write_points == (
        "BrainService.remember",
        "BrainService.update",
        "BrainService.forget",
        "BrainService.expire",
    )
    read_only = {item.name for item in report.components if item.read_only}
    assert "safe_personal_context" in read_only
    assert "conversation_context_preparer" in read_only


def test_m312_15_structural_audit_is_explicitly_not_runtime_connected() -> None:
    report = BrainStructuralAudit().inspect()

    assert report.runtime_connected is False
    assert report.to_dict()["summary"] == {
        "component_count": 9,
        "runtime_connected": False,
    }


def test_m312_15_structural_audit_is_stable_and_side_effect_free() -> None:
    audit = BrainStructuralAudit()

    assert audit.inspect() == audit.inspect()
