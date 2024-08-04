import httpx
from fastapi import APIRouter, Request, Depends, HTTPException

from authlib.integrations.starlette_client import OAuth
import os

from fastapi.security import OAuth2PasswordRequestForm
from starlette.responses import RedirectResponse

oauth = OAuth()
oauth.register(
    name='keycloak',
    client_id=os.getenv("KEYCLOAK_CLIENT_ID"),
    client_secret=os.getenv("KEYCLOAK_CLIENT_SECRET"),
    server_metadata_url=f'http://keycloak:8080/realms/{os.getenv("KEYCLOAK_REALM")}'
                        f'/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid profile email'}
)

router = APIRouter()


@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    url = (f"{os.getenv('NETWORK_KEYCLOAK_SERVER_URL')}"
           f"/realms/{os.getenv('KEYCLOAK_REALM')}"
           f"/protocol/openid-connect/token")
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "password",
        "client_id": os.getenv("KEYCLOAK_CLIENT_ID"),
        "username": form_data.username,
        "password": form_data.password,
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, data=data)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Invalid credentials")
        return response.json()


@router.get('/logout')
async def logout(request: Request):
    request.session.pop('user', None)
    return RedirectResponse(url='/')
