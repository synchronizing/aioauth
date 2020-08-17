from async_oauth2_provider.models import (
    AuthorizationCodeModel,
    ClientModel,
    TokenModel,
    UserModel,
)

from async_oauth2_provider.requests import Request


class BaseRequestValidator:
    request: Request

    def __init__(self, request: Request):
        self.request = request

    async def get_client(self, client_id: str, client_secret: str) -> ClientModel:
        raise NotImplementedError()

    async def create_token(self) -> TokenModel:
        raise NotImplementedError()


class AuthorizationCodeRequestValidator(BaseRequestValidator):
    async def get_authorization_code(self, code: str) -> AuthorizationCodeModel:
        raise NotImplementedError()

    async def delete_authorization_code(self, code):
        raise NotImplementedError()


class PasswordRequestValidator(BaseRequestValidator):
    async def get_user(self, username: str, password: str) -> UserModel:
        raise NotImplementedError()


class RefreshTokenRequestValidator(BaseRequestValidator):
    async def get_refresh_token(self, refresh_token: str) -> TokenModel:
        raise NotImplementedError()

    async def revoke_token(self, refresh_token: str):
        raise NotImplementedError()