from __future__ import annotations

import subprocess
import sys


def test_cognitive_maturity_can_import_before_derived_semantic_context() -> None:
    code = (
        "from core.cognitive_maturity.epistemic import EpistemicLevel; "
        "from core.governed_reasoning.context import ReasoningContextBundle; "
        "from core.governed_reasoning.derived_epistemic_assessment "
        "import GovernedDerivedEpistemicAssessment; "
        "assert EpistemicLevel.HYPOTHESIS.value == 'hypothesis'; "
        "assert ReasoningContextBundle.__name__ == 'ReasoningContextBundle'; "
        "assert GovernedDerivedEpistemicAssessment.__name__ "
        "== 'GovernedDerivedEpistemicAssessment'"
    )
    completed = subprocess.run(
        [sys.executable, "-c", code],
        cwd=".",
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
