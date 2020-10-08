from fastapi import FastAPI
from fastapi_oauth2.config import settings
from fastapi_oauth2.db import gino
from fastapi_oauth2.router import router
from starlette.authentication import (AuthCredentials, AuthenticationBackend,
                                      AuthenticationError, SimpleUser,
                                      UnauthenticatedUser)
from starlette.middleware.authentication import AuthenticationMiddleware

# from fastapi.staticfiles import StaticFiles


class BasicAuthBackend(AuthenticationBackend):
    async def authenticate(self, request):
        return AuthCredentials(["authenticated"]), SimpleUser("username")


app = FastAPI(title=settings.PROJECT_NAME)
# app.mount("/static", StaticFiles(directory="static"), name="static")
app.add_middleware(AuthenticationMiddleware, backend=BasicAuthBackend())
app.include_router(router)
gino.init_app(app)
