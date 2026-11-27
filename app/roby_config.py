from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from app.runtime_bootstrap_contract import OFFICIAL_RUNTIME_FACTORY

DEFAULT_CONFIG_PATH = Path(".roby/config.json")
LEGACY_CONFIG_PATH = Path(".hal/config.json")


@dataclass(frozen=True)
class RobyConfigLoadResult:
    path: Path
    data: dict[str, Any]
    created: bool = False




def resolve_roby_config_path(path: Path = DEFAULT_CONFIG_PATH) -> Path:
    """Resolve the canonical ROBY config independently of launch directory."""
    expanded = path.expanduser()
    if expanded != DEFAULT_CONFIG_PATH:
        return expanded

    configured = os.getenv("ROBY_HOME", "").strip()
    if configured:
        return Path(configured).expanduser().resolve() / DEFAULT_CONFIG_PATH

    project_root = Path(__file__).resolve().parents[1]
    cwd_candidate = Path.cwd() / DEFAULT_CONFIG_PATH
    if cwd_candidate.is_file():
        return cwd_candidate.resolve()
    return project_root / DEFAULT_CONFIG_PATH


DEFAULT_CONFIG: dict[str, Any] = {
    "version": 1,
    "assistant": {"name": "Roby", "aliases": []},
    "household": {
        "owners": ["Carlos", "Cristina"],
        "city": "Buenos Aires",
        "timezone": "America/Argentina/Buenos_Aires",
        "language": "es",
    },
    "runtime": {
        "factory": OFFICIAL_RUNTIME_FACTORY,
        "profile": "carlos-cristina",
        "session": "coowners-main",
    },
    "providers": {
        "default": "local",
        "allow_remote_fallback": False,
        "local": {
            "enabled": True,
            "name": "local-openai",
            "endpoint": "http://127.0.0.1:11434/v1",
            "model": "llama3:latest",
            "timeout_seconds": 120,
        },
        "gemini": {
            "enabled": False,
            "endpoint": "https://generativelanguage.googleapis.com/v1beta",
            "model": "gemini-2.5-flash",
        },
        "mistral": {
            "enabled": False,
            "endpoint": "https://api.mistral.ai/v1/chat/completions",
            "model": "mistral-small-latest",
        },
    },
    "services": {
        "weather": {"enabled": False, "provider": "openweather", "units": "metric"},
        "gmail": {"enabled": False, "allow_interactive_oauth": True},
        "wikimedia_commons": {
            "enabled": True,
            "user_agent": (
                "ROBY-XI.2/1.0 (https://github.com/Charlycah/Asistente-personal)"
            ),
        },
        "voice": {
            "enabled": True,
            "provider": "edge-tts",
            "profile": "casual_female",
            "voice": "",
            "rate": "",
            "pitch": "",
            "volume": "",
            "continuous_listening": {
                "enabled": True,
                "language": "es-AR",
                "wake_word": "roby",
                "ambient_comments": False,
                "comment_cooldown_seconds": 90,
                "utterance_timeout_seconds": 8,
                "audio_backend": "powershell",
                "vosk_model_path": ".roby/models/vosk-es",
                "input_device": "",
                "sample_rate": 16000,
                "block_size": 3200,
                "silence_threshold": 180,
                "voice_threshold": 380,
                "auto_calibrate": True,
                "calibration_seconds": 1.5,
                "noise_multiplier": 2.2,
                "normalize_audio": True,
                "target_peak": 14000,
                "max_gain": 4.0,
                "partial_results": True,
                "partial_finalize_ms": 1200,
                "vad_enabled": True,
                "vad_aggressiveness": 2,
                "pre_roll_ms": 300,
                "end_silence_ms": 650,
                "min_speech_ms": 250,
                "max_utterance_seconds": 12,
                "recalibration_silence_seconds": 5,
                "zcr_min": 0.005,
                "zcr_max": 0.35,
                "active_window_seconds": 30,
                "min_command_words": 2,
                "wake_aliases": "roby,robi,robby,robbie,ruby,rubi",
                "diagnostic_mode": False,
            },
        },
        "camera": {"enabled": False},
    },
    "privacy": {
        "require_confirmation_for_remote_private_content": True,
        "ambient_audio_consent": False,
        "ambient_camera_consent": False,
    },
    "environment": {},
}


