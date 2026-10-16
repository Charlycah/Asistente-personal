from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from core.face_detection import FaceDetection
from core.object_detection import ObjectDetection
from core.person_detection import PersonDetection
from core.text_extraction import TextExtraction
from core.visual_code_detection import VisualCodeDetection


@dataclass(frozen=True)
class SceneFusion:
    """Descriptive fusion of existing visual capabilities for one frame."""

    summary: str
    confidence: float
    person_count: int = 0
    face_count: int = 0
    object_labels: tuple[str, ...] = ()
    text_region_count: int = 0
    code_types: tuple[str, ...] = ()
    analyzer_name: str = "deterministic_scene_analyzer"

    def __post_init__(self) -> None:
        summary = self.summary.strip()
        analyzer_name = self.analyzer_name.strip()
        if not summary:
            raise ValueError("scene summary must not be blank")
        if not analyzer_name:
            raise ValueError("scene analyzer name must not be blank")
        if not 0 <= self.confidence <= 1:
            raise ValueError("scene confidence must be between zero and one")
        if self.person_count < 0 or self.face_count < 0:
            raise ValueError("scene counts must not be negative")
        if self.text_region_count < 0:
            raise ValueError("scene text count must not be negative")
        labels = tuple(label.strip() for label in self.object_labels)
        code_types = tuple(code_type.strip().upper() for code_type in self.code_types)
        if any(not label for label in labels):
            raise ValueError("scene object labels must not be blank")
        if any(not code_type for code_type in code_types):
            raise ValueError("scene code types must not be blank")
        object.__setattr__(self, "summary", summary)
        object.__setattr__(self, "object_labels", labels)
        object.__setattr__(self, "code_types", code_types)
        object.__setattr__(self, "analyzer_name", analyzer_name)


class SceneAnalyzer(Protocol):
    def analyze(
        self,
        *,
        people: PersonDetection | None,
        faces: FaceDetection | None,
        objects: ObjectDetection | None,
        text: TextExtraction | None,
        codes: VisualCodeDetection | None,
    ) -> SceneFusion: ...


class DeterministicSceneAnalyzer:
    """Compose observations without inferring activities, identity or intent."""

    name = "deterministic_scene_analyzer"

    def analyze(
        self,
        *,
        people: PersonDetection | None,
        faces: FaceDetection | None,
        objects: ObjectDetection | None,
        text: TextExtraction | None,
        codes: VisualCodeDetection | None,
    ) -> SceneFusion:
        person_count = people.person_count if people else 0
        face_count = faces.face_count if faces else 0
        object_labels = (
            tuple(region.label for region in objects.regions) if objects else ()
        )
        text_count = len(text.regions) if text else 0
        code_types = (
            tuple(region.code_type for region in codes.regions) if codes else ()
        )
        confidences = [
            region.confidence
            for detection in (people, faces, objects, text, codes)
            if detection is not None
            for region in detection.regions
        ]
        confidence = sum(confidences) / len(confidences) if confidences else 1.0
        parts = [f"people={person_count}", f"faces={face_count}"]
        parts.append(f"objects={','.join(object_labels) if object_labels else 'none'}")
        parts.append(f"text_regions={text_count}")
        parts.append(f"code_types={','.join(code_types) if code_types else 'none'}")
        return SceneFusion(
            summary=";".join(parts),
            confidence=confidence,
            person_count=person_count,
            face_count=face_count,
            object_labels=object_labels,
            text_region_count=text_count,
            code_types=code_types,
            analyzer_name=self.name,
        )
