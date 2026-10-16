from dataclasses import dataclass


@dataclass(frozen=True)
class AssistantConfig:
    name: str
    language: str
    timezone: str


@dataclass(frozen=True)
class WeatherConfig:
    default_city: str
    provider: str
    extended_provider: str


@dataclass(frozen=True)
class MemoryConfig:
    enabled: bool
    database_path: str


@dataclass(frozen=True)
class RemindersConfig:
    enabled: bool
    check_interval_seconds: int


@dataclass(frozen=True)
class LLMConfig:
    provider: str
    model: str


@dataclass(frozen=True)
class VoiceConfig:
    enabled: bool
    tts_provider: str
    stt_provider: str


@dataclass(frozen=True)
class SecretsConfig:
    openweather_api_key: str | None
    weatherapi_key: str | None
    google_client_secret_file: str | None
    google_token_file: str | None
    gmail_address: str | None
    gmail_app_password: str | None
    gemini_api_key: str | None
    openrouter_api_key: str | None
    mistral_api_key: str | None
    openai_api_key: str | None
    camera_index: int


@dataclass(frozen=True)
class AppConfig:
    assistant: AssistantConfig
    weather: WeatherConfig
    memory: MemoryConfig
    reminders: RemindersConfig
    llm: LLMConfig
    voice: VoiceConfig
    secrets: SecretsConfig
    debug: bool
