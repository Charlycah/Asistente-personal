from __future__ import annotations

from core.executive_event_model.models import (
    DeliveryRequirement,
    EventPriority,
    EventSource,
    GenericTextEvent,
    PrivacyLevel,
)


def text_to_executive_event(
    text: str,
    *,
    source: EventSource | str = EventSource.SYSTEM,
    priority: EventPriority | int = EventPriority.NORMAL,
    privacy_level: PrivacyLevel | str = PrivacyLevel.PERSONAL,
    delivery_requirement: DeliveryRequirement | str = (
        DeliveryRequirement.BEST_EFFORT
    ),
    entity_id: str | None = None,
    correlation_id: str | None = None,
    conversation_reference: str | None = None,
) -> GenericTextEvent:
    return GenericTextEvent(
        text=text,
        source=source,
        priority=priority,
        privacy_level=privacy_level,
        delivery_requirement=delivery_requirement,
        entity_id=entity_id,
        correlation_id=correlation_id,
        conversation_reference=conversation_reference,
    )
