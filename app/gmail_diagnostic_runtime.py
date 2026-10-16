from __future__ import annotations

import importlib.util
import json
import os
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from types import MappingProxyType
from typing import Mapping

from infrastructure.mail.google_oauth_deployment_adapter import (
    resolve_google_client_secrets_path,
)

_TRUE = {"1", "true", "yes", "on"}
_REQUIRED_SCOPE = "https://www.googleapis.com/auth/gmail.readonly"


class GmailDiagnosticState(str, Enum):
    READY = "ready"
    DEGRADED = "degraded"
    DISABLED = "disabled"


class GmailDiagnosticTraceState(str, Enum):
    OK = "ok"
    FAILED = "failed"
    NOT_EXECUTED = "not_executed"
    DISABLED = "disabled"


@dataclass(frozen=True)
class GmailDiagnosticTraceStage:
    ordinal: int
    total: int
    key: str
    label: str
    state: GmailDiagnosticTraceState

    def to_dict(self) -> Mapping[str, object]:
        return MappingProxyType(
            {
                "ordinal": self.ordinal,
                "total": self.total,
                "key": self.key,
                "label": self.label,
                "state": self.state.value,
            }
        )

    def console_line(self) -> str:
        return (
            f"GMAIL TRACE> {self.ordinal}/{self.total} "
            f"{self.label}: {self.state.value.upper()}"
        )


@dataclass(frozen=True)
class GmailDiagnosticFinding:
    component: str
    state: GmailDiagnosticState
    code: str
    summary: str
    remediation: str | None = None

    def to_dict(self) -> Mapping[str, object]:
        return MappingProxyType(
            {
                "component": self.component,
                "state": self.state.value,
                "code": self.code,
                "summary": self.summary,
                "remediation": self.remediation,
            }
        )


@dataclass(frozen=True)
class GmailDiagnosticReport:
    state: GmailDiagnosticState
    primary: GmailDiagnosticFinding
    findings: tuple[GmailDiagnosticFinding, ...]
    trace: tuple[GmailDiagnosticTraceStage, ...] = ()

    def to_dict(self) -> Mapping[str, object]:
        return MappingProxyType(
            {
                "state": self.state.value,
                "primary": dict(self.primary.to_dict()),
                "findings": tuple(dict(item.to_dict()) for item in self.findings),
                "trace": tuple(dict(item.to_dict()) for item in self.trace),
            }
        )

    def console_lines(self) -> tuple[str, ...]:
        if self.state is GmailDiagnosticState.DISABLED:
            return ()
        if self.state is GmailDiagnosticState.READY:
            primary = self.primary
            line = (
                f"GMAIL> READY [{primary.component}/{primary.code}]: {primary.summary}"
            )
            return (line, *(item.console_line() for item in self.trace))
        primary = self.primary
        line = (
            f"GMAIL> DEGRADED [{primary.component}/{primary.code}]: {primary.summary}"
        )
        if primary.remediation:
            line += f" Acción: {primary.remediation}"
        return (line, *(item.console_line() for item in self.trace))