def load_roby_config(path: Path = DEFAULT_CONFIG_PATH) -> RobyConfigLoadResult:
    path = path.expanduser()
    migrated_from_legacy = False
    source_path = path
    if (
        not path.exists()
        and path == DEFAULT_CONFIG_PATH
        and LEGACY_CONFIG_PATH.exists()
    ):
        source_path = LEGACY_CONFIG_PATH
        migrated_from_legacy = True
    if not source_path.exists():
        data = _deep_copy(DEFAULT_CONFIG)
        save_roby_config(data, path)
        return RobyConfigLoadResult(path=path, data=data, created=True)

    try:
        raw = json.loads(source_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Configuración inválida en {source_path}: línea {exc.lineno}, "
            f"columna {exc.colno}"
        ) from exc
    if not isinstance(raw, dict):
        raise ValueError(
            f"La configuración de Roby en {source_path} debe ser un objeto JSON."
        )

    migrated = _migrate_legacy_config(raw)
    migrated = _normalize_roby_identity(migrated)
    data = _merge(_deep_copy(DEFAULT_CONFIG), migrated)
    validate_roby_config(data)
    if data != raw or migrated_from_legacy:
        save_roby_config(data, path)
    return RobyConfigLoadResult(path=path, data=data, created=migrated_from_legacy)


