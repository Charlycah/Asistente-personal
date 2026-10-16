class ROBYZIPError(Exception):
    """Excepción base de ROBYZIP."""


class DomainError(ROBYZIPError):
    """Error de reglas de dominio."""


class ApplicationError(ROBYZIPError):
    """Error de caso de uso o aplicación."""


class InfrastructureError(ROBYZIPError):
    """Error de infraestructura externa o persistencia."""