class GmailDiagnosticRuntime:
    """Secret-free operational diagnostics for Gmail startup wiring."""

    def inspect_environment(self) -> GmailDiagnosticReport:
        findings: list[GmailDiagnosticFinding] = []
        enabled = _env_bool("ROBY_GMAIL_ENABLED", False)
        announcement = _env_bool("ROBY_GMAIL_STARTUP_ANNOUNCEMENT_ENABLED", enabled)
        if not enabled:
            item = _finding(
                "runtime",
                GmailDiagnosticState.DISABLED,
                "gmail_disabled",
                "Gmail está deshabilitado por configuración.",
                "Definir ROBY_GMAIL_ENABLED=true para activarlo.",
            )
            return GmailDiagnosticReport(
                item.state, item, (item,), _build_trace(item.state, item)
            )
        findings.append(_ready("runtime", "gmail_enabled", "Runtime Gmail habilitado."))

        if not announcement:
            findings.append(
                _degraded(
                    "startup_announcement",
                    "announcement_disabled",
                    "El anuncio de inicio está deshabilitado.",
                    "Definir ROBY_GMAIL_STARTUP_ANNOUNCEMENT_ENABLED=true.",
                )
            )

        account = _first_environment_value(
            "ROBY_GMAIL_ACCOUNT_ADDRESS",
            "ROBY_GMAIL_EMAIL",
            "GMAIL_ADDRESS",
            "EMAIL_USER",
        )
        findings.append(
            _ready("configuration", "account_configured", "Cuenta Gmail configurada.")
            if account
            else _degraded(
                "configuration",
                "account_missing",
                "No hay una cuenta Gmail configurada.",
                "Definir ROBY_GMAIL_ACCOUNT_ADDRESS.",
            )
        )

        token_raw = os.getenv("ROBY_GMAIL_TOKEN_PATH", "").strip()
        if not token_raw:
            findings.append(
                _degraded(
                    "oauth",
                    "token_path_missing",
                    "No está configurada la ruta del token OAuth.",
                    "Definir ROBY_GMAIL_TOKEN_PATH fuera del repositorio.",
                )
            )
        else:
            findings.extend(_inspect_token(Path(token_raw).expanduser()))

        client_path = resolve_google_client_secrets_path()
        interactive = _env_bool("ROBY_GMAIL_ALLOW_INTERACTIVE_OAUTH", False)
        findings.extend(_inspect_client_secrets(client_path, interactive))
        findings.extend(_inspect_google_dependencies())

        primary = next(
            (item for item in findings if item.state is GmailDiagnosticState.DEGRADED),
            _ready("gmail", "preflight_ready", "Preflight Gmail listo."),
        )
        state = (
            GmailDiagnosticState.DEGRADED
            if any(item.state is GmailDiagnosticState.DEGRADED for item in findings)
            else GmailDiagnosticState.READY
        )
        return GmailDiagnosticReport(
            state, primary, tuple(findings), _build_trace(state, primary)
        )

    def from_success(self) -> GmailDiagnosticReport:
        finding = _ready(
            "gmail",
            "runtime_ready",
            "El subsistema Gmail completó correctamente el arranque.",
        )
        return GmailDiagnosticReport(
            GmailDiagnosticState.READY,
            finding,
            (finding,),
            _build_trace(GmailDiagnosticState.READY, finding),
        )

    def from_exception(
        self, exc: BaseException, *, component: str = "startup_announcement"
    ) -> GmailDiagnosticReport:
        finding = _classify_exception(exc, component=component)
        return GmailDiagnosticReport(
            GmailDiagnosticState.DEGRADED,
            finding,
            (finding,),
            _build_trace(GmailDiagnosticState.DEGRADED, finding),
        )


_TRACE_STAGES = (
    ("runtime", "Runtime"),
    ("configuration", "Configuration"),
    ("google_auth", "google-auth"),
    ("oauth", "OAuth"),
    ("secure_credential_store", "Secure Credential Store"),
    ("token", "Token & Scopes"),
    ("gmail_api_backend", "Gmail API Backend"),
    ("startup_announcement", "Startup Announcement"),
    ("runtime_completion", "Runtime Completion"),
)

_COMPONENT_STAGE = {
    "runtime": "runtime",
    "configuration": "configuration",
    "google_auth": "google_auth",
    "oauth": "oauth",
    "client_secrets": "oauth",
    "permissions": "secure_credential_store",
    "secure_credential_store": "secure_credential_store",
    "token": "token",
    "scopes": "token",
    "gmail_api_backend": "gmail_api_backend",
    "startup_announcement": "startup_announcement",
    "gmail": "runtime_completion",
}


