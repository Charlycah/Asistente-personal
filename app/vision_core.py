from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from core.document_classification import (
    DeterministicDocumentClassifier,
    DocumentClassification,
    DocumentClassifier,
)
from core.document_extraction import (
    DeterministicStructuredDocumentExtractor,
    StructuredDocument,
    StructuredDocumentExtractor,
)
from core.document_intelligence import (
    DeterministicDocumentIntelligenceAnalyzer,
    DocumentIntelligence,
    DocumentIntelligenceAnalyzer,
)
from core.face_detection import FaceDetection, FaceDetector, FaceRegion
from core.intelligent_vision import (
    IntelligentVisionService,
    VisionCapability,
    VisionEvent,
    VisionObservation,
    VisionPrivacyLevel,
    VisionSnapshot,
)
from core.object_detection import ObjectDetection, ObjectDetector, ObjectRegion
from core.person_detection import PersonDetection, PersonDetector, PersonRegion
from core.scene_understanding import (
    DeterministicSceneAnalyzer,
    SceneAnalyzer,
    SceneFusion,
)
from core.text_extraction import TextExtraction, TextExtractor, TextRegion
from core.visual_code_detection import (
    CodeRegion,
    VisualCodeDecoder,
    VisualCodeDetection,
)
from core.visual_understanding_foundation import (
    VisualMediaType,
    VisualObservationSignal,
    VisualObservationSource,
    VisualPrivacyLevel,
)
from infrastructure.camera.camera_client import CameraFrame, CameraProvider


@dataclass(frozen=True)
class VisionCaptureRequest:
    """Explicit, governed request for one local-camera observation."""

    camera_index: int = 0
    capabilities: tuple[VisionCapability | str, ...] = (
        VisionCapability.SCENE_DESCRIPTION,
    )
    privacy_level: VisionPrivacyLevel | str = VisionPrivacyLevel.PERSONAL
    camera_permission: bool = False
    explicit_user_consent: bool = False
    user_requested: bool = True

    def __post_init__(self) -> None:
        capabilities = tuple(VisionCapability(item) for item in self.capabilities)
        privacy_level = VisionPrivacyLevel(self.privacy_level)
        if self.camera_index < 0:
            raise ValueError("vision camera index must not be negative")
        if not capabilities:
            raise ValueError("vision capture requires at least one capability")
        if len(capabilities) != len(set(capabilities)):
            raise ValueError("vision capture capabilities must be unique")
        object.__setattr__(self, "capabilities", capabilities)
        object.__setattr__(self, "privacy_level", privacy_level)


@dataclass(frozen=True)
class VisionCaptureResult:
    """Safe result: metadata and governance event, never raw image bytes."""

    frame_id: str
    camera_index: int
    mime_type: str
    width: int | None
    height: int | None
    size_bytes: int
    captured_at: datetime
    event: VisionEvent




@dataclass(frozen=True)
class StoredVisualInput:
    """Transient non-camera visual input selected from governed storage."""

    source_ref: str
    image_bytes: bytes
    mime_type: str
    observed_at: datetime
    explicit_user_consent: bool
    user_requested: bool

    def __post_init__(self) -> None:
        if not self.source_ref.strip():
            raise ValueError("stored visual source reference must not be blank")
        if not self.image_bytes:
            raise ValueError("stored visual input bytes must not be empty")
        if self.observed_at.tzinfo is None:
            raise ValueError("stored visual input timestamp must be timezone-aware")


@dataclass(frozen=True)
class StoredImageVisionResult:
    """Safe non-camera result; raw selected bytes are never returned."""

    source_ref: str
    mime_type: str
    size_bytes: int
    observed_at: datetime
    visual_observation: VisualObservationSignal
    perceptual_scene: SceneFusion
    people: PersonDetection | None
    faces: FaceDetection | None
    objects: ObjectDetection | None
    text: TextExtraction | None
    codes: VisualCodeDetection | None


@dataclass(frozen=True)
class VisionCoreSnapshot:
    capture_attempts: int
    frames_captured: int
    accepted_observations: int
    person_detection_attempts: int
    people_detected: int
    face_detection_attempts: int
    faces_detected: int
    text_extraction_attempts: int
    text_regions_extracted: int
    code_decoding_attempts: int
    codes_decoded: int
    object_detection_attempts: int
    objects_detected: int
    scene_analysis_attempts: int
    scenes_analyzed: int
    last_scene_summary: str | None
    document_classification_attempts: int
    documents_classified: int
    last_document_type: str | None
    document_extraction_attempts: int
    documents_extracted: int
    last_extracted_field_count: int
    document_intelligence_attempts: int
    documents_understood: int
    last_document_issue_count: int
    last_frame_id: str | None
    governance: VisionSnapshot


