from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime

from core.capability_registry import (
    CapabilityEffectClass,
    CapabilityInitiationPolicy,
    CapabilityInteractionScope,
    CapabilityKind,
    CapabilityRisk,
    PermissionScope,
)
from core.governed_image_repository import StoredImage
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
    GovernedOperationalInterception,
)

from .governed_visual_semantic_composition import (
    GovernedVisualSemanticComposition,
)
from .runtime_capability_registry import OfficialRuntimeCapabilityRegistry
from .vision_gateway import (
    GovernedVisionGateway,
    StoredImageAnalysisRequest,
    StoredImageAnalysisResult,
)

STORED_IMAGE_ACCESS_CAPABILITY = "vision.stored_images.read_analyze"


@dataclass(frozen=True)
class GovernedStoredImageRuntimeWiring:
    """Subordinate reachability seam for the existing governed vision boundary."""

    vision_gateway: GovernedVisionGateway
    interceptor: "GovernedStoredImageConversationInterceptionPort"


class GovernedStoredImageConversationInterceptionPort:
    """Expose explicit owner-scoped stored-image access through official registry."""

    _LIST_TRIGGERS = (
        "listar imágenes guardadas",
        "listar imagenes guardadas",
        "mostrar imágenes guardadas",
        "mostrar imagenes guardadas",
        "mis imágenes guardadas",
        "mis imagenes guardadas",
    )
    _ANALYZE_PREFIXES = (
        "analizar imagen guardada",
        "analizá imagen guardada",
        "analiza imagen guardada",
    )
    _CONSENT_MARKERS = (
        "autorizo",
        "doy consentimiento",
        "con mi consentimiento",
    )
    _IMAGE_ID_PATTERN = re.compile(r"\b[a-fA-F0-9]{32}\b")

    def __init__(
        self,
        vision_gateway: GovernedVisionGateway,
        *,
        semantic_composition: GovernedVisualSemanticComposition,
    ) -> None:
        self.vision_gateway = vision_gateway
        self.semantic_composition = semantic_composition

    def list_images(self, *, owner: str) -> tuple[StoredImage, ...]:
        """Return metadata-only records for the exact owner, without analysis."""

        return self.vision_gateway.list_stored_images(owner=owner)

    def analyze_image(
        self,
        *,
        owner: str,
        image_id: str,
        explicit_user_consent: bool,
    ) -> StoredImageAnalysisResult:
        """Analyze one exact selected id with fresh explicit consent."""

        selected_image_id = image_id.strip()
        if not selected_image_id:
            raise ValueError("stored-image id must not be blank")
        request = StoredImageAnalysisRequest(
            owner=owner,
            image_id=selected_image_id,
            explicit_user_consent=explicit_user_consent,
            user_requested=True,
        )
        return self.vision_gateway.analyze_stored_image(request)

    def analyze_image_for_cognitive_convergence(
        self,
        *,
        owner: str,
        image_id: str,
        explicit_user_consent: bool,
    ):
        """Project one consented stored image through existing visual semantics."""

        if not explicit_user_consent:
            raise PermissionError(
                "fresh explicit consent is required for stored-image convergence"
            )
        result = self.analyze_image(
            owner=owner,
            image_id=image_id,
            explicit_user_consent=True,
        )
        return self.semantic_composition.compose(
            owner=owner,
            observation=result.analysis.visual_observation,
            explicit_user_consent=True,
            object_detection=result.analysis.objects,
        )

    def intercept(self, request: GovernedConversationPipelineRequest, *, now: datetime):
        del now
        normalized = request.text.strip().casefold()
        if any(trigger in normalized for trigger in self._LIST_TRIGGERS):
            records = self.list_images(owner=request.owner)
            return GovernedOperationalInterception(
                response_text=self._format_listing(records),
                rationale="governed_stored_image_metadata_listing_completed",
            )
        if not any(prefix in normalized for prefix in self._ANALYZE_PREFIXES):
            return None
        match = self._IMAGE_ID_PATTERN.search(request.text)
        if match is None:
            return GovernedOperationalInterception(
                response_text=(
                    "Indicame el image_id exacto de la imagen guardada que "
                    "querés analizar."
                ),
                rationale="governed_stored_image_exact_id_required",
            )
        consent = any(marker in normalized for marker in self._CONSENT_MARKERS)
        if not consent:
            return GovernedOperationalInterception(
                response_text=(
                    "Necesito tu consentimiento explícito actual antes de analizar "
                    "esa imagen guardada."
                ),
                rationale="governed_stored_image_fresh_consent_required",
            )
        result = self.analyze_image(
            owner=request.owner,
            image_id=match.group(0),
            explicit_user_consent=True,
        )
        return GovernedOperationalInterception(
            response_text=(
                f"Análisis gobernado completado para image_id {result.image_id}. "
                f"Origen: {result.source_ref}."
            ),
            rationale="governed_stored_image_analysis_completed",
        )

    @staticmethod
    def _format_listing(records: tuple[StoredImage, ...]) -> str:
        if not records:
            return "No hay imágenes guardadas para este propietario."
        lines = ["Imágenes guardadas disponibles:"]
        for item in records:
            lines.append(
                f"- image_id={item.image_id} | etiqueta={item.label} | "
                f"tipo={item.mime_type} | sha256={item.sha256}"
            )
        return "\n".join(lines)


def build_governed_stored_image_runtime(
    *,
    vision_gateway: GovernedVisionGateway,
    capability_registry: OfficialRuntimeCapabilityRegistry,
    semantic_composition: GovernedVisualSemanticComposition,
) -> GovernedStoredImageRuntimeWiring:
    """Register one user-initiated read/analyze route over the existing gateway."""

    interceptor = GovernedStoredImageConversationInterceptionPort(
        vision_gateway,
        semantic_composition=semantic_composition,
    )
    capability_registry.register(
        name=STORED_IMAGE_ACCESS_CAPABILITY,
        description=(
            "Lista metadatos de imágenes guardadas y analiza una selección exacta "
            "sólo a petición explícita del usuario."
        ),
        interceptor=interceptor,
        kind=CapabilityKind.FILES,
        risk=CapabilityRisk.LOW,
        permission_scope=PermissionScope.READ,
        tags=("vision", "stored-images", "read-only", "explicit-selection"),
        semantic_triggers=(
            "listar imágenes guardadas",
            "listar imagenes guardadas",
            "analizar imagen guardada",
            "analiza imagen guardada",
        ),
        initiation_policy=CapabilityInitiationPolicy.HUMAN_APPROVAL,
        effect_class=CapabilityEffectClass.READ_ONLY,
        interaction_scope=CapabilityInteractionScope.HUMAN,
        requires_confirmation=False,
    )
    return GovernedStoredImageRuntimeWiring(
        vision_gateway=vision_gateway,
        interceptor=interceptor,
    )