def _build_trace(
    state: GmailDiagnosticState, primary: GmailDiagnosticFinding
) -> tuple[GmailDiagnosticTraceStage, ...]:
    total = len(_TRACE_STAGES)
    if state is GmailDiagnosticState.READY:
        return tuple(
            GmailDiagnosticTraceStage(
                ordinal, total, key, label, GmailDiagnosticTraceState.OK
            )
            for ordinal, (key, label) in enumerate(_TRACE_STAGES, start=1)
        )
    if state is GmailDiagnosticState.DISABLED:
        return tuple(
            GmailDiagnosticTraceStage(
                ordinal,
                total,
                key,
                label,
                GmailDiagnosticTraceState.DISABLED
                if key == "runtime"
                else GmailDiagnosticTraceState.NOT_EXECUTED,
            )
            for ordinal, (key, label) in enumerate(_TRACE_STAGES, start=1)
        )
    failed_key = _COMPONENT_STAGE.get(primary.component, "startup_announcement")
    failed_index = next(
        index for index, (key, _) in enumerate(_TRACE_STAGES) if key == failed_key
    )
    trace = []
    for index, (key, label) in enumerate(_TRACE_STAGES):
        if index < failed_index:
            trace_state = GmailDiagnosticTraceState.OK
        elif index == failed_index:
            trace_state = GmailDiagnosticTraceState.FAILED
        else:
            trace_state = GmailDiagnosticTraceState.NOT_EXECUTED
        trace.append(
            GmailDiagnosticTraceStage(index + 1, total, key, label, trace_state)
        )
    return tuple(trace)


def _inspect_token(path: Path) -> tuple[GmailDiagnosticFinding, ...]:
    if not path.exists():
        return (
            _degraded(
                "token",
                "token_missing",
                "El archivo de token OAuth no existe.",
                (
                    "Ejecutar la activación OAuth interactiva o corregir "
                    "ROBY_GMAIL_TOKEN_PATH."
                ),
            ),
        )
    if not path.is_file():
        return (
            _degraded(
                "token",
                "token_not_file",
                "La ruta del token OAuth no apunta a un archivo regular.",
                "Corregir ROBY_GMAIL_TOKEN_PATH.",
            ),
        )
    try:
        with path.open("r", encoding="utf-8") as stream:
            payload = json.load(stream)
    except PermissionError:
        return (
            _degraded(
                "permissions",
                "token_permission_denied",
                "ROBY no puede leer el archivo de token OAuth.",
                "Conceder permiso de lectura al usuario que ejecuta ROBY.",
            ),
        )
    except OSError:
        return (
            _degraded(
                "token",
                "token_io_error",
                "No se pudo abrir el archivo de token OAuth.",
                "Verificar ruta, permisos y disponibilidad del almacenamiento.",
            ),
        )
    except (UnicodeError, json.JSONDecodeError):
        return (
            _degraded(
                "token",
                "token_invalid_json",
                "El archivo de token OAuth no contiene JSON válido.",
                "Regenerar el token mediante la activación OAuth gobernada.",
            ),
        )
    if not isinstance(payload, dict):
        return (
            _degraded(
                "token",
                "token_invalid_document",
                "El documento de token OAuth no es un objeto JSON.",
                "Regenerar el token mediante la activación OAuth gobernada.",
            ),
        )
    missing = tuple(
        key
        for key in ("client_id", "client_secret", "refresh_token")
        if not payload.get(key)
    )
    if missing:
        return (
            _degraded(
                "token",
                "token_fields_missing",
                "El token OAuth no contiene todos los campos requeridos.",
                "Regenerar el token mediante la activación OAuth gobernada.",
            ),
        )
    scopes = payload.get("scopes", ())
    if isinstance(scopes, str):
        scopes = scopes.split()
    if scopes and _REQUIRED_SCOPE not in scopes:
        return (
            _degraded(
                "scopes",
                "readonly_scope_missing",
                "El token OAuth no declara el scope Gmail de solo lectura requerido.",
                "Reautorizar la cuenta con gmail.readonly.",
            ),
        )
    return (_ready("token", "token_available", "Token OAuth disponible."),)


