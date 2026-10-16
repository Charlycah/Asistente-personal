import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from infrastructure.config.config_schema import (
    AppConfig,
    AssistantConfig,
    LLMConfig,
    MemoryConfig,
    RemindersConfig,
    SecretsConfig,
    VoiceConfig,
    WeatherConfig,
)
from infrastructure.config.exceptions import (
    ConfigFileNotFoundError,
    InvalidConfigError,
)
from infrastructure.config.secrets_loader import SecretsLoader


class SettingsLoader:
    """
    Carga configuración profesional en dos capas:

    1. config.example.json: contrato base del proyecto, requerido.
    2. config.local.json: overrides locales, opcional.

    Los secretos viven en .roby/credentials.json o en variables de entorno explícitas.
    """

    def __init__(
        self,
        config_path: str = "config.example.json",
        credentials_path: str | None = None,
        local_config_path: str = "config.local.json",
    ):
        self.config_path = Path(config_path)
        self.local_config_path = Path(local_config_path)
        self.secrets_loader = SecretsLoader(credentials_path)

    def load(self) -> AppConfig:
        raw_config = self._load_json(self.config_path, required=True)

        if (
            self.local_config_path.exists()
            and self.local_config_path != self.config_path
        ):
            local_config = self._load_json(self.local_config_path, required=False)
            raw_config = self._deep_merge(raw_config, local_config)

        return self._build_app_config(raw_config)

    def _build_app_config(self, raw_config: dict[str, Any]) -> AppConfig:
        try:
            return AppConfig(
                assistant=AssistantConfig(
                    name=raw_config["assistant"]["name"],
                    language=raw_config["assistant"]["language"],
                    timezone=raw_config["assistant"]["timezone"],
                ),
                weather=WeatherConfig(
                    default_city=raw_config["weather"]["default_city"],
                    provider=raw_config["weather"]["provider"],
                    extended_provider=raw_config["weather"]["extended_provider"],
                ),
                memory=MemoryConfig(
                    enabled=raw_config["memory"]["enabled"],
                    database_path=raw_config["memory"]["database_path"],
                ),
                reminders=RemindersConfig(
                    enabled=raw_config["reminders"]["enabled"],
                    check_interval_seconds=raw_config["reminders"][
                        "check_interval_seconds"
                    ],
                ),
                llm=LLMConfig(
                    provider=raw_config["llm"]["provider"],
                    model=raw_config["llm"]["model"],
                ),
                voice=VoiceConfig(
                    enabled=raw_config["voice"]["enabled"],
                    tts_provider=raw_config["voice"]["tts_provider"],
                    stt_provider=raw_config["voice"]["stt_provider"],
                ),
                secrets=SecretsConfig(
                    openweather_api_key=self.secrets_loader.get("OPENWEATHER_API_KEY"),
                    weatherapi_key=self.secrets_loader.get("WEATHERAPI_KEY"),
                    google_client_secret_file=self.secrets_loader.get(
                        "GOOGLE_CLIENT_SECRET_FILE"
                    ),
                    google_token_file=self.secrets_loader.get("GOOGLE_TOKEN_FILE"),
                    gmail_address=self.secrets_loader.get("GMAIL_ADDRESS"),
                    gmail_app_password=self.secrets_loader.get("GMAIL_APP_PASSWORD"),
                    gemini_api_key=self.secrets_loader.get("GEMINI_API_KEY"),
                    openrouter_api_key=self.secrets_loader.get("OPENROUTER_API_KEY"),
                    mistral_api_key=self.secrets_loader.get("MISTRAL_API_KEY"),
                    openai_api_key=self.secrets_loader.get("OPENAI_API_KEY"),
                    camera_index=self._get_int_secret("CAMERA_INDEX", default=0),
                ),
                debug=raw_config.get("debug", False),
            )
        except KeyError as exc:
            raise InvalidConfigError(
                f"Falta clave obligatoria de configuración: {exc}"
            ) from exc
        except TypeError as exc:
            raise InvalidConfigError(
                "La configuración debe ser un objeto JSON válido."
            ) from exc

    def _get_int_secret(self, key: str, *, default: int) -> int:
        raw_value = self.secrets_loader.get(key)
        if raw_value is None or raw_value == "":
            return default
        try:
            return int(raw_value)
        except ValueError as exc:
            raise InvalidConfigError(
                f"La credencial {key} debe ser un entero."
            ) from exc

    def _load_json(self, path: Path, *, required: bool) -> dict[str, Any]:
        if not path.exists():
            if required:
                raise ConfigFileNotFoundError(
                    f"No existe el archivo de configuración base: {path}"
                )
            return {}

        try:
            with path.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except json.JSONDecodeError as exc:
            raise InvalidConfigError(f"JSON inválido en {path}: {exc}") from exc

        if not isinstance(data, dict):
            raise InvalidConfigError(
                f"La configuración en {path} debe ser un objeto JSON."
            )

        return data

    def _deep_merge(
        self,
        base: dict[str, Any],
        override: dict[str, Any],
    ) -> dict[str, Any]:
        result = deepcopy(base)

        for key, value in override.items():
            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value

        return result
