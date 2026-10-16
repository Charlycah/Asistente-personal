from datetime import date

import pytest

from core.cognitive_memory_integration import CognitiveMemoryIntegration
from core.cognitive_memory_store import CognitiveMemoryStore, CognitiveMemoryStoreConfig
from core.cognitive_pipeline import CognitivePipeline
from core.identity import HouseholdMember, ROBYIdentity, ROBYIdentityRegistry
from core.llm_provider import LLMRequest, LLMResponse
from core.llm_service import LLMService
from core.provider_router import ProviderRouter


class RecordingProvider:
    name = "test"

    def __init__(self) -> None:
        self.requests: list[LLMRequest] = []

    def generate(self, request: LLMRequest) -> LLMResponse:
        self.requests.append(request)
        return LLMResponse(text="respuesta con identidad", provider=self.name)


def test_roby_identity_describes_purpose_and_household_members():
    identity = ROBYIdentity()

    description = identity.describe()

    assert "Soy ROBY" in description
    assert "Carlos" in description
    assert "Cristina" in description
    assert "Acompañar" in description
    assert identity.member_names == ("Carlos", "Cristina")


def test_roby_identity_snapshot_is_deterministic_and_serializable():
    identity = ROBYIdentity(born_on=date(2026, 7, 8))

    snapshot = identity.to_dict()

    assert snapshot["name"] == "ROBY"
    assert snapshot["cognitive_phase"] == "FASE IV.1 - Identidad"
    assert snapshot["born_on"] == "2026-07-08"
    assert snapshot["family_name"] == "Hogar de Carlos y Cristina"
    assert snapshot["household_members"][0]["name"] == "Carlos"
    assert snapshot["household_members"][1]["name"] == "Cristina"
    assert "permanent_goals" in snapshot


def test_household_member_rejects_empty_required_fields():
    with pytest.raises(ValueError):
        HouseholdMember(name=" ", role="miembro", relationship="familia")

    with pytest.raises(ValueError):
        HouseholdMember(name="Cristina", role=" ", relationship="familia")

    with pytest.raises(ValueError):
        HouseholdMember(name="Cristina", role="miembro", relationship=" ")


def test_identity_registry_returns_default_roby_identity():
    registry = ROBYIdentityRegistry()

    assert registry.identity.name == "ROBY"
    assert registry.snapshot()["family_name"] == "Hogar de Carlos y Cristina"


def test_cognitive_pipeline_can_inject_identity_into_system_prompt(tmp_path):
    provider = RecordingProvider()
    store = CognitiveMemoryStore(
        CognitiveMemoryStoreConfig(db_path=tmp_path / "brain.sqlite")
    )
    identity = ROBYIdentity()
    pipeline = CognitivePipeline(
        CognitiveMemoryIntegration(store),
        llm_service=LLMService(ProviderRouter([provider])),
        identity=identity,
    )

    result = pipeline.process_turn("Explícame el propósito de ROBY")

    assert result.identity == identity
    assert "Identidad: eres ROBY" in result.system_prompt
    assert "Carlos" in result.system_prompt
    assert "Cristina" in result.system_prompt
    assert "Los modelos externos son herramientas" in result.system_prompt
    assert provider.requests[0].system_prompt == result.system_prompt