def _inspect_client_secrets(
    path: Path | None, interactive: bool
) -> tuple[GmailDiagnosticFinding, ...]:
    if not interactive:
        return (
            _ready(
                "oauth",
                "interactive_oauth_disabled",
                (
                    "OAuth interactivo deshabilitado por política; se requiere "
                    "token existente."
                ),
            ),
        )
    if path is None:
        return (
            _degraded(
                "client_secrets",
                "client_secrets_path_missing",
                (
                    "OAuth interactivo está permitido, pero no hay Client Secrets "
                    "disponibles."
                ),
                (
                    "Definir ROBY_GMAIL_CLIENT_SECRETS_PATH o agregar "
                    "credentials.json en el directorio de ejecución."
                ),
            ),
        )
    if not path.is_file():
        return (
            _degraded(
                "client_secrets",
                "client_secrets_missing",
                "El archivo Google OAuth Client Secrets no existe.",
                "Corregir ROBY_GMAIL_CLIENT_SECRETS_PATH.",
            ),
        )
    return (
        _ready(
            "client_secrets",
            "client_secrets_available",
            "Google OAuth Client Secrets disponible.",
        ),
    )


def _inspect_google_dependencies() -> tuple[GmailDiagnosticFinding, ...]:
    checks = (
        ("google-auth", "google.oauth2.credentials"),
        ("google-api-python-client", "googleapiclient.discovery"),
    )
    findings = []
    for package, module in checks:
        if not _module_available(module):
            findings.append(
                _degraded(
                    "google_auth" if package == "google-auth" else "gmail_api_backend",
                    "dependency_missing",
                    f"Falta la dependencia {package}.",
                    f"Instalar {package} en el entorno de ejecución de ROBY.",
                )
            )
        else:
            findings.append(
                _ready(
                    "google_auth" if package == "google-auth" else "gmail_api_backend",
                    "dependency_available",
                    f"Dependencia {package} disponible.",
                )
            )
    if _env_bool("ROBY_GMAIL_ALLOW_INTERACTIVE_OAUTH", False):
        module = "google_auth_oauthlib.flow"
        if not _module_available(module):
            findings.append(
                _degraded(
                    "oauth",
                    "interactive_dependency_missing",
                    "Falta google-auth-oauthlib para OAuth interactivo.",
                    "Instalar google-auth-oauthlib.",
                )
            )
    return tuple(findings)


def _module_available(module: str) -> bool:
    try:
        return importlib.util.find_spec(module) is not None
    except (ImportError, ModuleNotFoundError, AttributeError):
        return False


