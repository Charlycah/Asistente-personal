from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE_INIT = ROOT / "core/governed_reasoning/__init__.py"


def test_cognitive_maturity_can_import_before_reasoning_quality_carrier() -> None:
    code = (
        "from core.cognitive_maturity.epistemic import EpistemicLevel; "
        "from core.governed_reasoning.derived_reasoning_quality_assessment "
        "import GovernedDerivedReasoningQualityContextAssessment; "
        "assert EpistemicLevel.HYPOTHESIS.value == 'hypothesis'; "
        "assert GovernedDerivedReasoningQualityContextAssessment.__name__ "
        "== 'GovernedDerivedReasoningQualityContextAssessment'"
    )
    completed = subprocess.run(
        [sys.executable, "-c", code],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr


def test_package_root_does_not_eagerly_import_reasoning_quality_carrier() -> None:
    source = PACKAGE_INIT.read_text(encoding="utf-8")
    assert "derived_reasoning_quality_assessment import" not in source
