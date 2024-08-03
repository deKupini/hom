import httpx
import pytest

from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.authorization.users import get_admin_token, get_current_user
from main import app


client = TestClient(app)


@pytest.mark.asyncio
async def test_get_admin_token(httpx_mock, monkeypatch):
    monkeypatch.setenv('KEYCLOAK_ADMIN', 'admin')
    monkeypatch.setenv('KEYCLOAK_ADMIN_PASSWORD', 'admin')
    monkeypatch.setenv('NETWORK_KEYCLOAK_SERVER_URL', 'http://keycloak:8080')

    httpx_mock.add_response(
        method='POST',
        url='http://keycloak:8080/realms/master/protocol/openid-connect/token',
        json={'access_token': 'admin-token'},
        status_code=200
    )

    token = await get_admin_token()
    assert token


@pytest.mark.asyncio
async def test_get_admin_token_failure(httpx_mock, monkeypatch):
    monkeypatch.setenv('KEYCLOAK_ADMIN', 'admin')
    monkeypatch.setenv('KEYCLOAK_ADMIN_PASSWORD', 'admin')
    monkeypatch.setenv('NETWORK_KEYCLOAK_SERVER_URL', 'http://keycloak:8080')

    httpx_mock.add_response(
        method='POST',
        url='http://keycloak:8080/realms/master/protocol/openid-connect/token',
        json={'error': 'invalid_request'},
        status_code=400
    )

    with pytest.raises(HTTPException):
        await get_admin_token()


@pytest.mark.asyncio
async def test_register_user(mocker):
    mocker.patch('app.authorization.users.get_admin_token', return_value='admin-token')
    mocker.patch('httpx.AsyncClient.post', return_value=httpx.Response(201, json={'msg': 'User created successfully'}))

    response = client.post('/users/register', json={
        "username": "test",
        "password": "test",
        "email": "test@test.com",
        "first_name": "test",
        "last_name": "test",
    })

    assert response.status_code == 201
    assert response.json() == {'msg': 'User created successfully'}


@pytest.mark.asyncio
async def test_register_user_failure(mocker):
    mocker.patch('app.authorization.users.get_admin_token', return_value='admin-token')
    mocker.patch('httpx.AsyncClient.post', return_value=httpx.Response(400, json={'error': 'User registration failed'}))

    response = client.post('/users/register', json={
        "username": "test",
        "password": "test",
        "email": "test@test.com",
        "first_name": "test",
        "last_name": "test",
    })

    assert response.status_code == 400
    assert response.json() == {'detail': 'User registration failed'}


@pytest.mark.asyncio
async def test_get_current_user(mocker):
    mocker.patch('httpx.AsyncClient.get', return_value=httpx.Response(200, json={'username': 'test'}))

    user_info = await get_current_user()

    assert user_info == {'username': 'test'}


@pytest.mark.asyncio
async def test_get_current_user_failure(mocker):
    mocker.patch('httpx.AsyncClient.get', return_value=httpx.Response(401, json={'error': 'Invalid authentication credentials'}))

    with pytest.raises(HTTPException):
        await get_current_user()