def save_roby_config(data: Mapping[str, Any], path: Path = DEFAULT_CONFIG_PATH) -> None:
    path = path.expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(dict(data), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def validate_roby_config(data: Mapping[str, Any]) -> None:
    provider = _mapping(data, "providers")
    local = _mapping(provider, "local")
    endpoint = str(local.get("endpoint", "")).strip()
    model = str(local.get("model", "")).strip()
    if not endpoint.startswith(("http://", "https://")):
        raise ValueError("providers.local.endpoint debe ser una URL HTTP válida.")
    if not model:
        raise ValueError("providers.local.model no puede estar vacío.")


def activate_roby_config(
    path: Path = DEFAULT_CONFIG_PATH,
    *,
    override_existing: bool = False,
) -> RobyConfigLoadResult:
    """Load the local JSON configuration for this process.

    Existing composition modules consume process settings through this compatibility
    adapter. Configuration and credentials remain stored in separate local JSON files.
    """
    result = load_roby_config(path)
    values = environment_values(result.data)
    for name, value in values.items():
        if override_existing or not os.environ.get(name, "").strip():
            os.environ[name] = value
    return result


def environment_values(data: Mapping[str, Any]) -> dict[str, str]:
    household = _mapping(data, "household")
    runtime = _mapping(data, "runtime")
    providers = _mapping(data, "providers")
    local = _mapping(providers, "local")
    gemini = _mapping(providers, "gemini")
    mistral = _mapping(providers, "mistral")
    services = _mapping(data, "services")
    weather = _mapping(services, "weather")
    gmail = _mapping(services, "gmail")
    wikimedia_commons = _mapping(services, "wikimedia_commons")
    voice = _mapping(services, "voice")
    camera = _mapping(services, "camera")
    privacy = _mapping(data, "privacy")
    continuous_listening = _mapping(voice, "continuous_listening")

    values = {
        "ROBY_WIKIMEDIA_COMMONS_ENABLED": _bool_text(
            wikimedia_commons.get("enabled", True)
        ),
        "ROBY_WIKIMEDIA_COMMONS_USER_AGENT": str(
            wikimedia_commons.get(
                "user_agent",
                DEFAULT_CONFIG["services"]["wikimedia_commons"]["user_agent"],
            )
        ),
        "ROBY_RUNTIME_ROOT_FACTORY": str(
            runtime.get("factory", OFFICIAL_RUNTIME_FACTORY)
        ),
        "ROBY_RUNTIME_OWNER": "Carlos y Cristina",
        "ROBY_DEFAULT_CITY": str(household.get("city", "Buenos Aires")),
        "ROBY_HOUSEHOLD_TIMEZONE": str(
            household.get("timezone", "America/Argentina/Buenos_Aires")
        ),
        "ROBY_WIKIPEDIA_LANGUAGE": str(household.get("language", "es")),
        "ROBY_LOCAL_PROVIDER_NAME": str(local.get("name", "local-openai")),
        "ROBY_LOCAL_PROVIDER_ENDPOINT": str(
            local.get("endpoint", "http://127.0.0.1:11434/v1")
        ),
        "ROBY_LOCAL_PROVIDER_MODEL": str(local.get("model", "llama3:latest")),
        "ROBY_LOCAL_PROVIDER_TIMEOUT_SECONDS": str(local.get("timeout_seconds", 120)),
        "ROBY_LLM_PROVIDER": str(providers.get("default", "local")),
        "ROBY_GEMINI_ENABLED": _bool_text(gemini.get("enabled", False)),
        "ROBY_GEMINI_ENDPOINT": str(gemini.get("endpoint", "")),
        "ROBY_GEMINI_MODEL": str(gemini.get("model", "gemini-2.5-flash")),
        "ROBY_MISTRAL_ENABLED": _bool_text(mistral.get("enabled", False)),
        "ROBY_MISTRAL_ENDPOINT": str(mistral.get("endpoint", "")),
        "ROBY_MISTRAL_MODEL": str(mistral.get("model", "mistral-small-latest")),
        "ROBY_WEATHER_ENABLED": _bool_text(weather.get("enabled", False)),
        "ROBY_GMAIL_ENABLED": _bool_text(gmail.get("enabled", False)),
        "ROBY_GMAIL_ALLOW_INTERACTIVE_OAUTH": _bool_text(
            gmail.get("allow_interactive_oauth", True)
        ),
        "ROBY_VOICE_ENABLED": _bool_text(voice.get("enabled", False)),
        "ROBY_VOICE_PROVIDER": str(voice.get("provider", "edge-tts")),
        "ROBY_VOICE_PROFILE": str(voice.get("profile", "casual_female")),
        "ROBY_EDGE_TTS_VOICE": str(voice.get("voice", "")),
        "ROBY_EDGE_TTS_RATE": str(voice.get("rate", "")),
        "ROBY_EDGE_TTS_PITCH": str(voice.get("pitch", "")),
        "ROBY_EDGE_TTS_VOLUME": str(voice.get("volume", "")),
        "ROBY_CONTINUOUS_LISTENING_ENABLED": _bool_text(
            continuous_listening.get("enabled", False)
        ),
        "ROBY_SPEECH_LANGUAGE": str(continuous_listening.get("language", "es-AR")),
        "ROBY_VOICE_WAKE_WORD": str(continuous_listening.get("wake_word", "roby")),
        "ROBY_AMBIENT_COMMENTS_ENABLED": _bool_text(
            continuous_listening.get("ambient_comments", False)
        ),
        "ROBY_AMBIENT_COMMENT_COOLDOWN_SECONDS": str(
            continuous_listening.get("comment_cooldown_seconds", 90)
        ),
        "ROBY_LISTEN_UTTERANCE_TIMEOUT_SECONDS": str(
            continuous_listening.get("utterance_timeout_seconds", 8)
        ),
        "ROBY_AUDIO_BACKEND": str(
            continuous_listening.get("audio_backend", "powershell")
        ),
        "ROBY_VOSK_MODEL_PATH": str(
            continuous_listening.get("vosk_model_path", ".roby/models/vosk-es")
        ),
        "ROBY_AUDIO_INPUT_DEVICE": str(
            continuous_listening.get("input_device", "")
        ),
        "ROBY_AUDIO_SAMPLE_RATE": str(
            continuous_listening.get("sample_rate", 16000)
        ),
        "ROBY_AUDIO_BLOCK_SIZE": str(
            continuous_listening.get("block_size", 3200)
        ),
        "ROBY_AUDIO_SILENCE_THRESHOLD": str(
            continuous_listening.get("silence_threshold", 180)
        ),
        "ROBY_AUDIO_VOICE_THRESHOLD": str(
            continuous_listening.get("voice_threshold", 380)
        ),
        "ROBY_AUDIO_AUTO_CALIBRATE": _bool_text(
            continuous_listening.get("auto_calibrate", True)
        ),
        "ROBY_AUDIO_CALIBRATION_SECONDS": str(
            continuous_listening.get("calibration_seconds", 1.5)
        ),
        "ROBY_AUDIO_NOISE_MULTIPLIER": str(
            continuous_listening.get("noise_multiplier", 2.2)
        ),
        "ROBY_AUDIO_NORMALIZE": _bool_text(
            continuous_listening.get("normalize_audio", True)
        ),
        "ROBY_AUDIO_TARGET_PEAK": str(
            continuous_listening.get("target_peak", 14000)
        ),
        "ROBY_AUDIO_MAX_GAIN": str(
            continuous_listening.get("max_gain", 4.0)
        ),
        "ROBY_AUDIO_PARTIAL_RESULTS": _bool_text(
            continuous_listening.get("partial_results", True)
        ),
        "ROBY_AUDIO_PARTIAL_FINALIZE_MS": str(
            continuous_listening.get("partial_finalize_ms", 1200)
        ),
        "ROBY_AUDIO_VAD_ENABLED": _bool_text(
            continuous_listening.get("vad_enabled", True)
        ),
        "ROBY_AUDIO_VAD_AGGRESSIVENESS": str(
            continuous_listening.get("vad_aggressiveness", 2)
        ),
        "ROBY_AUDIO_PRE_ROLL_MS": str(
            continuous_listening.get("pre_roll_ms", 300)
        ),
        "ROBY_AUDIO_END_SILENCE_MS": str(
            continuous_listening.get("end_silence_ms", 650)
        ),
        "ROBY_AUDIO_MIN_SPEECH_MS": str(
            continuous_listening.get("min_speech_ms", 250)
        ),
        "ROBY_AUDIO_MAX_UTTERANCE_SECONDS": str(
            continuous_listening.get("max_utterance_seconds", 12)
        ),
        "ROBY_AUDIO_RECALIBRATION_SILENCE_SECONDS": str(
            continuous_listening.get("recalibration_silence_seconds", 5)
        ),
        "ROBY_AUDIO_ZCR_MIN": str(
            continuous_listening.get("zcr_min", 0.005)
        ),
        "ROBY_AUDIO_ZCR_MAX": str(
            continuous_listening.get("zcr_max", 0.35)
        ),
        "ROBY_AUDIO_DIAGNOSTIC_MODE": _bool_text(
            continuous_listening.get("diagnostic_mode", False)
        ),
        "ROBY_VOICE_ACTIVE_WINDOW_SECONDS": str(
            continuous_listening.get("active_window_seconds", 30)
        ),
        "ROBY_VOICE_WAKE_ALIASES": str(
            continuous_listening.get(
                "wake_aliases", "roby,robi,robby,robbie,ruby,rubi"
            )
        ),
        "ROBY_VOICE_MIN_COMMAND_WORDS": str(
            continuous_listening.get("min_command_words", 2)
        ),
        "ROBY_VOICE_REQUIRE_WAKE_WORD": _bool_text(
            continuous_listening.get("require_wake_word", False)
        ),
        "ROBY_CAMERA_ENABLED": _bool_text(camera.get("enabled", False)),
        "ROBY_AMBIENT_AUDIO_CONSENT": _bool_text(
            privacy.get("ambient_audio_consent", False)
        ),
        "ROBY_AMBIENT_CAMERA_CONSENT": _bool_text(
            privacy.get("ambient_camera_consent", False)
        ),
    }
    extra = data.get("environment", {})
    if isinstance(extra, dict):
        for name, value in extra.items():
            if isinstance(name, str) and name.startswith("ROBY_") and value is not None:
                values[name] = _scalar_text(value)
    optional_false_flags = {
        "ROBY_GEMINI_ENABLED",
        "ROBY_MISTRAL_ENABLED",
        "ROBY_WEATHER_ENABLED",
        "ROBY_GMAIL_ENABLED",
        "ROBY_VOICE_ENABLED",
        "ROBY_CONTINUOUS_LISTENING_ENABLED",
        "ROBY_AMBIENT_COMMENTS_ENABLED",
        "ROBY_CAMERA_ENABLED",
        "ROBY_AMBIENT_AUDIO_CONSENT",
        "ROBY_AMBIENT_CAMERA_CONSENT",
    }
    return {
        name: value
        for name, value in values.items()
        if value.strip() and not (name in optional_false_flags and value == "false")
    }


def _migrate_legacy_config(raw: dict[str, Any]) -> dict[str, Any]:
    if "providers" in raw or "runtime" in raw or "household" in raw:
        return raw
    migrated = _deep_copy(DEFAULT_CONFIG)
    household = migrated["household"]
    local = migrated["providers"]["local"]
    household["city"] = raw.get("ciudad_predeterminada") or household["city"]
    household["language"] = raw.get("idioma_wikipedia") or household["language"]
    local["model"] = raw.get("modelo_ollama") or local["model"]
    # Legacy plaintext secrets are deliberately not migrated.
    return migrated


def _normalize_roby_identity(data: dict[str, Any]) -> dict[str, Any]:
    normalized = _deep_copy(data)
    household = normalized.setdefault("household", {})
    if isinstance(household, dict):
        household.pop("owner", None)
        household["owners"] = ["Carlos", "Cristina"]
    runtime = normalized.setdefault("runtime", {})
    if isinstance(runtime, dict):
        runtime["profile"] = "carlos-cristina"
        runtime["session"] = "coowners-main"
    assistant = normalized.setdefault("assistant", {})
    if isinstance(assistant, dict):
        assistant["name"] = "Roby"
        assistant["aliases"] = []
    services = normalized.get("services", {})
    if isinstance(services, dict):
        voice = services.get("voice", {})
        if isinstance(voice, dict):
            listening = voice.get("continuous_listening", {})
            if isinstance(listening, dict):
                listening["wake_word"] = "roby"
    return normalized


def _mapping(data: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    value = data.get(key, {})
    return value if isinstance(value, Mapping) else {}


def _merge(base: dict[str, Any], overlay: Mapping[str, Any]) -> dict[str, Any]:
    for key, value in overlay.items():
        if isinstance(value, Mapping) and isinstance(base.get(key), dict):
            _merge(base[key], value)
        else:
            base[key] = value
    return base


def _deep_copy(value: Mapping[str, Any]) -> dict[str, Any]:
    return json.loads(json.dumps(value))


def _bool_text(value: Any) -> str:
    return "true" if bool(value) else "false"


def _scalar_text(value: Any) -> str:
    if isinstance(value, bool):
        return _bool_text(value)
    return str(value)
