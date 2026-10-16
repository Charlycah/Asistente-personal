from __future__ import annotations

from pathlib import Path

from app.memory_consolidation import OfficialMemoryGateway
from app.productive_governed_learning_wiring import ProductiveGovernedLearningWiring
from core.learning_foundation import LearningDomain, LearningRole

ROOT = Path(__file__).resolve().parents[2]


def test_rp245_learning_store_is_retired_and_current_learning_boundary_preserved(
) -> None:
    assert not (ROOT / "core/unified_learning_base.py").exists()
    assert not (ROOT / "tests/test_rp245_unified_learning_base.py").exists()
    assert not (ROOT / "docs/RP_24_5_BASE_UNIFICADA_APRENDIZAJE.md").exists()
    assert (
        ROOT
        / "docs/history/legacy-learning/RP_24_5_BASE_UNIFICADA_APRENDIZAJE.md"
    ).exists()

    assert "records" not in {item.value for item in LearningDomain}
    assert "record" not in {item.value for item in LearningRole}
    assert OfficialMemoryGateway is not None
    assert ProductiveGovernedLearningWiring is not None

    foundation_source = (ROOT / "app/learning_foundation.py").read_text(
        encoding="utf-8"
    )
    assert "core.unified_learning_base" not in foundation_source
    assert "unified_learning_base" not in foundation_source