@dataclass(frozen=True)
class DocumentClassificationResult:
    """Governed document category based on transient visual evidence."""

    frame_id: str
    camera_index: int
    classification: DocumentClassification
    event: VisionEvent


@dataclass(frozen=True)
class StructuredDocumentExtractionResult:
    """Governed structured fields with traceable OCR evidence."""

    frame_id: str
    camera_index: int
    document: StructuredDocument
    classification: DocumentClassification
    event: VisionEvent


@dataclass(frozen=True)
class DocumentIntelligenceResult:
    """Governed explanation of document completeness and consistency."""

    frame_id: str
    camera_index: int
    intelligence: DocumentIntelligence
    document: StructuredDocument
    classification: DocumentClassification
    event: VisionEvent


@dataclass(frozen=True)
class PersonDetectionResult:
    """Governed result containing detection metadata and no source image."""

    frame_id: str
    camera_index: int
    person_present: bool
    person_count: int
    regions: tuple[PersonRegion, ...]
    detector_name: str
    event: VisionEvent

    def __post_init__(self) -> None:
        if self.person_count != len(self.regions):
            raise ValueError("person count must match detected regions")
        if self.person_present is not bool(self.regions):
            raise ValueError("person presence must match detected regions")


@dataclass(frozen=True)
class TextExtractionResult:
    """Governed OCR text; no source image or semantic document inference."""

    frame_id: str
    camera_index: int
    text_present: bool
    full_text: str
    regions: tuple[TextRegion, ...]
    extractor_name: str
    language: str
    event: VisionEvent

    def __post_init__(self) -> None:
        if self.text_present is not bool(self.regions):
            raise ValueError("OCR text presence must match extracted regions")
        expected = "\n".join(region.text for region in self.regions)
        if self.full_text != expected:
            raise ValueError("OCR full text must match extracted regions")


@dataclass(frozen=True)
class VisualCodeDetectionResult:
    """Governed decoded content; never raw media or automatic execution."""

    frame_id: str
    camera_index: int
    code_present: bool
    code_count: int
    regions: tuple[CodeRegion, ...]
    decoder_name: str
    event: VisionEvent

    def __post_init__(self) -> None:
        if self.code_count != len(self.regions):
            raise ValueError("decoded code count must match regions")
        if self.code_present is not bool(self.regions):
            raise ValueError("decoded code presence must match regions")


@dataclass(frozen=True)
class ObjectDetectionResult:
    """Governed object labels and regions; no source image or automatic action."""

    frame_id: str
    camera_index: int
    object_present: bool
    object_count: int
    regions: tuple[ObjectRegion, ...]
    detector_name: str
    event: VisionEvent

    def __post_init__(self) -> None:
        if self.object_count != len(self.regions):
            raise ValueError("object count must match detected regions")
        if self.object_present is not bool(self.regions):
            raise ValueError("object presence must match detected regions")



@dataclass(frozen=True)
class SceneUnderstandingResult:
    """Governed, descriptive fusion of visual signals from one frame."""

    frame_id: str
    camera_index: int
    scene: SceneFusion
    event: VisionEvent

@dataclass(frozen=True)
class FaceDetectionResult:
    """Governed face locations; no identity, biometric template or attributes."""

    frame_id: str
    camera_index: int
    face_present: bool
    face_count: int
    regions: tuple[FaceRegion, ...]
    detector_name: str
    event: VisionEvent

    def __post_init__(self) -> None:
        if self.face_count != len(self.regions):
            raise ValueError("face count must match detected regions")
        if self.face_present is not bool(self.regions):
            raise ValueError("face presence must match detected regions")


