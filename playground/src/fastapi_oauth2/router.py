from pathlib import Path
from urllib.parse import quote, urlencode

from async_oauth2_provider.requests import Query
from async_oauth2_provider.responses import ErrorResponse, Response
from async_oauth2_provider.types import ResponseType
from async_oauth2_provider.utils import generate_token, scope_to_list
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi_oauth2.config import settings
from fastapi_oauth2.oauth2 import endpoint
from pydantic.networks import AnyHttpUrl
from starlette import status
from starlette.datastructures import URL

from .utils import to_fastapi_response, to_oauth2_request

router = APIRouter()
here = Path(__file__).parent
templates = Jinja2Templates(directory=str(here / "templates"))
credentials = {
    "client_id": settings.OAUTH2_CLIENT_ID,
    "client_secret": settings.OAUTH2_CLIENT_SECRET,
    "username": settings.OAUTH2_USERNAME,
    "password": settings.OAUTH2_PASSWORD,
    "redirect_uri": settings.OAUTH2_REDIRECT_URI,
}


@router.get("/authorize", name="authorize")
async def authorize(request: Request):
    oauth2_request = await to_oauth2_request(request)
    oauth2_response = await endpoint.create_authorization_code_response(oauth2_request)

    response = await to_fastapi_response(oauth2_response)

    error_description = None

    if isinstance(oauth2_response.content, ErrorResponse):
        error_description = oauth2_response.content.error_description

    context = {
        "request": request,
        "error": error_description,
        "scopes": scope_to_list(oauth2_request.query.scope),
        "redirect_to": None,
        "credentials": credentials,
    }

    if response.status_code == status.HTTP_302_FOUND:
        return response

    return templates.TemplateResponse(
        "login.html", context, status_code=response.status_code
    )


@router.post("/token")
async def token(request: Request):
    oauth2_request = await to_oauth2_request(request)
    oauth2_response = await endpoint.create_token_response(oauth2_request)

    return await to_fastapi_response(oauth2_response)


@router.get("/callback")
async def callback(request: Request):
    return templates.TemplateResponse(
        "callback.html",
        {"request": request, "credentials": credentials},
        status_code=status.HTTP_200_OK,
    )


def build_uri(
    url: URL,
    response_type: ResponseType,
    scope: str = "",
    state: str = generate_token(),
):
    params = {
        "url": str(url),
        "scheme": url.scheme,
        "host": url.hostname,
        "port": str(url.port),
        "path": "/authorize",
    }

    return AnyHttpUrl.build(
        **params,
        query=urlencode(
            {
                "client_id": settings.OAUTH2_CLIENT_ID,
                "response_type": response_type.value,
                "redirect_uri": settings.OAUTH2_REDIRECT_URI,
                "state": state,
                "scope": scope,
            },
            quote_via=quote,
        )
    )


@router.get("/")
async def index(request: Request):
    authorization_code_uri = build_uri(
        request.url, ResponseType.TYPE_CODE, "read write"
    )
    implicit_flow_uri = build_uri(request.url, ResponseType.TYPE_TOKEN, "read write")

    context = {
        "request": request,
        "credentials": credentials,
        "authorization_code_uri": authorization_code_uri,
        "implicit_flow_uri": implicit_flow_uri,
    }
    return templates.TemplateResponse(
        "index.html", context, status_code=status.HTTP_200_OK
    )


@router.post("/token/introspect")
async def introspect(request: Request):
    oauth2_request = await to_oauth2_request(request)
    oauth2_response = await endpoint.create_token_introspection_response(oauth2_request)
    return await to_fastapi_response(oauth2_response)
