from __future__ import annotations

import inspect

from app.governed_intellectual_goal_proposal import GovernedIntellectualGoalProposal
from app.official_conversation_gateway import OfficialConversationGateway


def test_agrl_2c_requires_official_conversation_productive_goal_realization() -> None:
    method_name = "realize_governed_intellectual_goal_proposal"
    assert hasattr(OfficialConversationGateway, method_name), (
        "AGRL-2C RED confirmed: governed investigative goal proposals already exist "
        "and remain non-executive, but OfficialConversationGateway exposes no "
        "productive conversational realization for that existing proposal."
    )

    method = getattr(OfficialConversationGateway, method_name)
    signature = inspect.signature(method)
    assert "proposal" in signature.parameters
    annotation = signature.parameters["proposal"].annotation
    assert annotation in {
        GovernedIntellectualGoalProposal,
        "GovernedIntellectualGoalProposal",
    }
