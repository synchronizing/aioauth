from dataclasses import dataclass, field
from http import HTTPStatus
from typing import Dict, Optional, Union

from .constances import _default_headers
from .types import ErrorType


@dataclass
class ErrorResponse:
    error: ErrorType
    error_description: str
    error_uri: str = ""


@dataclass
class AuthorizationCodeResponse:
    code: str
    scope: str


@dataclass
class TokenResponse:
    expires_in: int
    refresh_token_expires_in: int
    access_token: str
    refresh_token: str
    scope: str
    token_type: str = "Bearer"


@dataclass
class Response:
    content: Optional[Union[ErrorResponse, TokenResponse, AuthorizationCodeResponse]]
    status_code: HTTPStatus = HTTPStatus.OK
    headers: Dict[str, str] = field(default_factory=_default_headers)
