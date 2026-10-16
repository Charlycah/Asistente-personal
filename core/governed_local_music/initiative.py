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

LOCAL_MUSIC_CATALOGUE_READ_CAPABILITY = "music.local_catalogue.read"


def governed_local_music_catalogue_read_descriptor() -> CapabilityDescriptor:
    """Describe read-only access to one explicitly authorized local music root."""

    return CapabilityDescriptor(
        name=LOCAL_MUSIC_CATALOGUE_READ_CAPABILITY,
        description="Inspect the governed read-only local music catalogue.",
        kind=CapabilityKind.FILES,
        risk=CapabilityRisk.LOW,
        permission_scope=PermissionScope.READ,
        enabled=True,
        requires_confirmation=False,
        tags=("music", "local-collection", "catalogue", "read-only"),
        semantic_triggers=(
            "catálogo de música",
            "catalogo de musica",
            "mi música",
            "mi musica",
            "música local",
            "musica local",
        ),
        supported_intents=("local_music_catalogue_read",),
        example_utterances=("qué música tengo en mi colección",),
        evidence_outputs=("local_music_catalogue_metadata",),
        initiation_policy=CapabilityInitiationPolicy.HUMAN_APPROVAL,
        effect_class=CapabilityEffectClass.READ_ONLY,
        interaction_scope=CapabilityInteractionScope.INTERNAL,
        metadata={"authority": "governed_local_music_catalogue"},
    )

LOCAL_MUSIC_PLAYBACK_CAPABILITY = "music.local_playback.execute"


def governed_local_music_playback_descriptor() -> CapabilityDescriptor:
    """Describe explicit human-authorized playback on the local device."""

    return CapabilityDescriptor(
        name=LOCAL_MUSIC_PLAYBACK_CAPABILITY,
        description=(
            "Play one uniquely selected track from the governed local collection."
        ),
        kind=CapabilityKind.FILES,
        risk=CapabilityRisk.MEDIUM,
        permission_scope=PermissionScope.DEVICE,
        enabled=True,
        requires_confirmation=False,
        tags=("music", "local-collection", "playback", "device"),
        semantic_triggers=(
            "reproducí música",
            "reproduci musica",
            "reproducir música",
            "reproducir musica",
            "poné música",
            "pone musica",
        ),
        supported_intents=("local_music_playback",),
        example_utterances=("reproducí música Love of My Life",),
        evidence_outputs=("local_music_playback_started",),
        initiation_policy=CapabilityInitiationPolicy.HUMAN_APPROVAL,
        effect_class=CapabilityEffectClass.STATE_CHANGING,
        interaction_scope=CapabilityInteractionScope.DEVICE,
        metadata={"authority": "governed_local_music_playback"},
    )

