"""Frozen M6 compatibility shim for the neutral response contract.

Modern code must import :mod:`domain.response` directly. This module remains
only for historical response-model compatibility while preserving type identity.
"""

from domain.response import ResponseStatus, UserResponse

__all__ = ["ResponseStatus", "UserResponse"]
