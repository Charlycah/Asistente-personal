from __future__ import annotations

import os
from pathlib import Path

from application.reminders import ReminderConversationService
from core.document_inbox import DocumentInboxManager
from core.memory_runtime_integration import (
    MemoryRuntimeConfig,
    MemoryRuntimeIntegration,
)
from core.personal_knowledge_base import KnowledgeOwner, PersonalKnowledgeBaseManager
from core.task_intelligence import TaskIntelligenceManager
from infrastructure.calendar.calendar_runtime_composition import (
    CalendarRuntimeComposition,
)
from infrastructure.calendar.calendar_runtime_composition import (
    build_calendar_runtime_from_environment as build_calendar_runtime,
)
from infrastructure.camera.camera_adapter import build_camera_adapter_from_config
from infrastructure.camera.camera_client import OpenCVCameraClient
from infrastructure.config.secrets_loader import SecretsLoader
from infrastructure.config.settings_loader import SettingsLoader
from infrastructure.mail.gmail_runtime_composition import (
    GmailRuntimeComposition,
    GmailRuntimeConfig,
)
from infrastructure.mail.mail_adapter import (
    build_mail_reader_adapter_from_credentials,
)
from infrastructure.maps import (
    DesktopMapPresenter,
    FoliumMapRenderer,
    NominatimGeocodingAdapter,
    NominatimGeocodingConfig,
)
from infrastructure.repositories.sqlite_document_repository import (
    SQLiteDocumentRepository,
)
from infrastructure.repositories.sqlite_personal_knowledge_repository import (
    SQLitePersonalKnowledgeRepository,
)
from infrastructure.repositories.sqlite_task_repository import SQLiteTaskRepository
from infrastructure.vision import (
    OpenCVCascadeFaceDetector,
    OpenCVHOGPersonDetector,
    PyzbarVisualCodeDecoder,
    TesseractTextExtractor,
)
from infrastructure.vision.file_image_repository import FileImageRepository
from infrastructure.weather.weather_adapter import WeatherAdapter, WeatherAdapterPolicy
from infrastructure.weather.weather_client import OpenWeatherMapClient

from .foursquare_governed_source import FoursquareGovernedSourceAdapter
from .household_goals import HouseholdGoalService
from .household_knowledge import HouseholdKnowledgeService
from .household_projects import HouseholdProjectService
from .map_conversation_runtime import (
    MapConversationInterceptionPort,
    MapConversationPolicy,
)
from .runtime_environment_ports import (
    HouseholdGoalConversationInterceptionPort,
    HouseholdKnowledgeConversationInterceptionPort,
    HouseholdProjectConversationInterceptionPort,
    PersonalKnowledgeConversationInterceptionPort,
    ReminderConversationInterceptionPort,
    TaskIntelligenceConversationInterceptionPort,
)
from .unified_runtime_integration import (
    CameraConversationInterceptionPort,
    MailReaderConversationInterceptionPort,
    MailUnavailableConversationInterceptionPort,
    VoiceRuntimeConversationInterceptionPort,
)
from .vision_core import OfficialVisionCore
from .vision_gateway import GovernedVisionGateway
from .voice_input import (
    LocalCommandVoiceInput,
    LocalCommandVoiceInputConfig,
    VoiceRequestTranscriber,
)
from .voice_output import (
    LocalCommandVoiceConfig,
    LocalCommandVoiceOutput,
    VoiceResponseReader,
    build_voice_output_from_environment,
)
from .weather_conversation_runtime import (
    WeatherConversationInterceptionPort,
    WeatherUnavailableConversationInterceptionPort,
)
from .wikimedia_commons_governed_source import (
    WikimediaCommonsGovernedSourceAdapter,
)

_TRUE_VALUES = frozenset({"1", "true", "yes", "on"})


