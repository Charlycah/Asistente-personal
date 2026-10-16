from __future__ import annotations

from core.capability_registry import (
    CapabilityDescriptor,
    CapabilityEffectClass,
    CapabilityInitiationPolicy,
    CapabilityInteractionScope,
    CapabilityKind,
    CapabilityRisk,
    PermissionScope,
)

LOCAL_LIBRARY_READ_CAPABILITY = "knowledge.local_library.read"


def governed_local_library_read_descriptor() -> CapabilityDescriptor:
    """Describe governed read-only access to the authorized local library."""

    return CapabilityDescriptor(
        name=LOCAL_LIBRARY_READ_CAPABILITY,
        description="Read selected material from the governed local personal library.",
        kind=CapabilityKind.FILES,
        risk=CapabilityRisk.LOW,
        permission_scope=PermissionScope.READ,
        enabled=True,
        requires_confirmation=False,
        tags=("knowledge", "local-library", "read-only"),
        semantic_triggers=("biblioteca", "mis libros", "biblioteca personal"),
        supported_intents=("local_library_read",),
        example_utterances=("consultar la biblioteca personal",),
        evidence_outputs=("local_document_content",),
        initiation_policy=CapabilityInitiationPolicy.GOVERNED_AUTONOMOUS,
        effect_class=CapabilityEffectClass.READ_ONLY,
        interaction_scope=CapabilityInteractionScope.INTERNAL,
        metadata={"authority": "governed_local_library"},
    )
