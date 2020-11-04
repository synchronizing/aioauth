import time
from http import HTTPStatus
from typing import Dict, List

import pytest
from aioauth.config import get_settings
from aioauth.endpoints import Endpoint
from aioauth.models import Client
from aioauth.requests import Post, Query, Request
from aioauth.types import (
    CodeChallengeMethod,
    ErrorType,
    GrantType,
    RequestMethod,
    ResponseType,
)
from aioauth.utils import (
    create_s256_code_challenge,
    encode_auth_headers,
    generate_token,
)

from .models import Defaults
from .utils import set_values


@pytest.mark.asyncio
async def test_insecure_transport_error(endpoint: Endpoint):
    request_url = "http://localhost"

    request = Request(url=request_url, method=RequestMethod.GET,)

    response = await endpoint.create_authorization_code_response(request)
    assert response.status_code == HTTPStatus.BAD_REQUEST


@pytest.mark.asyncio
async def test_allowed_methods(endpoint: Endpoint):
    request_url = "https://localhost"

    request = Request(url=request_url, method=RequestMethod.POST,)

    response = await endpoint.create_authorization_code_response(request)
    assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED


@pytest.mark.asyncio
async def test_invalid_client_credentials(endpoint: Endpoint, defaults: Defaults):
    client_id = defaults.client_id
    request_url = "https://localhost"

    post = Post(
        grant_type=GrantType.TYPE_PASSWORD,
        username=defaults.username,
        password=defaults.password,
    )

    request = Request(
        post=post,
        url=request_url,
        method=RequestMethod.POST,
        headers=encode_auth_headers(client_id, "client_secret"),
    )

    response = await endpoint.create_token_response(request)
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.content.error == ErrorType.INVALID_REQUEST


@pytest.mark.asyncio
async def test_invalid_scope(endpoint: Endpoint, defaults: Defaults):
    client_id = defaults.client_id
    client_secret = defaults.client_secret
    request_url = "https://localhost"

    post = Post(
        grant_type=GrantType.TYPE_PASSWORD,
        username=defaults.username,
        password=defaults.password,
        scope="test test",
    )

    request = Request(
        post=post,
        url=request_url,
        method=RequestMethod.POST,
        headers=encode_auth_headers(client_id, client_secret),
    )

    response = await endpoint.create_token_response(request)
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.content.error == ErrorType.INVALID_SCOPE


@pytest.mark.asyncio
async def test_invalid_grant_type(endpoint: Endpoint, defaults: Defaults, storage):
    client: Client = storage["clients"][0]

    client_metadata = set_values(
        client.client_metadata, {"grant_types": [GrantType.TYPE_AUTHORIZATION_CODE]}
    )

    client = set_values(client, {"client_metadata": client_metadata})

    storage["clients"][0] = client

    client_id = defaults.client_id
    client_secret = defaults.client_secret
    request_url = "https://localhost"

    post = Post(
        grant_type=GrantType.TYPE_PASSWORD,
        username=defaults.username,
        password=defaults.password,
        scope="test test",
    )

    request = Request(
        post=post,
        url=request_url,
        method=RequestMethod.POST,
        headers=encode_auth_headers(client_id, client_secret),
    )

    response = await endpoint.create_token_response(request)
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.content.error == ErrorType.UNAUTHORIZED_CLIENT


@pytest.mark.asyncio
async def test_invalid_response_type(endpoint: Endpoint, defaults: Defaults, storage):
    code_verifier = generate_token(128)
    code_challenge = create_s256_code_challenge(code_verifier)
    request_url = "https://localhost"
    user = "username"

    client = storage["clients"][0]

    client_metadata = set_values(
        client.client_metadata, {"response_types": [ResponseType.TYPE_TOKEN]}
    )
    client = set_values(client, {"client_metadata": client_metadata})

    storage["clients"][0] = client

    query = Query(
        client_id=defaults.client_id,
        response_type=ResponseType.TYPE_CODE,
        redirect_uri=defaults.redirect_uri,
        scope=defaults.scope,
        state=generate_token(10),
        code_challenge_method=CodeChallengeMethod.S256,
        code_challenge=code_challenge,
    )

    request = Request(
        url=request_url, query=query, method=RequestMethod.GET, user=user,
    )
    response = await endpoint.create_authorization_code_response(request)
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.content.error == ErrorType.UNSUPPORTED_RESPONSE_TYPE


@pytest.mark.asyncio
async def test_anonymous_user(endpoint: Endpoint, defaults: Defaults, storage):
    code_verifier = generate_token(128)
    code_challenge = create_s256_code_challenge(code_verifier)
    request_url = "https://localhost"

    query = Query(
        client_id=defaults.client_id,
        response_type=ResponseType.TYPE_CODE,
        redirect_uri=defaults.redirect_uri,
        scope=defaults.scope,
        state=generate_token(10),
        code_challenge_method=CodeChallengeMethod.S256,
        code_challenge=code_challenge,
    )

    request = Request(url=request_url, query=query, method=RequestMethod.GET)
    response = await endpoint.create_authorization_code_response(request)
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.content.error == ErrorType.INVALID_CLIENT


@pytest.mark.asyncio
async def test_expired_authorization_code(
    endpoint: Endpoint, defaults: Defaults, storage: Dict[str, List]
):
    request_url = "https://localhost"

    settings = get_settings()

    authorization_code = storage["authorization_codes"][0]
    storage["authorization_codes"][0] = set_values(
        authorization_code,
        {"auth_time": time.time() - settings.AUTHORIZATION_CODE_EXPIRES_IN},
    )
    post = Post(
        grant_type=GrantType.TYPE_AUTHORIZATION_CODE,
        redirect_uri=defaults.redirect_uri,
        code=storage["authorization_codes"][0].code,
    )

    request = Request(
        url=request_url,
        post=post,
        method=RequestMethod.POST,
        headers=encode_auth_headers(defaults.client_id, defaults.client_secret),
    )
    response = await endpoint.create_token_response(request)
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.content.error == ErrorType.INVALID_GRANT


@pytest.mark.asyncio
async def test_expired_refresh_token(
    endpoint: Endpoint, defaults: Defaults, storage: Dict[str, List]
):
    settings = get_settings()
    token = storage["tokens"][0]
    refresh_token = token.refresh_token
    storage["tokens"][0] = set_values(
        token, {"issued_at": time.time() - (settings.TOKEN_EXPIRES_IN * 2)}
    )
    request_url = "https://localhost"
    post = Post(grant_type=GrantType.TYPE_REFRESH_TOKEN, refresh_token=refresh_token,)
    request = Request(
        url=request_url,
        post=post,
        method=RequestMethod.POST,
        headers=encode_auth_headers(defaults.client_id, defaults.client_secret),
    )
    response = await endpoint.create_token_response(request)
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.content.error == ErrorType.INVALID_GRANT