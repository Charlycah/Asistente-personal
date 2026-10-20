from __future__ import annotations

import mimetypes
import os
import re
import subprocess
import time
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from queue import Empty, SimpleQueue
from threading import Event, Thread
from typing import Protocol

from app.advanced_clinical_safety import AdvancedClinicalSafetyService
from app.allergy_registry import AllergyRegistryService
from app.audio_engine import AudioEngineEvent, AudioEngineState
from app.chronic_condition_registry import ChronicConditionRegistryService
from app.conversational_health_guidance import (
    ConversationalHealthGuidanceService,
)
from app.conversational_translation import ConversationalTranslation
from app.desktop_governed_image_preview_coordinator import (
    GovernedImagePreviewCoordinator,
)
from app.desktop_governed_image_preview_fetch_adapter import (
    fetch_desktop_governed_preview,
)
from app.desktop_governed_floating_image_viewer import (
    DesktopGovernedFloatingImageViewer,
)
from app.desktop_governed_floating_viewer_integration import (
    connect_governed_floating_viewer,
)
from app.desktop_visual_companion_runtime_binding import (
    bind_applied_result_to_desktop,
    dispatch_desktop_runtime_visual_render,
)
from app.device_architecture import DeviceArchitectureService
from app.document_reading import DocumentReadingService
from app.emergency_contacts import EmergencyContactService
from app.health_checkup_import import AssistedHealthCheckupImportService
from app.health_orchestrator import HealthOrchestratorService
from app.health_orientation import HealthOrientationService
from app.health_result_comparison import HistoricalHealthComparisonService
from app.healthcare_directory import HealthcareDirectoryService
from app.intelligent_dictation import DictationAction, IntelligentDictationSession
from app.intelligent_task_agent import IntelligentTaskAgent
from app.m341_stage_closure import M341StageClosureService
from app.medical_consultation_preparation import (
    MedicalConsultationPreparationService,
)
from app.medical_pdf_export import MedicalPdfExportService
from app.runtime_capability_registry import RuntimeCapabilityView
from app.secure_health_checkups import SecureHealthCheckupService
from app.secure_medication_registry import SecureMedicationRegistryService
from app.structured_symptom_registry import StructuredSymptomService
from app.ui_adapter import UIResponse
from app.vital_sign_history import VitalSignHistoryService
from app.voice_input import NullVoiceInput, VoiceInput, VoiceRequestTranscriber
from app.voice_output import NullVoiceOutput, VoiceOutput, VoiceResponseReader
from app.voice_session_gate import VoiceSessionGate
from core.application_lifecycle import (
    ApplicationLifecycleManager,
    LifecycleExitReason,
)
from core.executive_presence_attention import AttentionState
from core.governed_image_repository import ImageStoreRequest


class VoiceMonitorState(str, Enum):
    INACTIVE = "inactive"
    STARTING = "starting"
    SILENCE = "silence"
    VOICE = "voice"
    PROCESSING = "processing"
    ERROR = "error"


@dataclass(frozen=True)
class VoiceMonitorView:
    label: str
    detail: str
    level: int
    meter: str


def voice_monitor_view(state: VoiceMonitorState) -> VoiceMonitorView:
    views = {
        VoiceMonitorState.INACTIVE: VoiceMonitorView(
            "⚪ Micrófono inactivo",
            "Escucha continua desactivada",
            0,
            "░░░░░░░░░░",
        ),
        VoiceMonitorState.STARTING: VoiceMonitorView(
            "🟡 Inicializando",
            "🎤 Buscando micrófono…",
            0,
            "░░░░░░░░░░",
        ),
        VoiceMonitorState.SILENCE: VoiceMonitorView(
            "🟢 Silencio",
            "🎤 Escuchando…",
            1,
            "█░░░░░░░░░",
        ),
        VoiceMonitorState.VOICE: VoiceMonitorView(
            "🟡 Voz detectada",
            "🎤 Captando voz…",
            6,
            "██████░░░░",
        ),
        VoiceMonitorState.PROCESSING: VoiceMonitorView(
            "🔴 Procesando",
            "Roby está interpretando lo escuchado…",
            10,
            "██████████",
        ),
        VoiceMonitorState.ERROR: VoiceMonitorView(
            "🔴 Error de micrófono",
            "No se pudo abrir el dispositivo de entrada",
            0,
            "░░░░░░░░░░",
        ),
    }
    return views[state]


class UIThreadDispatcher:
    """Queues UI callbacks so worker threads never call Tkinter directly."""

    def __init__(self) -> None:
        self._callbacks: SimpleQueue[Callable[[], None]] = SimpleQueue()

    def post(self, callback: Callable[[], None]) -> None:
        self._callbacks.put(callback)

    def drain(self) -> int:
        processed = 0
        while True:
            try:
                callback = self._callbacks.get_nowait()
            except Empty:
                return processed
            callback()
            processed += 1


class DesktopROBYAdapter(Protocol):
    def submit_text(
        self,
        text: str,
        session_id: str | None = None,
        *,
        explicit_document_ids: tuple[str, ...] = (),
        explicit_sources: tuple[object, ...] = (),
        explicit_evidence_references: tuple[object, ...] = (),
        integrated_visual_context: object | None = None,
    ) -> UIResponse: ...


@dataclass(frozen=True)
class DesktopUIConfig:
    title: str = "Roby XI.2"
    geometry: str = "880x680"
    greeting: str = "¿Qué tal, cómo estás?"


@dataclass(frozen=True)
class DesktopMessage:
    sender: str
    text: str

    def render(self) -> str:
        return f"{self.sender}: {self.text}"


class DesktopMessagePresenter:
    def user_message(self, text: str) -> DesktopMessage:
        return DesktopMessage("Vos", text)

    def roby_message(self, text: str) -> DesktopMessage:
        return DesktopMessage("Roby", text)