def environment_flag(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().casefold() in _TRUE_VALUES


def build_household_goals_from_environment():
    if not environment_flag("ROBY_HOUSEHOLD_GOALS_ENABLED", default=True):
        return None
    return HouseholdGoalConversationInterceptionPort(
        HouseholdGoalService(
            os.getenv("ROBY_HOUSEHOLD_GOALS_DB_PATH", ".roby/household_goals.db")
        )
    )


def build_household_projects_from_environment():
    if not environment_flag("ROBY_HOUSEHOLD_PROJECTS_ENABLED", default=True):
        return None
    return HouseholdProjectConversationInterceptionPort(
        HouseholdProjectService(
            os.getenv("ROBY_HOUSEHOLD_PROJECTS_DB_PATH", ".roby/household_projects.db")
        )
    )


def build_household_knowledge_from_environment():
    if not environment_flag("ROBY_HOUSEHOLD_KNOWLEDGE_ENABLED", default=True):
        return None
    return HouseholdKnowledgeConversationInterceptionPort(
        HouseholdKnowledgeService(
            os.getenv(
                "ROBY_HOUSEHOLD_KNOWLEDGE_DB_PATH", ".roby/household_knowledge.db"
            )
        )
    )


def build_reminder_conversation_from_environment():
    if not environment_flag("ROBY_REMINDER_CONVERSATION_ENABLED", default=True):
        return None
    return ReminderConversationInterceptionPort(
        ReminderConversationService(
            os.getenv("ROBY_REMINDER_DB_PATH", ".roby/reminders.db"),
            routines_enabled=environment_flag(
                "ROBY_HOUSEHOLD_ROUTINES_ENABLED", default=True
            ),
        )
    )


def build_vision_gateway_from_environment():
    """Provision the existing governed vision boundary with private storage."""

    repository = FileImageRepository(
        Path(os.getenv("ROBY_VISUAL_COLLECTION_ROOT", ".roby/visual_collection"))
    )
    return GovernedVisionGateway(
        vision_core=OfficialVisionCore(
            camera_provider=OpenCVCameraClient(),
            person_detector=OpenCVHOGPersonDetector(),
            face_detector=OpenCVCascadeFaceDetector(),
            text_extractor=TesseractTextExtractor(),
            visual_code_decoder=PyzbarVisualCodeDecoder(),
        ),
        image_repository=repository,
    )


def build_document_inbox_from_environment():
    if not environment_flag("ROBY_DOCUMENT_INBOX_ENABLED", default=True):
        return None
    repository = SQLiteDocumentRepository(
        os.getenv("ROBY_DOCUMENT_INBOX_DB_PATH", ".roby/documents.db")
    )
    return DocumentInboxManager(repository=repository)


def build_personal_knowledge_from_environment(
    document_inbox: DocumentInboxManager | None = None,
):
    if not environment_flag("ROBY_PERSONAL_KNOWLEDGE_ENABLED", default=True):
        return None
    repository = SQLitePersonalKnowledgeRepository(
        os.getenv("ROBY_PERSONAL_KNOWLEDGE_DB_PATH", ".roby/personal_knowledge.db")
    )
    owner_name = os.getenv("ROBY_RUNTIME_OWNER", "Carlos").strip().casefold()
    owner = (
        KnowledgeOwner.PARTNER if owner_name == "cristina" else KnowledgeOwner.CARLOS
    )
    return PersonalKnowledgeConversationInterceptionPort(
        PersonalKnowledgeBaseManager(
            repository=repository,
            document_inbox=document_inbox,
        ),
        owner=owner,
    )


def build_task_intelligence_from_environment(
    document_inbox: DocumentInboxManager | None = None,
):
    if not environment_flag("ROBY_TASK_INTELLIGENCE_ENABLED", default=True):
        return None
    repository = SQLiteTaskRepository(os.getenv("ROBY_TASK_DB_PATH", ".roby/tasks.db"))
    return TaskIntelligenceConversationInterceptionPort(
        TaskIntelligenceManager(
            repository=repository,
            document_inbox=document_inbox,
        )
    )


def build_memory_runtime_from_environment() -> MemoryRuntimeIntegration | None:
    if not environment_flag("ROBY_PERSONAL_MEMORY_ENABLED", default=True):
        return None
    return MemoryRuntimeIntegration(
        MemoryRuntimeConfig(
            root_path=os.getenv("ROBY_PERSONAL_MEMORY_PATH", ".roby/memory"),
            recall_limit=int(os.getenv("ROBY_PERSONAL_MEMORY_RECALL_LIMIT", "5")),
            enable_recall=environment_flag(
                "ROBY_PERSONAL_MEMORY_RECALL_ENABLED", default=True
            ),
            enable_learning=environment_flag(
                "ROBY_PERSONAL_MEMORY_LEARNING_ENABLED", default=True
            ),
            include_shared=False,
            canonical_joint_owner=True,
        )
    )


def build_foursquare_governed_source_from_environment(
    *,
    transport=None,
):
    if not environment_flag("ROBY_FOURSQUARE_PLACES_ENABLED"):
        return None
    try:
        credential = SecretsLoader().get("FOURSQUARE_SERVICE_API_KEY")
        if not credential or not credential.strip():
            return None
        return FoursquareGovernedSourceAdapter(
            api_key=credential,
            transport=transport,
        )
    except (OSError, RuntimeError, ValueError):
        return None


def build_wikimedia_commons_governed_source_from_environment(
    *,
    transport=None,
):
    if not environment_flag("ROBY_WIKIMEDIA_COMMONS_ENABLED"):
        return None
    try:
        user_agent = os.getenv("ROBY_WIKIMEDIA_COMMONS_USER_AGENT")
        if not user_agent or not user_agent.strip():
            return None
        return WikimediaCommonsGovernedSourceAdapter(
            user_agent=user_agent,
            transport=transport,
        )
    except (OSError, RuntimeError, ValueError):
        return None


def build_weather_conversation_from_environment():
    if not environment_flag("ROBY_WEATHER_ENABLED", default=True):
        return WeatherUnavailableConversationInterceptionPort("disabled")
    try:
        city = os.getenv("ROBY_DEFAULT_CITY", "Buenos Aires").strip()
        api_key = SecretsLoader().get("OPENWEATHER_API_KEY")
        if not api_key:
            return WeatherUnavailableConversationInterceptionPort("missing_credentials")
        adapter = WeatherAdapter(
            OpenWeatherMapClient(api_key),
            WeatherAdapterPolicy(default_location=city or "Buenos Aires"),
        )
    except (OSError, RuntimeError, ValueError):
        return WeatherUnavailableConversationInterceptionPort("configuration_error")
    return WeatherConversationInterceptionPort(adapter)


def build_map_conversation_from_environment():
    if not environment_flag("ROBY_MAPS_ENABLED", default=True):
        return None
    try:
        owner = os.getenv("ROBY_RUNTIME_OWNER", "Carlos")
        user_agent = os.getenv(
            "ROBY_NOMINATIM_USER_AGENT",
            "ROBY-XI.2/325.12 (local desktop assistant)",
        )
        geocoder = NominatimGeocodingAdapter(
            NominatimGeocodingConfig(user_agent=user_agent)
        )
        return MapConversationInterceptionPort(
            geocoder=geocoder,
            renderer=FoliumMapRenderer(),
            presenter=DesktopMapPresenter(),
            policy=MapConversationPolicy(owner=owner),
        )
    except (OSError, RuntimeError, ValueError):
        return None


def _command_from_environment(name: str) -> tuple[str, ...]:
    raw = os.getenv(name, "").strip()
    return tuple(part for part in raw.split() if part)


def build_mail_reader_conversation_from_environment():
    # ROBY_MAIL_READER_ENABLED is canonical. ROBY_MAIL_ENABLED remains a legacy
    # fallback only when the canonical switch is absent.
    if os.getenv("ROBY_MAIL_READER_ENABLED") is None:
        enabled = environment_flag("ROBY_MAIL_ENABLED", default=True)
    else:
        enabled = environment_flag("ROBY_MAIL_READER_ENABLED")
    if not enabled:
        return MailUnavailableConversationInterceptionPort("disabled")
    try:
        secrets = SecretsLoader()
        adapter = build_mail_reader_adapter_from_credentials(
            address=secrets.get("GMAIL_ADDRESS"),
            password=secrets.get("GMAIL_APP_PASSWORD"),
        )
    except (OSError, RuntimeError, ValueError):
        return MailUnavailableConversationInterceptionPort("not_configured")
    return MailReaderConversationInterceptionPort(adapter)


def build_camera_conversation_from_environment():
    if not environment_flag("ROBY_CAMERA_ENABLED"):
        return None
    try:
        adapter = build_camera_adapter_from_config(SettingsLoader().load())
    except (OSError, RuntimeError, ValueError):
        return None
    return CameraConversationInterceptionPort(adapter)


def build_voice_runtime_from_environment():
    input_command = _command_from_environment("ROBY_VOICE_INPUT_COMMAND")
    output_command = _command_from_environment("ROBY_VOICE_OUTPUT_COMMAND")
    if not input_command and not output_command:
        return None
    transcriber = VoiceRequestTranscriber(
        LocalCommandVoiceInput(LocalCommandVoiceInputConfig(input_command))
        if input_command
        else None
    )
    reader = VoiceResponseReader(
        LocalCommandVoiceOutput(LocalCommandVoiceConfig(output_command))
        if output_command
        else build_voice_output_from_environment()
    )
    from .ui_adapter import UIResponse

    return VoiceRuntimeConversationInterceptionPort(
        transcriber=transcriber,
        response_reader=reader,
        response_factory=lambda text: UIResponse(text=text, status="success"),
    )


def build_calendar_runtime_from_environment() -> CalendarRuntimeComposition:
    """Build the controlled Google Calendar runtime from canonical settings."""
    return build_calendar_runtime()


def build_gmail_runtime_from_environment() -> GmailRuntimeComposition:
    """Build a secret-free Gmail runtime shell from environment feature flags."""
    return GmailRuntimeComposition(
        config=GmailRuntimeConfig(enabled=environment_flag("ROBY_GMAIL_ENABLED"))
    )