def _classify_exception(
    exc: BaseException, *, component: str
) -> GmailDiagnosticFinding:
    chain = tuple(_exception_chain(exc))
    text = " ".join(str(item).casefold() for item in chain)
    types = tuple(type(item) for item in chain)
    if any(issubclass(item, PermissionError) for item in types):
        if "interactive google oauth disabled" in text:
            return _degraded(
                "oauth",
                "interactive_oauth_denied",
                "La política de despliegue impide iniciar OAuth interactivo.",
                (
                    "Habilitar ROBY_GMAIL_ALLOW_INTERACTIVE_OAUTH o proporcionar "
                    "un token válido."
                ),
            )
        return _degraded(
            "permissions",
            "permission_denied",
            "El sistema operativo o el proveedor rechazó el acceso requerido.",
            "Verificar permisos de archivos y autorización de la cuenta.",
        )
    if any(issubclass(item, ImportError) for item in types):
        return _degraded(
            "google_auth",
            "dependency_import_failed",
            "Una dependencia Google requerida no pudo importarse.",
            "Verificar google-auth, google-api-python-client y google-auth-oauthlib.",
        )
    classifications = (
        (
            "client configuration unavailable",
            "client_secrets",
            "client_secrets_unavailable",
            "Google OAuth Client Secrets no está disponible.",
        ),
        (
            "credentials are unavailable",
            "token",
            "credentials_unavailable",
            "No hay credenciales OAuth utilizables.",
        ),
        (
            "credential refresh failed",
            "oauth",
            "token_refresh_failed",
            "Falló la renovación del token OAuth.",
        ),
        (
            "authorization failed",
            "oauth",
            "interactive_authorization_failed",
            "Falló la autorización OAuth interactiva.",
        ),
        (
            "credential persistence failed",
            "secure_credential_store",
            "credential_persistence_failed",
            "No se pudieron persistir las credenciales OAuth.",
        ),
        (
            "secure credential store read failed",
            "secure_credential_store",
            "secure_store_read_failed",
            "Falló la lectura del Secure Credential Store.",
        ),
        (
            "gmail unread subject lookup failed",
            "startup_announcement",
            "subject_lookup_failed",
            "Falló la consulta de asuntos no leídos en Gmail.",
        ),
        (
            "account address is not configured",
            "configuration",
            "account_missing",
            "No hay una cuenta Gmail configurada.",
        ),
        (
            "deployment configuration is missing",
            "oauth",
            "oauth_configuration_missing",
            "Falta la configuración de despliegue OAuth.",
        ),
    )
    for marker, classified_component, code, summary in classifications:
        if marker in text:
            return _degraded(classified_component, code, summary, _remediation(code))
    if any(issubclass(item, OSError) for item in types):
        return _degraded(
            component,
            "operating_system_error",
            "Una dependencia local de Gmail produjo un error de sistema operativo.",
            "Verificar rutas, permisos y disponibilidad del almacenamiento o red.",
        )
    return _degraded(
        component,
        "unexpected_failure",
        "El subsistema Gmail produjo un fallo no clasificado.",
        "Consultar el diagnóstico estructurado y los registros operacionales.",
    )


def _remediation(code: str) -> str:
    return {
        "client_secrets_unavailable": (
            "Configurar ROBY_GMAIL_CLIENT_SECRETS_PATH con un archivo válido."
        ),
        "credentials_unavailable": (
            "Ejecutar la activación OAuth gobernada o corregir ROBY_GMAIL_TOKEN_PATH."
        ),
        "token_refresh_failed": (
            "Reautorizar la cuenta Gmail y reemplazar el token revocado o vencido."
        ),
        "interactive_authorization_failed": (
            "Verificar Client Secrets, navegador local y consentimiento OAuth."
        ),
        "credential_persistence_failed": (
            "Verificar permisos del token o del Secure Credential Store."
        ),
        "secure_store_read_failed": (
            "Verificar protector, clave y permisos del Secure Credential Store."
        ),
        "subject_lookup_failed": (
            "Verificar token, scopes, conectividad y disponibilidad de Gmail API."
        ),
        "account_missing": "Definir ROBY_GMAIL_ACCOUNT_ADDRESS.",
        "oauth_configuration_missing": (
            "Definir ROBY_GMAIL_TOKEN_PATH y la configuración OAuth requerida."
        ),
    }[code]


def _exception_chain(exc: BaseException):
    current: BaseException | None = exc
    seen: set[int] = set()
    while current is not None and id(current) not in seen:
        seen.add(id(current))
        yield current
        current = current.__cause__ or current.__context__


def _finding(
    component: str,
    state: GmailDiagnosticState,
    code: str,
    summary: str,
    remediation: str | None = None,
) -> GmailDiagnosticFinding:
    return GmailDiagnosticFinding(component, state, code, summary, remediation)


def _ready(component: str, code: str, summary: str) -> GmailDiagnosticFinding:
    return _finding(component, GmailDiagnosticState.READY, code, summary)


def _degraded(
    component: str, code: str, summary: str, remediation: str
) -> GmailDiagnosticFinding:
    return _finding(
        component, GmailDiagnosticState.DEGRADED, code, summary, remediation
    )


def _env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None or not raw.strip():
        return default
    return raw.strip().casefold() in _TRUE


def _first_environment_value(*names: str) -> str:
    for name in names:
        value = os.getenv(name, "").strip()
        if value:
            return value
    return ""
