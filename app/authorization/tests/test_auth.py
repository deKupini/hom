import httpx
import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


@pytest.mark.asyncio
async def test_logout(mocker):
    mocker.patch("httpx.AsyncClient.post", return_value=httpx.Response(200, json={"access_token": "fake-token"}))

    response = client.post('/auth/login', data={
        'username': 'test',
        'password': 'test'
    })

    assert response.status_code == 200

    client.cookies.set('session', 'fake-session-id')

    response = client.get('/auth/logout', follow_redirects=False)

    assert response.status_code == 307
    assert response.headers['location'] == '/'

    cookies = response.cookies

    assert 'session' not in cookies or cookies.get('session') == ''


@pytest.mark.asyncio
async def test_login(mocker):
    mocker.patch("httpx.AsyncClient.post", return_value=httpx.Response(200, json={"access_token": "fake-token"}))

    response = client.post('/auth/login', data={
        'username': 'test',
        'password': 'test'
    })

    assert response.status_code == 200
    assert 'access_token' in response.json()


@pytest.mark.asyncio
async def test_login_failure(mocker):
    mocker.patch("httpx.AsyncClient.post", return_value=httpx.Response(400, json={"detail": "invalid_request"}))

    response = client.post('/auth/login', data={
        'username': 'test',
        'password': 'test'
    })

    assert response.status_code == 400
