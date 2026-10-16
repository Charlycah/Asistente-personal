from __future__ import annotations

import pytest

from core.governed_operational_conversation_pipeline.models import (
    ExplicitLongitudinalTopicDeclaration,
    GovernedConversationPipelineRequest,
)


def test_cih_2bx_governed_conversation_request_exposes_typed_explicit_topic_carrier(
) -> None:
    fields = GovernedConversationPipelineRequest.__dataclass_fields__

    assert "explicit_longitudinal_topic_declaration" in fields

    declaration = ExplicitLongitudinalTopicDeclaration(topic_key="ROBY architecture")
    request = GovernedConversationPipelineRequest(
        owner="owner-1",
        session_id="session-1",
        text="Continue.",
        explicit_longitudinal_topic_declaration=declaration,
    )

    assert request.explicit_longitudinal_topic_declaration is declaration
    assert declaration.topic_key == "ROBY architecture"

    with pytest.raises(ValueError, match="must not be blank"):
        ExplicitLongitudinalTopicDeclaration(topic_key="   ")

    with pytest.raises(ValueError, match="already be canonical"):
        ExplicitLongitudinalTopicDeclaration(topic_key="ROBY  architecture")

    without_declaration = GovernedConversationPipelineRequest(
        owner="owner-1",
        session_id="session-2",
        text="Ordinary turn.",
    )
    assert without_declaration.explicit_longitudinal_topic_declaration is None