class DesktopConversationController:
    def __init__(
        self,
        adapter: DesktopROBYAdapter,
        presenter: DesktopMessagePresenter | None = None,
        voice_output: VoiceOutput | None = None,
        voice_input: VoiceInput | None = None,
    ) -> None:
        self.adapter = adapter
        self.presenter = presenter or DesktopMessagePresenter()
        self.voice_reader = VoiceResponseReader(voice_output or NullVoiceOutput())
        self.voice_transcriber = VoiceRequestTranscriber(
            voice_input or NullVoiceInput()
        )
        self.translation = ConversationalTranslation()
        self.clinical_safety = AdvancedClinicalSafetyService()
        self.chronic_conditions = ChronicConditionRegistryService()
        self.health_guidance = ConversationalHealthGuidanceService()
        self.allergies = AllergyRegistryService()
        self.device_architecture = DeviceArchitectureService()
        self.document_reading = DocumentReadingService()
        self.emergency_contacts = EmergencyContactService()
        self.health_orchestrator = HealthOrchestratorService()
        self.healthcare_directory = HealthcareDirectoryService()
        self.medical_consultation = MedicalConsultationPreparationService()
        self.medical_pdf_export = MedicalPdfExportService()
        self.stage_closure = M341StageClosureService()
        self.symptoms = StructuredSymptomService()
        self.vital_signs = VitalSignHistoryService()
        self.health_orientation = HealthOrientationService()
        self.task_agent = IntelligentTaskAgent()
        self.health_checkups = SecureHealthCheckupService()
        self.medications = SecureMedicationRegistryService()
        self.health_checkup_import = AssistedHealthCheckupImportService()
        self.health_comparison = HistoricalHealthComparisonService()

    def _adaptive_delivery_tone(self):
        tone = getattr(self.adapter, "adaptive_delivery_tone", None)
        if tone is not None:
            return tone
        gateway = getattr(self.adapter, "runtime", None)
        runtime = getattr(gateway, "_runtime", None)
        profile = getattr(runtime, "adaptive_personality_profile", None)
        return getattr(profile, "delivery_tone", None)

    def _m341_integrations(self) -> dict[str, bool]:
        return {
            "StructuredSymptomService": self.symptoms is not None,
            "AllergyRegistryService": self.allergies is not None,
            "ChronicConditionRegistryService": (self.chronic_conditions is not None),
            "HealthcareDirectoryService": self.healthcare_directory is not None,
            "EmergencyContactService": self.emergency_contacts is not None,
            "HealthOrchestratorService": self.health_orchestrator is not None,
            "ConversationalHealthGuidanceService": (self.health_guidance is not None),
            "MedicalPdfExportService": self.medical_pdf_export is not None,
            "DeviceArchitectureService": self.device_architecture is not None,
        }

    def submit(
        self,
        text: str,
        session_id: str | None = None,
        *,
        explicit_document_ids: tuple[str, ...] = (),
        explicit_sources: tuple[object, ...] = (),
        explicit_evidence_references: tuple[object, ...] = (),
        integrated_visual_context: object | None = None,
    ) -> list[DesktopMessage]:
        normalized_text = text.strip()
        if not normalized_text:
            return []

        safety = self.clinical_safety.prepare(
            normalized_text,
            session_id=session_id,
        )
        if safety.handled:
            self.voice_reader.voice_output.speak(safety.response)
            return [
                self.presenter.user_message(normalized_text),
                self.presenter.roby_message(safety.response),
            ]

        allergy = self.allergies.prepare(normalized_text, session_id=session_id)
        if allergy.handled:
            self.voice_reader.voice_output.speak(allergy.response)
            return [
                self.presenter.user_message(normalized_text),
                self.presenter.roby_message(allergy.response),
            ]

        emergency = self.emergency_contacts.prepare(
            normalized_text,
            session_id=session_id,
        )
        if emergency.handled:
            self.voice_reader.voice_output.speak(emergency.response)
            return [
                self.presenter.user_message(normalized_text),
                self.presenter.roby_message(emergency.response),
            ]

        directory = self.healthcare_directory.prepare(
            normalized_text,
            session_id=session_id,
        )
        if directory.handled:
            self.voice_reader.voice_output.speak(directory.response)
            return [
                self.presenter.user_message(normalized_text),
                self.presenter.roby_message(directory.response),
            ]

        condition = self.chronic_conditions.prepare(
            normalized_text,
            session_id=session_id,
        )
        if condition.handled:
            self.voice_reader.voice_output.speak(condition.response)
            return [
                self.presenter.user_message(normalized_text),
                self.presenter.roby_message(condition.response),
            ]

        consultation = self.medical_consultation.prepare(normalized_text)
        if consultation.handled:
            self.voice_reader.voice_output.speak(consultation.response)
            return [
                self.presenter.user_message(normalized_text),
                self.presenter.roby_message(consultation.response),
            ]

        vital = self.vital_signs.prepare(normalized_text, session_id=session_id)
        if vital.handled:
            self.voice_reader.voice_output.speak(vital.response)
            return [
                self.presenter.user_message(normalized_text),
                self.presenter.roby_message(vital.response),
            ]

        symptom = self.symptoms.prepare(normalized_text, session_id=session_id)
        if symptom.handled:
            self.voice_reader.voice_output.speak(symptom.response)
            return [
                self.presenter.user_message(normalized_text),
                self.presenter.roby_message(symptom.response),
            ]

        closure = self.stage_closure.prepare(
            normalized_text,
            integrations=self._m341_integrations(),
        )
        if closure.handled:
            self.voice_reader.voice_output.speak(closure.response)
            return [
                self.presenter.user_message(normalized_text),
                self.presenter.roby_message(closure.response),
            ]

        devices = self.device_architecture.prepare(normalized_text)
        if devices.handled:
            self.voice_reader.voice_output.speak(devices.response)
            return [
                self.presenter.user_message(normalized_text),
                self.presenter.roby_message(devices.response),
            ]

        exported = self.medical_pdf_export.prepare(normalized_text)
        if exported.handled:
            self.voice_reader.voice_output.speak(exported.response)
            return [
                self.presenter.user_message(normalized_text),
                self.presenter.roby_message(exported.response),
            ]

        guided = self.health_guidance.prepare(normalized_text)
        if guided.handled:
            self.voice_reader.voice_output.speak(guided.response)
            return [
                self.presenter.user_message(normalized_text),
                self.presenter.roby_message(guided.response),
            ]

        orchestrated = self.health_orchestrator.prepare(normalized_text)
        if orchestrated.handled:
            self.voice_reader.voice_output.speak(orchestrated.response)
            return [
                self.presenter.user_message(normalized_text),
                self.presenter.roby_message(orchestrated.response),
            ]

        task = self.task_agent.prepare(normalized_text, session_id=session_id)
        if task.handled:
            self.voice_reader.voice_output.speak(task.response)
            return [
                self.presenter.user_message(normalized_text),
                self.presenter.roby_message(task.response),
            ]

        medication = self.medications.prepare(
            normalized_text,
            session_id=session_id,
        )
        if medication.handled:
            self.voice_reader.voice_output.speak(medication.response)
            return [
                self.presenter.user_message(normalized_text),
                self.presenter.roby_message(medication.response),
            ]

        imported = self.health_checkup_import.prepare(
            normalized_text,
            session_id=session_id,
        )
        if imported.handled:
            self.voice_reader.voice_output.speak(imported.response)
            return [
                self.presenter.user_message(normalized_text),
                self.presenter.roby_message(imported.response),
            ]

        checkup = self.health_checkups.prepare(
            normalized_text,
            session_id=session_id,
        )
        if checkup.handled:
            self.voice_reader.voice_output.speak(checkup.response)
            return [
                self.presenter.user_message(normalized_text),
                self.presenter.roby_message(checkup.response),
            ]

        comparison = self.health_comparison.prepare(normalized_text)
        if comparison.handled:
            self.voice_reader.voice_output.speak(comparison.response)
            return [
                self.presenter.user_message(normalized_text),
                self.presenter.roby_message(comparison.response),
            ]

        health = self.health_orientation.prepare(
            normalized_text,
            session_id=session_id,
        )
        if health.handled and health.response:
            self.voice_reader.voice_output.speak(health.response)
            return [
                self.presenter.user_message(normalized_text),
                self.presenter.roby_message(health.response),
            ]
        document = self.document_reading.prepare(normalized_text)
        if document.handled and document.error:
            self.voice_reader.voice_output.speak(document.error)
            return [
                self.presenter.user_message(normalized_text),
                self.presenter.roby_message(document.error),
            ]
        translation = self.translation.parse(normalized_text)
        submitted_text = (
            health.prompt
            if health.handled
            else document.prompt
            if document.handled
            else translation.prompt()
            if translation
            else normalized_text
        )
        if (
            explicit_document_ids
            or explicit_sources
            or explicit_evidence_references
            or integrated_visual_context is not None
        ):
            response = self.adapter.submit_text(
                submitted_text,
                session_id=session_id,
                explicit_document_ids=explicit_document_ids,
                explicit_sources=explicit_sources,
                explicit_evidence_references=explicit_evidence_references,
                integrated_visual_context=integrated_visual_context,
            )
        else:
            response = self.adapter.submit_text(
                submitted_text,
                session_id=session_id,
            )
        delivery_tone = self._adaptive_delivery_tone()
        self.voice_reader.read(response, delivery_tone=delivery_tone)
        return [
            self.presenter.user_message(normalized_text),
            self.presenter.roby_message(response.text),
        ]

    def submit_with_visual_companion(
        self,
        text: str,
        session_id: str | None = None,
        *,
        explicit_document_ids: tuple[str, ...] = (),
        explicit_sources: tuple[object, ...] = (),
        explicit_evidence_references: tuple[object, ...] = (),
        integrated_visual_context: object | None = None,
    ) -> tuple[list[DesktopMessage], object | None]:
        normalized_text = text.strip()
        submit_visual = getattr(
            self.adapter,
            "submit_text_with_visual_companion",
            None,
        )
        if not callable(submit_visual):
            return self.submit(normalized_text, session_id), None
        response, applied_result = submit_visual(
            normalized_text,
            session_id=session_id,
            explicit_document_ids=explicit_document_ids,
            explicit_sources=explicit_sources,
            explicit_evidence_references=explicit_evidence_references,
            integrated_visual_context=integrated_visual_context,
        )
        delivery_tone = self._adaptive_delivery_tone()
        self.voice_reader.read(response, delivery_tone=delivery_tone)
        messages = [
            self.presenter.user_message(normalized_text),
            self.presenter.roby_message(response.text),
        ]
        return messages, applied_result

    def submit_voice(
        self,
        session_id: str | None = None,
    ) -> list[DesktopMessage]:
        text = self.voice_transcriber.transcribe().strip()
        if not text:
            return []
        submit_voice = getattr(self.adapter, "submit_voice", None)
        if submit_voice is None:
            return self.submit(text, session_id=session_id)
        safety = self.clinical_safety.prepare(text, session_id=session_id)
        if safety.handled:
            self.voice_reader.voice_output.speak(safety.response)
            return [
                self.presenter.user_message(text),
                self.presenter.roby_message(safety.response),
            ]

        allergy = self.allergies.prepare(text, session_id=session_id)
        if allergy.handled:
            self.voice_reader.voice_output.speak(allergy.response)
            return [
                self.presenter.user_message(text),
                self.presenter.roby_message(allergy.response),
            ]

        emergency = self.emergency_contacts.prepare(
            text,
            session_id=session_id,
        )
        if emergency.handled:
            self.voice_reader.voice_output.speak(emergency.response)
            return [
                self.presenter.user_message(text),
                self.presenter.roby_message(emergency.response),
            ]

        directory = self.healthcare_directory.prepare(
            text,
            session_id=session_id,
        )
        if directory.handled:
            self.voice_reader.voice_output.speak(directory.response)
            return [
                self.presenter.user_message(text),
                self.presenter.roby_message(directory.response),
            ]

        condition = self.chronic_conditions.prepare(
            text,
            session_id=session_id,
        )
        if condition.handled:
            self.voice_reader.voice_output.speak(condition.response)
            return [
                self.presenter.user_message(text),
                self.presenter.roby_message(condition.response),
            ]

        consultation = self.medical_consultation.prepare(text)
        if consultation.handled:
            self.voice_reader.voice_output.speak(consultation.response)
            return [
                self.presenter.user_message(text),
                self.presenter.roby_message(consultation.response),
            ]

        vital = self.vital_signs.prepare(text, session_id=session_id)
        if vital.handled:
            self.voice_reader.voice_output.speak(vital.response)
            return [
                self.presenter.user_message(text),
                self.presenter.roby_message(vital.response),
            ]

        symptom = self.symptoms.prepare(text, session_id=session_id)
        if symptom.handled:
            self.voice_reader.voice_output.speak(symptom.response)
            return [
                self.presenter.user_message(text),
                self.presenter.roby_message(symptom.response),
            ]

        closure = self.stage_closure.prepare(
            text,
            integrations=self._m341_integrations(),
        )
        if closure.handled:
            self.voice_reader.voice_output.speak(closure.response)
            return [
                self.presenter.user_message(text),
                self.presenter.roby_message(closure.response),
            ]

        devices = self.device_architecture.prepare(text)
        if devices.handled:
            self.voice_reader.voice_output.speak(devices.response)
            return [
                self.presenter.user_message(text),
                self.presenter.roby_message(devices.response),
            ]

        exported = self.medical_pdf_export.prepare(text)
        if exported.handled:
            self.voice_reader.voice_output.speak(exported.response)
            return [
                self.presenter.user_message(text),
                self.presenter.roby_message(exported.response),
            ]

        guided = self.health_guidance.prepare(text)
        if guided.handled:
            self.voice_reader.voice_output.speak(guided.response)
            return [
                self.presenter.user_message(text),
                self.presenter.roby_message(guided.response),
            ]

        orchestrated = self.health_orchestrator.prepare(text)
        if orchestrated.handled:
            self.voice_reader.voice_output.speak(orchestrated.response)
            return [
                self.presenter.user_message(text),
                self.presenter.roby_message(orchestrated.response),
            ]

        task = self.task_agent.prepare(text, session_id=session_id)
        if task.handled:
            self.voice_reader.voice_output.speak(task.response)
            return [
                self.presenter.user_message(text),
                self.presenter.roby_message(task.response),
            ]

        medication = self.medications.prepare(text, session_id=session_id)
        if medication.handled:
            self.voice_reader.voice_output.speak(medication.response)
            return [
                self.presenter.user_message(text),
                self.presenter.roby_message(medication.response),
            ]

        imported = self.health_checkup_import.prepare(
            text,
            session_id=session_id,
        )
        if imported.handled:
            self.voice_reader.voice_output.speak(imported.response)
            return [
                self.presenter.user_message(text),
                self.presenter.roby_message(imported.response),
            ]

        checkup = self.health_checkups.prepare(text, session_id=session_id)
        if checkup.handled:
            self.voice_reader.voice_output.speak(checkup.response)
            return [
                self.presenter.user_message(text),
                self.presenter.roby_message(checkup.response),
            ]

        comparison = self.health_comparison.prepare(text)
        if comparison.handled:
            self.voice_reader.voice_output.speak(comparison.response)
            return [
                self.presenter.user_message(text),
                self.presenter.roby_message(comparison.response),
            ]

        health = self.health_orientation.prepare(text, session_id=session_id)
        if health.handled and health.response:
            self.voice_reader.voice_output.speak(health.response)
            return [
                self.presenter.user_message(text),
                self.presenter.roby_message(health.response),
            ]
        document = self.document_reading.prepare(text)
        if document.handled and document.error:
            self.voice_reader.voice_output.speak(document.error)
            return [
                self.presenter.user_message(text),
                self.presenter.roby_message(document.error),
            ]
        translation = self.translation.parse(text)
        submitted_text = (
            health.prompt
            if health.handled
            else document.prompt
            if document.handled
            else translation.prompt()
            if translation
            else text
        )
        response = submit_voice(submitted_text, session_id=session_id)
        delivery_tone = self._adaptive_delivery_tone()
        self.voice_reader.read(response, delivery_tone=delivery_tone)
        return [
            self.presenter.user_message(text),
            self.presenter.roby_message(response.text),
        ]