class OfficialVisionCore:
    """Canonical bridge for governed capture and local visual capabilities.

    Supports governed capture, non-biometric detection and local OCR while
    preserving authorization, governance and raw-media discard boundaries.
    """

    def __init__(
        self,
        *,
        camera_provider: CameraProvider,
        vision_service: IntelligentVisionService | None = None,
        person_detector: PersonDetector | None = None,
        face_detector: FaceDetector | None = None,
        text_extractor: TextExtractor | None = None,
        visual_code_decoder: VisualCodeDecoder | None = None,
        object_detector: ObjectDetector | None = None,
        scene_analyzer: SceneAnalyzer | None = None,
        document_classifier: DocumentClassifier | None = None,
        document_extractor: StructuredDocumentExtractor | None = None,
        document_intelligence_analyzer: DocumentIntelligenceAnalyzer | None = None,
    ) -> None:
        self.camera_provider = camera_provider
        self.vision_service = vision_service or IntelligentVisionService()
        self.person_detector = person_detector
        self.face_detector = face_detector
        self.text_extractor = text_extractor
        self.visual_code_decoder = visual_code_decoder
        self.object_detector = object_detector
        self.scene_analyzer = scene_analyzer or DeterministicSceneAnalyzer()
        self.document_classifier = (
            document_classifier or DeterministicDocumentClassifier()
        )
        self.document_extractor = (
            document_extractor or DeterministicStructuredDocumentExtractor()
        )
        self.document_intelligence_analyzer = (
            document_intelligence_analyzer
            or DeterministicDocumentIntelligenceAnalyzer()
        )
        self._capture_attempts = 0
        self._frames_captured = 0
        self._accepted_observations = 0
        self._person_detection_attempts = 0
        self._people_detected = 0
        self._face_detection_attempts = 0
        self._faces_detected = 0
        self._text_extraction_attempts = 0
        self._text_regions_extracted = 0
        self._code_decoding_attempts = 0
        self._codes_decoded = 0
        self._object_detection_attempts = 0
        self._objects_detected = 0
        self._scene_analysis_attempts = 0
        self._scenes_analyzed = 0
        self._last_scene_summary: str | None = None
        self._document_classification_attempts = 0
        self._documents_classified = 0
        self._last_document_type: str | None = None
        self._document_extraction_attempts = 0
        self._documents_extracted = 0
        self._last_extracted_field_count = 0
        self._document_intelligence_attempts = 0
        self._documents_understood = 0
        self._last_document_issue_count = 0
        self._last_frame_id: str | None = None

    @property
    def snapshot(self) -> VisionCoreSnapshot:
        return VisionCoreSnapshot(
            capture_attempts=self._capture_attempts,
            frames_captured=self._frames_captured,
            accepted_observations=self._accepted_observations,
            person_detection_attempts=self._person_detection_attempts,
            people_detected=self._people_detected,
            face_detection_attempts=self._face_detection_attempts,
            faces_detected=self._faces_detected,
            text_extraction_attempts=self._text_extraction_attempts,
            text_regions_extracted=self._text_regions_extracted,
            code_decoding_attempts=self._code_decoding_attempts,
            codes_decoded=self._codes_decoded,
            object_detection_attempts=self._object_detection_attempts,
            objects_detected=self._objects_detected,
            scene_analysis_attempts=self._scene_analysis_attempts,
            scenes_analyzed=self._scenes_analyzed,
            last_scene_summary=self._last_scene_summary,
            document_classification_attempts=(
                self._document_classification_attempts
            ),
            documents_classified=self._documents_classified,
            last_document_type=self._last_document_type,
            document_extraction_attempts=self._document_extraction_attempts,
            documents_extracted=self._documents_extracted,
            last_extracted_field_count=self._last_extracted_field_count,
            document_intelligence_attempts=self._document_intelligence_attempts,
            documents_understood=self._documents_understood,
            last_document_issue_count=self._last_document_issue_count,
            last_frame_id=self._last_frame_id,
            governance=self.vision_service.snapshot,
        )

    def analyze_stored_image(
        self,
        request: object,
        visual_input: StoredVisualInput,
    ) -> StoredImageVisionResult:
        """Accept one explicit stored-image input without camera semantics."""

        if not visual_input.explicit_user_consent:
            raise PermissionError("explicit vision consent is required")
        if not visual_input.user_requested:
            raise PermissionError("stored-image analysis must be explicitly requested")
        visual_observation = VisualObservationSignal(
            observation_ref=visual_input.source_ref,
            source=VisualObservationSource.IMAGE_FILE,
            media_type=VisualMediaType.PHOTO,
            privacy_level=VisualPrivacyLevel.PERSONAL,
            confidence=1.0,
            observed_at=visual_input.observed_at,
            externally_supplied=False,
        )
        frame = CameraFrame(
            camera_index=0,
            mime_type=visual_input.mime_type,
            image_bytes=visual_input.image_bytes,
            captured_at=visual_input.observed_at,
            frame_id=visual_input.source_ref,
        )
        people = self.person_detector.detect(frame) if self.person_detector else None
        faces = self.face_detector.detect(frame) if self.face_detector else None
        objects = self.object_detector.detect(frame) if self.object_detector else None
        text = self.text_extractor.extract(frame) if self.text_extractor else None
        codes = (
            self.visual_code_decoder.decode(frame)
            if self.visual_code_decoder
            else None
        )
        perceptual_scene = self.scene_analyzer.analyze(
            people=people,
            faces=faces,
            objects=objects,
            text=text,
            codes=codes,
        )
        return StoredImageVisionResult(
            source_ref=visual_input.source_ref,
            mime_type=visual_input.mime_type,
            size_bytes=len(visual_input.image_bytes),
            observed_at=visual_input.observed_at,
            visual_observation=visual_observation,
            perceptual_scene=perceptual_scene,
            people=people,
            faces=faces,
            objects=objects,
            text=text,
            codes=codes,
        )

    def capture(self, request: VisionCaptureRequest) -> VisionCaptureResult:
        self._capture_attempts += 1
        self._require_authorization(request)
        frame = self.camera_provider.capture(request.camera_index)
        self._frames_captured += 1
        self._last_frame_id = frame.frame_id
        event = self._govern(frame, request)
        if event.event_type.value == "accepted":
            self._accepted_observations += 1
        return VisionCaptureResult(
            frame_id=frame.frame_id,
            camera_index=frame.camera_index,
            mime_type=frame.mime_type,
            width=frame.width,
            height=frame.height,
            size_bytes=len(frame.image_bytes),
            captured_at=frame.captured_at,
            event=event,
        )

    def detect_people(self, request: VisionCaptureRequest) -> PersonDetectionResult:
        """Capture one authorized frame and detect people without identifying them."""

        if VisionCapability.OBJECT_DETECTION not in request.capabilities:
            raise ValueError("person detection requires object_detection capability")
        if self.person_detector is None:
            raise RuntimeError("person detector is not configured")
        self._person_detection_attempts += 1
        self._capture_attempts += 1
        self._require_authorization(request)
        frame = self.camera_provider.capture(request.camera_index)
        self._frames_captured += 1
        self._last_frame_id = frame.frame_id
        detection: PersonDetection = self.person_detector.detect(frame)
        event = self._govern_person_detection(frame, request, detection)
        if event.event_type.value == "accepted":
            self._accepted_observations += 1
        self._people_detected += detection.person_count
        return PersonDetectionResult(
            frame_id=frame.frame_id,
            camera_index=frame.camera_index,
            person_present=detection.person_present,
            person_count=detection.person_count,
            regions=detection.regions,
            detector_name=detection.detector_name,
            event=event,
        )

    def detect_faces(self, request: VisionCaptureRequest) -> FaceDetectionResult:
        """Locate faces in one authorized frame without recognizing anyone."""

        if VisionCapability.FACE_DETECTION not in request.capabilities:
            raise ValueError("face detection requires face_detection capability")
        if self.face_detector is None:
            raise RuntimeError("face detector is not configured")
        self._face_detection_attempts += 1
        self._capture_attempts += 1
        self._require_authorization(request)
        frame = self.camera_provider.capture(request.camera_index)
        self._frames_captured += 1
        self._last_frame_id = frame.frame_id
        detection: FaceDetection = self.face_detector.detect(frame)
        event = self._govern_face_detection(frame, request, detection)
        if event.event_type.value == "accepted":
            self._accepted_observations += 1
        self._faces_detected += detection.face_count
        return FaceDetectionResult(
            frame_id=frame.frame_id,
            camera_index=frame.camera_index,
            face_present=detection.face_present,
            face_count=detection.face_count,
            regions=detection.regions,
            detector_name=detection.detector_name,
            event=event,
        )

    def extract_text(self, request: VisionCaptureRequest) -> TextExtractionResult:
        """Extract visible text from one authorized frame using local OCR."""

        if VisionCapability.TEXT_EXTRACTION not in request.capabilities:
            raise ValueError("OCR requires text_extraction capability")
        if self.text_extractor is None:
            raise RuntimeError("text extractor is not configured")
        self._text_extraction_attempts += 1
        self._capture_attempts += 1
        self._require_authorization(request)
        frame = self.camera_provider.capture(request.camera_index)
        self._frames_captured += 1
        self._last_frame_id = frame.frame_id
        extraction: TextExtraction = self.text_extractor.extract(frame)
        event = self._govern_text_extraction(frame, request, extraction)
        if event.event_type.value == "accepted":
            self._accepted_observations += 1
        self._text_regions_extracted += len(extraction.regions)
        return TextExtractionResult(
            frame_id=frame.frame_id,
            camera_index=frame.camera_index,
            text_present=extraction.text_present,
            full_text=extraction.full_text,
            regions=extraction.regions,
            extractor_name=extraction.extractor_name,
            language=extraction.language,
            event=event,
        )


    def decode_visual_codes(
        self, request: VisionCaptureRequest
    ) -> VisualCodeDetectionResult:
        """Decode QR/barcodes from one authorized frame without acting on them."""

        if VisionCapability.CODE_DECODING not in request.capabilities:
            raise ValueError("QR/barcode decoding requires code_decoding capability")
        if self.visual_code_decoder is None:
            raise RuntimeError("visual code decoder is not configured")
        self._code_decoding_attempts += 1
        self._capture_attempts += 1
        self._require_authorization(request)
        frame = self.camera_provider.capture(request.camera_index)
        self._frames_captured += 1
        self._last_frame_id = frame.frame_id
        detection: VisualCodeDetection = self.visual_code_decoder.decode(frame)
        event = self._govern_visual_code_detection(frame, request, detection)
        if event.event_type.value == "accepted":
            self._accepted_observations += 1
        self._codes_decoded += len(detection.regions)
        return VisualCodeDetectionResult(
            frame_id=frame.frame_id,
            camera_index=frame.camera_index,
            code_present=detection.code_present,
            code_count=len(detection.regions),
            regions=detection.regions,
            decoder_name=detection.decoder_name,
            event=event,
        )

    def detect_objects(self, request: VisionCaptureRequest) -> ObjectDetectionResult:
        """Detect local object classes in one authorized frame without acting."""

        if VisionCapability.OBJECT_DETECTION not in request.capabilities:
            raise ValueError("object detection requires object_detection capability")
        if self.object_detector is None:
            raise RuntimeError("object detector is not configured")
        self._object_detection_attempts += 1
        self._capture_attempts += 1
        self._require_authorization(request)
        frame = self.camera_provider.capture(request.camera_index)
        self._frames_captured += 1
        self._last_frame_id = frame.frame_id
        detection: ObjectDetection = self.object_detector.detect(frame)
        event = self._govern_object_detection(frame, request, detection)
        if event.event_type.value == "accepted":
            self._accepted_observations += 1
        self._objects_detected += detection.object_count
        return ObjectDetectionResult(
            frame_id=frame.frame_id,
            camera_index=frame.camera_index,
            object_present=detection.object_present,
            object_count=detection.object_count,
            regions=detection.regions,
            detector_name=detection.detector_name,
            event=event,
        )

    def classify_document(
        self, request: VisionCaptureRequest
    ) -> DocumentClassificationResult:
        """Classify one authorized document without external enrichment."""

        if VisionCapability.DOCUMENT_UNDERSTANDING not in request.capabilities:
            raise ValueError(
                "document classification requires document_understanding capability"
            )
        if self.text_extractor is None:
            raise RuntimeError("document classification requires a text extractor")
        self._document_classification_attempts += 1
        self._capture_attempts += 1
        self._require_authorization(request)
        frame = self.camera_provider.capture(request.camera_index)
        self._frames_captured += 1
        self._last_frame_id = frame.frame_id
        text = self.text_extractor.extract(frame)
        objects = self.object_detector.detect(frame) if self.object_detector else None
        codes = (
            self.visual_code_decoder.decode(frame)
            if self.visual_code_decoder
            else None
        )
        classification = self.document_classifier.classify(
            text=text, objects=objects, codes=codes
        )
        event = self._govern_document_classification(
            frame, request, classification
        )
        if event.event_type.value == "accepted":
            self._accepted_observations += 1
        self._documents_classified += 1
        self._last_document_type = classification.primary.document_type.value
        return DocumentClassificationResult(
            frame_id=frame.frame_id,
            camera_index=frame.camera_index,
            classification=classification,
            event=event,
        )

    def extract_document_fields(
        self, request: VisionCaptureRequest
    ) -> StructuredDocumentExtractionResult:
        """Extract traceable fields from one authorized document frame."""

        if VisionCapability.DOCUMENT_UNDERSTANDING not in request.capabilities:
            raise ValueError(
                "structured extraction requires document_understanding capability"
            )
        if self.text_extractor is None:
            raise RuntimeError("structured extraction requires a text extractor")
        self._document_extraction_attempts += 1
        self._capture_attempts += 1
        self._require_authorization(request)
        frame = self.camera_provider.capture(request.camera_index)
        self._frames_captured += 1
        self._last_frame_id = frame.frame_id
        text = self.text_extractor.extract(frame)
        objects = self.object_detector.detect(frame) if self.object_detector else None
        codes = (
            self.visual_code_decoder.decode(frame)
            if self.visual_code_decoder
            else None
        )
        classification = self.document_classifier.classify(
            text=text, objects=objects, codes=codes
        )
        document = self.document_extractor.extract(
            text=text, classification=classification, codes=codes
        )
        event = self._govern_document_extraction(frame, request, document)
        if event.event_type.value == "accepted":
            self._accepted_observations += 1
        self._documents_extracted += 1
        self._last_extracted_field_count = len(document.fields)
        self._last_document_type = document.document_type
        return StructuredDocumentExtractionResult(
            frame_id=frame.frame_id,
            camera_index=frame.camera_index,
            document=document,
            classification=classification,
            event=event,
        )

    def understand_document(
        self, request: VisionCaptureRequest
    ) -> DocumentIntelligenceResult:
        """Explain one authorized document without external actions."""

        if VisionCapability.DOCUMENT_UNDERSTANDING not in request.capabilities:
            raise ValueError(
                "document intelligence requires document_understanding capability"
            )
        if self.text_extractor is None:
            raise RuntimeError("document intelligence requires a text extractor")
        self._document_intelligence_attempts += 1
        self._capture_attempts += 1
        self._require_authorization(request)
        frame = self.camera_provider.capture(request.camera_index)
        self._frames_captured += 1
        self._last_frame_id = frame.frame_id
        text = self.text_extractor.extract(frame)
        objects = self.object_detector.detect(frame) if self.object_detector else None
        codes = (
            self.visual_code_decoder.decode(frame)
            if self.visual_code_decoder
            else None
        )
        classification = self.document_classifier.classify(
            text=text, objects=objects, codes=codes
        )
        document = self.document_extractor.extract(
            text=text, classification=classification, codes=codes
        )
        intelligence = self.document_intelligence_analyzer.analyze(
            document=document, text=text, codes=codes
        )
        event = self._govern_document_intelligence(
            frame, request, intelligence
        )
        if event.event_type.value == "accepted":
            self._accepted_observations += 1
        self._documents_understood += 1
        self._last_document_issue_count = len(intelligence.issues)
        self._last_document_type = intelligence.document_type
        return DocumentIntelligenceResult(
            frame_id=frame.frame_id,
            camera_index=frame.camera_index,
            intelligence=intelligence,
            document=document,
            classification=classification,
            event=event,
        )

    def understand_scene(
        self, request: VisionCaptureRequest
    ) -> SceneUnderstandingResult:
        """Describe one authorized frame by fusing configured local analyzers."""

        if VisionCapability.SCENE_DESCRIPTION not in request.capabilities:
            raise ValueError(
                "scene understanding requires scene_description capability"
            )
        configured = (
            self.person_detector,
            self.face_detector,
            self.object_detector,
            self.text_extractor,
            self.visual_code_decoder,
        )
        if not any(item is not None for item in configured):
            raise RuntimeError(
                "scene understanding requires at least one visual analyzer"
            )
        self._scene_analysis_attempts += 1
        self._capture_attempts += 1
        self._require_authorization(request)
        frame = self.camera_provider.capture(request.camera_index)
        self._frames_captured += 1
        self._last_frame_id = frame.frame_id
        people = self.person_detector.detect(frame) if self.person_detector else None
        faces = self.face_detector.detect(frame) if self.face_detector else None
        objects = self.object_detector.detect(frame) if self.object_detector else None
        text = self.text_extractor.extract(frame) if self.text_extractor else None
        codes = (
            self.visual_code_decoder.decode(frame)
            if self.visual_code_decoder
            else None
        )
        scene = self.scene_analyzer.analyze(
            people=people,
            faces=faces,
            objects=objects,
            text=text,
            codes=codes,
        )
        event = self._govern_scene_understanding(frame, request, scene)
        if event.event_type.value == "accepted":
            self._accepted_observations += 1
        self._scenes_analyzed += 1
        self._last_scene_summary = scene.summary
        return SceneUnderstandingResult(
            frame_id=frame.frame_id,
            camera_index=frame.camera_index,
            scene=scene,
            event=event,
        )

    @staticmethod
    def _require_authorization(request: VisionCaptureRequest) -> None:
        if not request.camera_permission:
            raise PermissionError("vision camera permission is required")
        if not request.explicit_user_consent:
            raise PermissionError("explicit vision consent is required")
        if not request.user_requested:
            raise PermissionError("vision capture must be explicitly requested")

    def _govern(
        self,
        frame: CameraFrame,
        request: VisionCaptureRequest,
    ) -> VisionEvent:
        observation = VisionObservation(
            observation_ref=frame.frame_id,
            observed_at=frame.captured_at,
            privacy_level=request.privacy_level,
            requested_capabilities=request.capabilities,
            confidence=1.0,
            camera_permission=request.camera_permission,
            explicit_user_consent=request.explicit_user_consent,
            user_requested=request.user_requested,
            summary="",
            raw_media_present=False,
        )
        return self.vision_service.process(
            observation,
            now=datetime.now(timezone.utc),
        )

    def _govern_person_detection(
        self,
        frame: CameraFrame,
        request: VisionCaptureRequest,
        detection: PersonDetection,
    ) -> VisionEvent:
        confidence = (
            max(region.confidence for region in detection.regions)
            if detection.regions
            else 1.0
        )
        summary = (
            f"person_present={str(detection.person_present).lower()};"
            f"person_count={detection.person_count};"
            f"detector={detection.detector_name}"
        )
        observation = VisionObservation(
            observation_ref=frame.frame_id,
            observed_at=frame.captured_at,
            privacy_level=request.privacy_level,
            requested_capabilities=(VisionCapability.OBJECT_DETECTION,),
            confidence=confidence,
            camera_permission=request.camera_permission,
            explicit_user_consent=request.explicit_user_consent,
            user_requested=request.user_requested,
            summary=summary,
            raw_media_present=False,
        )
        return self.vision_service.process(
            observation,
            now=datetime.now(timezone.utc),
        )

    def _govern_face_detection(
        self,
        frame: CameraFrame,
        request: VisionCaptureRequest,
        detection: FaceDetection,
    ) -> VisionEvent:
        confidence = (
            max(region.confidence for region in detection.regions)
            if detection.regions
            else 1.0
        )
        summary = (
            f"face_present={str(detection.face_present).lower()};"
            f"face_count={detection.face_count};"
            f"detector={detection.detector_name}"
        )
        observation = VisionObservation(
            observation_ref=frame.frame_id,
            observed_at=frame.captured_at,
            privacy_level=request.privacy_level,
            requested_capabilities=(VisionCapability.FACE_DETECTION,),
            confidence=confidence,
            camera_permission=request.camera_permission,
            explicit_user_consent=request.explicit_user_consent,
            user_requested=request.user_requested,
            summary=summary,
            raw_media_present=False,
        )
        return self.vision_service.process(
            observation,
            now=datetime.now(timezone.utc),
        )
    def _govern_text_extraction(
        self,
        frame: CameraFrame,
        request: VisionCaptureRequest,
        extraction: TextExtraction,
    ) -> VisionEvent:
        confidence = (
            max(region.confidence for region in extraction.regions)
            if extraction.regions
            else 1.0
        )
        summary = (
            f"text_present={str(extraction.text_present).lower()};"
            f"text_regions={len(extraction.regions)};"
            f"language={extraction.language};"
            f"extractor={extraction.extractor_name}"
        )
        observation = VisionObservation(
            observation_ref=frame.frame_id,
            observed_at=frame.captured_at,
            privacy_level=request.privacy_level,
            requested_capabilities=(VisionCapability.TEXT_EXTRACTION,),
            confidence=confidence,
            camera_permission=request.camera_permission,
            explicit_user_consent=request.explicit_user_consent,
            user_requested=request.user_requested,
            summary=summary,
            raw_media_present=False,
        )
        return self.vision_service.process(
            observation,
            now=datetime.now(timezone.utc),
        )

    def _govern_object_detection(
        self,
        frame: CameraFrame,
        request: VisionCaptureRequest,
        detection: ObjectDetection,
    ) -> VisionEvent:
        confidence = (
            max(region.confidence for region in detection.regions)
            if detection.regions
            else 1.0
        )
        labels = ",".join(region.label for region in detection.regions)
        summary = (
            f"object_present={str(detection.object_present).lower()};"
            f"object_count={detection.object_count};"
            f"labels={labels};"
            f"detector={detection.detector_name}"
        )
        observation = VisionObservation(
            observation_ref=frame.frame_id,
            observed_at=frame.captured_at,
            privacy_level=request.privacy_level,
            requested_capabilities=(VisionCapability.OBJECT_DETECTION,),
            confidence=confidence,
            camera_permission=request.camera_permission,
            explicit_user_consent=request.explicit_user_consent,
            user_requested=request.user_requested,
            summary=summary,
            raw_media_present=False,
        )
        return self.vision_service.process(
            observation,
            now=datetime.now(timezone.utc),
        )

    def _govern_scene_understanding(
        self,
        frame: CameraFrame,
        request: VisionCaptureRequest,
        scene: SceneFusion,
    ) -> VisionEvent:
        observation = VisionObservation(
            observation_ref=frame.frame_id,
            observed_at=frame.captured_at,
            privacy_level=request.privacy_level,
            requested_capabilities=(VisionCapability.SCENE_DESCRIPTION,),
            confidence=scene.confidence,
            camera_permission=request.camera_permission,
            explicit_user_consent=request.explicit_user_consent,
            user_requested=request.user_requested,
            summary=scene.summary,
            raw_media_present=False,
        )
        return self.vision_service.process(
            observation,
            now=datetime.now(timezone.utc),
        )

    def _govern_document_classification(
        self,
        frame: CameraFrame,
        request: VisionCaptureRequest,
        classification: DocumentClassification,
    ) -> VisionEvent:
        primary = classification.primary
        signals = ",".join(primary.matched_signals) or "none"
        summary = (
            f"document_type={primary.document_type.value};"
            f"confidence={primary.confidence:.2f};"
            f"signals={signals};"
            f"classifier={classification.classifier_name}"
        )
        observation = VisionObservation(
            observation_ref=frame.frame_id,
            observed_at=frame.captured_at,
            privacy_level=request.privacy_level,
            requested_capabilities=(VisionCapability.DOCUMENT_UNDERSTANDING,),
            confidence=primary.confidence if primary.confidence > 0 else 1.0,
            camera_permission=request.camera_permission,
            explicit_user_consent=request.explicit_user_consent,
            user_requested=request.user_requested,
            summary=summary,
            raw_media_present=False,
        )
        return self.vision_service.process(
            observation,
            now=datetime.now(timezone.utc),
        )

    def _govern_document_intelligence(
        self,
        frame: CameraFrame,
        request: VisionCaptureRequest,
        intelligence: DocumentIntelligence,
    ) -> VisionEvent:
        summary = (
            f"document_type={intelligence.document_type};"
            f"completeness={intelligence.completeness:.3f};"
            f"consistency={intelligence.consistency:.3f};"
            f"issue_count={len(intelligence.issues)};"
            f"analyzer={intelligence.intelligence_name}"
        )
        observation = VisionObservation(
            observation_ref=frame.frame_id,
            observed_at=frame.captured_at,
            privacy_level=request.privacy_level,
            requested_capabilities=(VisionCapability.DOCUMENT_UNDERSTANDING,),
            confidence=min(intelligence.completeness, intelligence.consistency),
            camera_permission=request.camera_permission,
            explicit_user_consent=request.explicit_user_consent,
            user_requested=request.user_requested,
            summary=summary,
            raw_media_present=False,
        )
        return self.vision_service.process(
            observation, now=datetime.now(timezone.utc)
        )

    def _govern_document_extraction(
        self,
        frame: CameraFrame,
        request: VisionCaptureRequest,
        document: StructuredDocument,
    ) -> VisionEvent:
        names = ",".join(field.name for field in document.fields) or "none"
        confidence = (
            min(field.confidence for field in document.fields)
            if document.fields
            else 1.0
        )
        summary = (
            f"document_type={document.document_type};"
            f"field_count={len(document.fields)};"
            f"field_names={names};"
            f"extractor={document.extractor_name}"
        )
        observation = VisionObservation(
            observation_ref=frame.frame_id,
            observed_at=frame.captured_at,
            privacy_level=request.privacy_level,
            requested_capabilities=(VisionCapability.DOCUMENT_UNDERSTANDING,),
            confidence=confidence,
            camera_permission=request.camera_permission,
            explicit_user_consent=request.explicit_user_consent,
            user_requested=request.user_requested,
            summary=summary,
            raw_media_present=False,
        )
        return self.vision_service.process(
            observation,
            now=datetime.now(timezone.utc),
        )

    def _govern_visual_code_detection(
        self,
        frame: CameraFrame,
        request: VisionCaptureRequest,
        detection: VisualCodeDetection,
    ) -> VisionEvent:
        confidence = (
            max(region.confidence for region in detection.regions)
            if detection.regions
            else 1.0
        )
        code_types = ",".join(region.code_type for region in detection.regions)
        summary = (
            f"code_present={str(detection.code_present).lower()};"
            f"code_count={len(detection.regions)};"
            f"code_types={code_types};"
            f"decoder={detection.decoder_name}"
        )
        observation = VisionObservation(
            observation_ref=frame.frame_id,
            observed_at=frame.captured_at,
            privacy_level=request.privacy_level,
            requested_capabilities=(VisionCapability.CODE_DECODING,),
            confidence=confidence,
            camera_permission=request.camera_permission,
            explicit_user_consent=request.explicit_user_consent,
            user_requested=request.user_requested,
            summary=summary,
            raw_media_present=False,
        )
        return self.vision_service.process(
            observation,
            now=datetime.now(timezone.utc),
        )
