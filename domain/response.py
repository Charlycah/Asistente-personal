from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ResponseStatus(str, Enum):
    SUCCESS = "success"
    NEEDS_INFORMATION = "needs_information"
    FAILURE = "failure"


@dataclass(frozen=True)
class UserResponse:
    text: str
    status: ResponseStatus
