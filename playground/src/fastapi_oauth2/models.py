from typing import Optional

from pydantic import BaseModel


class BaseUser(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None

    @property
    def is_authenticated(self) -> bool:
        raise NotImplementedError()  # pragma: no cover


class User(BaseUser):
    @property
    def is_authenticated(self) -> bool:
        return True


class AnonymousUser(BaseUser):
    @property
    def is_authenticated(self) -> bool:
        return False
