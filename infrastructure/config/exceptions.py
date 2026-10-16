from domain.exceptions import InfrastructureError


class ConfigError(InfrastructureError):
    """Error base de configuración."""


class ConfigFileNotFoundError(ConfigError, FileNotFoundError):
    """No se encontró el archivo de configuración base requerido."""


class InvalidConfigError(ConfigError, ValueError):
    """La configuración no tiene el formato esperado."""