class ROBYDesktopApp:
    def __init__(
        self,
        adapter: DesktopROBYAdapter,
        config: DesktopUIConfig | None = None,
        voice_output: VoiceOutput | None = None,
        voice_input: VoiceInput | None = None,
        startup_announcer: Callable[[], str] | None = None,
        on_start: Callable[[], None] | None = None,
        on_stop: Callable[[], None] | None = None,
        drain_notifications: Callable[[], tuple[str, ...]] | None = None,
        capability_snapshot: (
            Callable[[], tuple[RuntimeCapabilityView, ...]] | None
        ) = None,
        lifecycle_manager: ApplicationLifecycleManager | None = None,
        update_attention: Callable[[AttentionState], None] | None = None,
        on_audio_error: Callable[[], object] | None = None,
        document_inbox: object | None = None,
        governed_visual_collection_runtime: object | None = None,
        external_image_presenter: object | None = None,
        attachment_owner: str = "Carlos",
    ) -> None:
        self.adapter = adapter
        self.config = config or DesktopUIConfig()
        self.voice_output = voice_output or NullVoiceOutput()
        self.voice_input = voice_input or NullVoiceInput()
        self.startup_announcer = startup_announcer
        self.on_start = on_start
        self.on_stop = on_stop
        self.drain_notifications = drain_notifications
        self.capability_snapshot = capability_snapshot
        self.lifecycle_manager = lifecycle_manager or ApplicationLifecycleManager()
        self.update_attention = update_attention
        self.on_audio_error = on_audio_error
        self.document_inbox = document_inbox
        self.governed_visual_collection_runtime = governed_visual_collection_runtime
        self.external_image_presenter = external_image_presenter
        self.attachment_owner = attachment_owner.strip() or "Carlos"
        self.controller = DesktopConversationController(
            adapter=self.adapter,
            voice_output=self.voice_output,
            voice_input=self.voice_input,
        )
        self.session_id: str | None = None
        self.restart_requested = False

    @property
    def diagnostics(self) -> object | None:
        """Expose safe adapter diagnostics without rendering private turn content."""

        return getattr(self.adapter, "diagnostics", None)

    def startup_messages(self) -> list[DesktopMessage]:
        if self.startup_announcer is None:
            return []
        try:
            startup_text = self.startup_announcer().strip()
        except Exception:
            return []
        if not startup_text:
            return []
        spoken = self.controller.voice_reader.prosody_formatter.format(startup_text)
        if spoken:
            try:
                self.controller.voice_reader.voice_output.speak(spoken)
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                # External TTS failure must not prevent the written startup greeting.
                pass
        return [self.controller.presenter.roby_message(startup_text)]

    def capability_messages(self) -> list[DesktopMessage]:
        """Render the official capability registry for the desktop transcript."""
        if self.capability_snapshot is None:
            return [
                self.controller.presenter.roby_message(
                    "El registro operacional no está disponible en esta interfaz."
                )
            ]
        try:
            capabilities = self.capability_snapshot()
        except Exception:
            return [
                self.controller.presenter.roby_message(
                    "No pude consultar el registro operacional."
                )
            ]
        if not capabilities:
            text = "No hay capacidades operacionales registradas."
        else:
            lines = ["Capacidades del runtime oficial:"]
            for capability in capabilities:
                state = "habilitada" if capability.enabled else "deshabilitada"
                lines.append(f"- {capability.name} [{state}]: {capability.description}")
            lines.append(f"Total: {len(capabilities)}.")
            text = "\n".join(lines)
        return [self.controller.presenter.roby_message(text)]

    @staticmethod
    def lifecycle_command(text: str) -> LifecycleExitReason | None:
        normalized = re.sub(r"[.,;:!?]+", "", text.casefold()).strip()
        normalized = re.sub(r"^roby\s+", "", normalized).strip()
        shutdown_commands = {
            "apagate",
            "apagáte",
            "cerrate",
            "cerráte",
            "cerra la aplicacion",
            "cerrá la aplicación",
            "terminamos por hoy",
            "hasta mañana",
            "podes descansar",
            "podés descansar",
        }
        restart_commands = {
            "reiniciate",
            "reiniciáte",
            "reinicia la aplicacion",
            "reiniciá la aplicación",
        }
        if normalized in shutdown_commands:
            return LifecycleExitReason.VOICE_SHUTDOWN
        if normalized in restart_commands:
            return LifecycleExitReason.RESTART
        return None

    @property
    def recovery_message(self) -> str:
        return self.lifecycle_manager.recovery_message()

    def run(self) -> None:
        import tkinter as tk
        from tkinter import filedialog, scrolledtext, ttk

        root = tk.Tk()
        root.title(self.config.title)
        root.geometry(self.config.geometry)
        def cancel_manual_preview() -> None:
            preview_coordinator.cancel()

        floating_image_viewer = DesktopGovernedFloatingImageViewer(
            root=root,
            toolkit=tk,
            on_close=cancel_manual_preview,
        )

        frame = ttk.Frame(root)
        frame.pack(expand=True, fill="both", padx=12, pady=12)

        transcript = scrolledtext.ScrolledText(
            frame,
            wrap="word",
            state="disabled",
            font=("Segoe UI", 11),
        )
        transcript.pack(expand=True, fill="both")

        entry = ttk.Entry(frame, font=("Segoe UI", 11))
        entry.pack(fill="x", pady=(8, 0))

        diagnostic_mode = os.getenv(
            "ROBY_AUDIO_DIAGNOSTIC_MODE", "false"
        ).strip().casefold() in {"1", "true", "yes", "on"}
        engine = getattr(self.voice_input, "voice_input", self.voice_input)
        engine_name = type(engine).__name__
        diagnostic_text = tk.StringVar(
            value=f"DIAG · entrada={engine_name} · preparando escucha"
        )
        if diagnostic_mode:
            ttk.Label(
                frame,
                textvariable=diagnostic_text,
                anchor="w",
            ).pack(fill="x", pady=(4, 0))

        footer = ttk.Frame(frame)
        footer.pack(fill="x", pady=(6, 0))
        monitor = ttk.Frame(footer)
        monitor.pack(side="left", fill="x", expand=True)
        listening_status = ttk.Label(monitor, text="⚪ Micrófono inactivo")
        listening_status.pack(side="left")
        listening_detail = ttk.Label(monitor, text="Escucha continua desactivada")
        listening_detail.pack(side="left", padx=(10, 0))
        audio_level = ttk.Progressbar(
            monitor,
            orient="horizontal",
            mode="determinate",
            maximum=10,
            length=120,
        )
        audio_level.pack(side="left", padx=(10, 0))
        audio_meter = ttk.Label(monitor, text="░░░░░░░░░░")
        audio_meter.pack(side="left", padx=(6, 0))
        hint = ttk.Label(footer, text="Enter para enviar")
        hint.pack(side="left", padx=(10, 0))

        def append(message: str) -> None:
            transcript.configure(state="normal")
            transcript.insert("end", message + "\n")
            transcript.configure(state="disabled")
            transcript.see("end")

        busy = False
        staged_document_ids: tuple[str, ...] = ()
        staged_visual_context: object | None = None
        stop_listening = Event()
        dictation = IntelligentDictationSession()

        def set_attention(state: AttentionState) -> None:
            if self.update_attention is None:
                return
            try:
                self.update_attention(state)
            except Exception:
                return

        typing_generation = 0

        def note_user_typing(_event=None) -> None:
            nonlocal typing_generation
            if busy:
                return
            typing_generation += 1
            generation = typing_generation
            set_attention(AttentionState.USER_TYPING)

            def release_typing_attention() -> None:
                if generation == typing_generation and not busy:
                    set_attention(AttentionState.AVAILABLE)

            root.after(750, release_typing_attention)

        entry.bind("<KeyPress>", note_user_typing)
        close_request: dict[str, Callable[[LifecycleExitReason], None]] = {}
        monitor_state = VoiceMonitorState.INACTIVE

        def set_monitor_state(
            state: VoiceMonitorState,
            *,
            level: int | None = None,
            detail: str = "",
            device_name: str = "",
        ) -> None:
            nonlocal monitor_state
            monitor_state = state
            view = voice_monitor_view(state)
            actual_level = view.level if level is None else max(0, min(10, level))
            meter = "█" * actual_level + "░" * (10 - actual_level)
            shown_detail = detail or view.detail
            if device_name:
                shown_detail = f"🎤 {device_name} · {shown_detail}"
            listening_status.configure(text=view.label)
            listening_detail.configure(text=shown_detail)
            audio_level.configure(value=actual_level)
            audio_meter.configure(text=meter)

        def return_to_silence_after_voice() -> None:
            if monitor_state is VoiceMonitorState.VOICE and not busy:
                set_monitor_state(VoiceMonitorState.SILENCE)

        def finish_submit(messages: list[DesktopMessage]) -> None:
            nonlocal busy
            for message in messages:
                if message.sender != "Vos":
                    append(message.render())
            busy = False
            set_attention(AttentionState.AVAILABLE)
            pause_audio = getattr(self.voice_input, "set_paused", None)
            if callable(pause_audio):
                pause_audio(False)
            entry.configure(state="normal")
            hint.configure(text="Enter para enviar")
            if not isinstance(self.voice_input, NullVoiceInput):
                set_monitor_state(VoiceMonitorState.SILENCE)
            entry.focus_set()

        def submit(
            text_override: str | None = None,
            *,
            render_user: bool = True,
            explicit_document_ids: tuple[str, ...] = (),
            explicit_sources: tuple[object, ...] = (),
            explicit_evidence_references: tuple[object, ...] = (),
            integrated_visual_context: object | None = None,
        ) -> None:
            nonlocal busy, staged_document_ids, staged_visual_context
            if busy:
                return
            text = (text_override if text_override is not None else entry.get()).strip()
            if not text:
                return

            dictation_result = dictation.handle(text)
            if dictation_result.handled:
                entry.delete(0, "end")
                if render_user:
                    append(self.controller.presenter.user_message(text).render())
                if dictation_result.document:
                    label = (
                        "Dictado final"
                        if dictation_result.action is DictationAction.FINISHED
                        else "Dictado"
                    )
                    append(f"{label}: {dictation_result.document}")
                append(
                    self.controller.presenter.roby_message(
                        dictation_result.message
                    ).render()
                )
                if dictation_result.action is not DictationAction.UPDATED:
                    self.controller.voice_reader.voice_output.speak(
                        dictation_result.message
                    )
                hint.configure(
                    text=(
                        "Modo dictado activo · Enter para agregar texto"
                        if dictation_result.active
                        else "Enter para enviar"
                    )
                )
                return

            lifecycle_reason = self.lifecycle_command(text)
            if lifecycle_reason is not None:
                append(self.controller.presenter.user_message(text).render())
                farewell = (
                    "Un momento. Guardo el estado y vuelvo enseguida."
                    if lifecycle_reason is LifecycleExitReason.RESTART
                    else "Perfecto. Guardo todo y me apago. Hasta luego."
                )
                append(self.controller.presenter.roby_message(farewell).render())
                self.controller.voice_reader.voice_output.speak(farewell)
                root.after(50, lambda: close_request["close"](lifecycle_reason))
                return

            turn_document_ids = staged_document_ids + explicit_document_ids
            turn_visual_context = (
                integrated_visual_context
                if integrated_visual_context is not None
                else staged_visual_context
            )
            staged_document_ids = ()
            staged_visual_context = None

            busy = True
            set_attention(AttentionState.ROBY_RESPONDING)
            pause_audio = getattr(self.voice_input, "set_paused", None)
            if callable(pause_audio):
                pause_audio(True)
            entry.delete(0, "end")
            entry.configure(state="disabled")
            hint.configure(text="Roby está pensando…")
            set_monitor_state(VoiceMonitorState.PROCESSING)
            if render_user:
                append(self.controller.presenter.user_message(text).render())

            def worker() -> None:
                try:
                    messages, applied_result = (
                        self.controller.submit_with_visual_companion(
                            text,
                            self.session_id,
                            explicit_document_ids=turn_document_ids,
                            explicit_sources=explicit_sources,
                            explicit_evidence_references=(explicit_evidence_references),
                            integrated_visual_context=turn_visual_context,
                        )
                    )
                    if (
                        applied_result is not None
                        and self.external_image_presenter is not None
                    ):
                        visual_turn = bind_applied_result_to_desktop(applied_result)
                        dispatch_desktop_runtime_visual_render(
                            ui_dispatcher,
                            lambda: connect_governed_floating_viewer(
                                presenter=self.external_image_presenter,
                                viewer=preview_bridge,
                                artifacts=visual_turn.visual_companion.artifacts,
                            ),
                        )
                except Exception:
                    messages = [
                        self.controller.presenter.roby_message(
                            "Ocurrió un error al procesar tu mensaje."
                        )
                    ]
                root.after(0, lambda: finish_submit(messages))

            Thread(target=worker, daemon=True).start()

        def attach_file() -> None:
            nonlocal staged_document_ids, staged_visual_context
            selected = filedialog.askopenfilename(title="Adjuntar archivo")
            if not selected:
                return
            path = Path(selected)
            suffix = path.suffix.casefold()
            if suffix == ".zip":
                append(
                    self.controller.presenter.roby_message(
                        "Formato .zip no soportado para adjuntar directamente."
                    ).render()
                )
                return
            media_type = (
                mimetypes.guess_type(path.name)[0] or "application/octet-stream"
            )
            if media_type.startswith("image/"):
                visual_runtime = self.governed_visual_collection_runtime
                gateway = getattr(visual_runtime, "vision_gateway", None)
                if gateway is None:
                    append(
                        self.controller.presenter.roby_message(
                            "La colección visual gobernada no está disponible."
                        ).render()
                    )
                    return
                stored = gateway.store_image(
                    ImageStoreRequest(
                        owner=self.attachment_owner,
                        label=path.name,
                        explicit_user_consent=True,
                        user_requested=True,
                    ),
                    image_bytes=path.read_bytes(),
                    mime_type=media_type,
                )
                interceptor = getattr(visual_runtime, "interceptor", None)
                if interceptor is None:
                    append(
                        self.controller.presenter.roby_message(
                            "La convergencia visual gobernada no está disponible."
                        ).render()
                    )
                    return
                visual_context = interceptor.analyze_image_for_cognitive_convergence(
                    owner=self.attachment_owner,
                    image_id=stored.image_id,
                    explicit_user_consent=True,
                )
                staged_visual_context = visual_context
                append(
                    self.controller.presenter.roby_message(
                        f"Imagen adjuntada: {stored.label}."
                    ).render()
                )
                return
            if self.document_inbox is None:
                append(
                    self.controller.presenter.roby_message(
                        "La bandeja documental gobernada no está disponible."
                    ).render()
                )
                return
            try:
                content = self.controller.document_reading.read_text(path)
                record = self.document_inbox.ingest_text(
                    content,
                    title=path.name,
                    source_name=path.name,
                    media_type=media_type,
                )
            except (OSError, ValueError) as exc:
                append(self.controller.presenter.roby_message(str(exc)).render())
                return
            staged_document_ids += (record.document_id,)
            append(
                self.controller.presenter.roby_message(
                    f"Documento adjuntado: {path.name}."
                ).render()
            )

        attach_button = ttk.Button(
            footer,
            text="Adjuntar",
            command=attach_file,
        )
        attach_button.pack(side="right", padx=(0, 6))

        def show_capabilities() -> None:
            for message in self.capability_messages():
                append(message.render())

        capabilities_button = ttk.Button(
            footer,
            text="Capacidades",
            command=show_capabilities,
        )
        capabilities_button.pack(side="right")

        exit_button = ttk.Button(
            footer,
            text="Salir",
            command=lambda: close_request["close"](LifecycleExitReason.MENU_EXIT),
        )
        exit_button.pack(side="right", padx=(0, 6))

        def poll_notifications() -> None:
            nonlocal busy
            if stopped:
                return
            if self.drain_notifications is not None and not busy:
                for text in self.drain_notifications():
                    append(self.controller.presenter.roby_message(text).render())
                    spoken = self.controller.voice_reader.prosody_formatter.format(text)
                    if spoken:
                        busy = True
                        pause_audio = getattr(self.voice_input, "set_paused", None)
                        if callable(pause_audio):
                            pause_audio(True)
                        try:
                            self.controller.voice_reader.voice_output.speak(spoken)
                        finally:
                            if callable(pause_audio):
                                pause_audio(False)
                            busy = False
            root.after(250, poll_notifications)

        stopped = False
        ui_dispatcher = UIThreadDispatcher()
        preview_executor = ThreadPoolExecutor(max_workers=3)
        preview_coordinator = GovernedImagePreviewCoordinator(
            viewer=floating_image_viewer,
            dispatcher=ui_dispatcher,
            fetcher=fetch_desktop_governed_preview,
            executor=preview_executor,
        )

        class PreviewBridge:
            def open(self, artifacts: tuple[object, ...]) -> None:
                preview_coordinator.present(artifacts)

        preview_bridge = PreviewBridge()

        def poll_ui_dispatcher() -> None:
            if stopped:
                return
            ui_dispatcher.drain()
            root.after(50, poll_ui_dispatcher)

        def handle_audio_event(event: AudioEngineEvent) -> None:
            state_map = {
                AudioEngineState.INACTIVE: VoiceMonitorState.INACTIVE,
                AudioEngineState.STARTING: VoiceMonitorState.STARTING,
                AudioEngineState.SILENCE: VoiceMonitorState.SILENCE,
                AudioEngineState.VOICE: VoiceMonitorState.VOICE,
                AudioEngineState.ERROR: VoiceMonitorState.ERROR,
                AudioEngineState.STOPPED: VoiceMonitorState.INACTIVE,
            }
            state = state_map[event.state]
            if state is VoiceMonitorState.VOICE:
                set_attention(AttentionState.USER_SPEAKING)
            elif state is VoiceMonitorState.SILENCE and not busy:
                set_attention(AttentionState.AVAILABLE)
            set_monitor_state(
                state,
                level=event.level,
                detail=event.detail,
                device_name=event.device_name,
            )
            if (
                event.state is AudioEngineState.ERROR
                and self.on_audio_error is not None
            ):
                try:
                    self.on_audio_error()
                except Exception:
                    pass
            if diagnostic_mode:
                if event.text:
                    diagnostic_text.set(f"DIAG · Vosk: {event.text}")
                elif event.detail:
                    diagnostic_text.set(event.detail)

        event_sink_setter = getattr(self.voice_input, "set_event_sink", None)
        if callable(event_sink_setter):
            event_sink_setter(
                lambda event: ui_dispatcher.post(
                    lambda event=event: handle_audio_event(event)
                )
            )

        def poll_audio_diagnostics() -> None:
            if stopped or not diagnostic_mode:
                return
            snapshot_getter = getattr(self.voice_input, "diagnostic_snapshot", None)
            if not callable(snapshot_getter):
                snapshot_getter = getattr(engine, "diagnostic_snapshot", None)
            if callable(snapshot_getter):
                try:
                    snapshot = snapshot_getter()
                except Exception as exc:
                    diagnostic_text.set(f"DIAG · snapshot falló: {exc}")
                else:
                    if snapshot is not None:
                        device = snapshot.device_name or "sin dispositivo"
                        diagnostic_text.set(
                            "DIAG · "
                            f"worker={'sí' if snapshot.worker_alive else 'no'} · "
                            f"stream={'sí' if snapshot.stream_open else 'no'} · "
                            f"frames={snapshot.callback_frames} · "
                            f"cola={snapshot.queued_audio_frames} · "
                            f"estado={snapshot.state.value} · "
                            f"nivel={snapshot.level} · "
                            f"umbral={snapshot.voice_threshold} · "
                            f"dispositivo={device}"
                        )
            root.after(1000, poll_audio_diagnostics)

        def start_voice_input() -> bool:
            start_audio = getattr(self.voice_input, "start", None)
            if diagnostic_mode:
                ui_dispatcher.post(
                    lambda: diagnostic_text.set(
                        f"DIAG · entrada={engine_name} · llamando start()"
                    )
                )
            if not callable(start_audio):
                if diagnostic_mode:
                    ui_dispatcher.post(
                        lambda: diagnostic_text.set(
                            "DIAG · "
                            f"entrada={engine_name} · sin start(); transcribe directo"
                        )
                    )
                return True
            try:
                start_audio()
            except Exception as exc:
                detail = f"No se pudo iniciar el motor de voz: {exc}"
                ui_dispatcher.post(
                    lambda detail=detail: set_monitor_state(
                        VoiceMonitorState.ERROR, detail=detail
                    )
                )
                return False
            error = str(getattr(self.voice_input, "error", "")).strip()
            if diagnostic_mode and not error:
                ui_dispatcher.post(
                    lambda: diagnostic_text.set(
                        f"DIAG · entrada={engine_name} · start() completado"
                    )
                )
            if error:
                ui_dispatcher.post(
                    lambda error=error: set_monitor_state(
                        VoiceMonitorState.ERROR, detail=error
                    )
                )
                return False
            return True

        def close(
            reason: LifecycleExitReason = LifecycleExitReason.WINDOW_CLOSE,
        ) -> None:
            nonlocal stopped
            if stopped:
                return
            stopped = True
            preview_coordinator.shutdown()
            stop_listening.set()
            stop_audio = getattr(self.voice_input, "stop", None)
            if callable(stop_audio):
                stop_audio()
            steps = []
            if self.on_stop is not None:
                steps.append(("runtime", self.on_stop))
            try:
                snapshot = self.lifecycle_manager.shutdown(
                    reason=reason,
                    steps=steps,
                )
                self.restart_requested = snapshot.restart_requested
            finally:
                root.destroy()

        close_request["close"] = close

        menu_bar = tk.Menu(root)
        application_menu = tk.Menu(menu_bar, tearoff=False)
        application_menu.add_command(
            label="Reiniciar",
            command=lambda: close(LifecycleExitReason.RESTART),
        )
        application_menu.add_separator()
        application_menu.add_command(
            label="Salir",
            command=lambda: close(LifecycleExitReason.MENU_EXIT),
        )
        menu_bar.add_cascade(label="Roby", menu=application_menu)
        root.configure(menu=menu_bar)

        def continuous_listening_worker() -> None:
            if diagnostic_mode:
                ui_dispatcher.post(
                    lambda: diagnostic_text.set(
                        f"DIAG · entrada={engine_name} · worker iniciado"
                    )
                )
            if not start_voice_input():
                return
            wake_word = (
                os.getenv("ROBY_VOICE_WAKE_WORD", "roby").strip().casefold() or "roby"
            )
            configured_aliases = os.getenv(
                "ROBY_VOICE_WAKE_ALIASES", "roby,robi,robby,robbie,ruby,rubi"
            )
            wake_aliases = tuple(
                dict.fromkeys(
                    [wake_word]
                    + [
                        item.strip().casefold()
                        for item in configured_aliases.split(",")
                        if item.strip()
                    ]
                )
            )
            session_gate = VoiceSessionGate(
                wake_aliases=wake_aliases,
                active_window_seconds=float(
                    os.getenv("ROBY_VOICE_ACTIVE_WINDOW_SECONDS", "30") or 30
                ),
                min_words=int(os.getenv("ROBY_VOICE_MIN_COMMAND_WORDS", "2") or 2),
                require_wake_word=(
                    os.getenv("ROBY_VOICE_REQUIRE_WAKE_WORD", "false")
                    .strip()
                    .casefold()
                    in {"1", "true", "yes", "on"}
                ),
            )
            while not stop_listening.is_set():
                if busy:
                    time.sleep(0.1)
                    continue
                ui_dispatcher.post(lambda: set_monitor_state(VoiceMonitorState.SILENCE))
                if diagnostic_mode:
                    ui_dispatcher.post(
                        lambda: diagnostic_text.set(
                            "DIAG · entrada="
                            f"{engine_name} · esperando audio/transcripción"
                        )
                    )
                try:
                    heard = self.controller.voice_transcriber.transcribe().strip()
                except Exception as exc:
                    detail = f"El ciclo de escucha se detuvo: {exc}"
                    ui_dispatcher.post(
                        lambda detail=detail: set_monitor_state(
                            VoiceMonitorState.ERROR, detail=detail
                        )
                    )
                    return
                if not heard:
                    error = str(getattr(self.voice_input, "error", "")).strip()
                    if error:
                        ui_dispatcher.post(
                            lambda error=error: set_monitor_state(
                                VoiceMonitorState.ERROR, detail=error
                            )
                        )
                        return
                    time.sleep(0.05)
                    continue
                if diagnostic_mode:
                    ui_dispatcher.post(
                        lambda heard=heard: diagnostic_text.set(
                            f"DIAG · texto reconocido: {heard}"
                        )
                    )
                if dictation.active:
                    spoken = heard

                    def show_dictation_heard(text: str = spoken) -> None:
                        set_monitor_state(VoiceMonitorState.VOICE)
                        append(self.controller.presenter.user_message(text).render())
                        root.after(900, return_to_silence_after_voice)

                    ui_dispatcher.post(show_dictation_heard)
                    ui_dispatcher.post(
                        lambda text=spoken: submit(text, render_user=False)
                    )
                    continue

                decision = session_gate.evaluate(heard)
                if not decision.accepted:
                    if decision.addressed and decision.reason == "wake_only":

                        def acknowledge_wake(text: str = heard) -> None:
                            set_monitor_state(VoiceMonitorState.VOICE)
                            user_message = self.controller.presenter.user_message(text)
                            append(user_message.render())
                            reply = "Sí, te escucho."
                            roby_message = self.controller.presenter.roby_message(reply)
                            append(roby_message.render())
                            self.controller.voice_reader.voice_output.speak(reply)
                            root.after(900, return_to_silence_after_voice)

                        ui_dispatcher.post(acknowledge_wake)
                    continue

                spoken = decision.command

                def show_heard(text: str = spoken) -> None:
                    set_monitor_state(VoiceMonitorState.VOICE)
                    append(self.controller.presenter.user_message(text).render())
                    root.after(900, return_to_silence_after_voice)

                ui_dispatcher.post(show_heard)

                def dispatch(text: str = spoken) -> None:
                    if busy:
                        return
                    submit(text, render_user=False)

                ui_dispatcher.post(dispatch)

        if not isinstance(self.voice_input, NullVoiceInput):
            Thread(target=continuous_listening_worker, daemon=True).start()
            if callable(getattr(self.voice_input, "set_event_sink", None)):
                set_monitor_state(VoiceMonitorState.STARTING)
            else:
                set_monitor_state(VoiceMonitorState.SILENCE)
            hint.configure(text="Escucha continua activa · Enter para enviar")

        entry.bind("<Return>", lambda _event: submit())
        root.protocol(
            "WM_DELETE_WINDOW",
            lambda: close(LifecycleExitReason.WINDOW_CLOSE),
        )
        self.lifecycle_manager.start()
        if self.on_start is not None:
            self.on_start()
        poll_ui_dispatcher()
        poll_notifications()
        poll_audio_diagnostics()
        if self.config.greeting.strip():
            greeting = self.config.greeting.strip()
            append(self.controller.presenter.roby_message(greeting).render())
            spoken = self.controller.voice_reader.prosody_formatter.format(greeting)
            if spoken:
                try:
                    self.controller.voice_reader.voice_output.speak(spoken)
                except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                    # A TTS failure must not suppress the visible greeting.
                    pass
        if self.recovery_message:
            append(
                self.controller.presenter.roby_message(self.recovery_message).render()
            )
        for message in self.startup_messages():
            append(message.render())
        entry.focus_set()
        root.mainloop()
