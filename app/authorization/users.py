import os

import httpx
from fastapi import HTTPException, Depends, APIRouter
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2AuthorizationCodeBearer
from starlette import status

from app.authorization.models import UserCreate

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=f"http://keycloak:8080/realms/"
                     f"{os.getenv('KEYCLOAK_REALM')}/protocol/openid-connect/auth",
    tokenUrl=f"http://keycloak:8080/realms/"
             f"{os.getenv('KEYCLOAK_REALM')}/protocol/openid-connect/token",
    refreshUrl=f"http://keycloak:8080/realms/"
               f"{os.getenv('KEYCLOAK_REALM')}/protocol/openid-connect/token",
)

router = APIRouter()


async def get_current_user(token: str = Depends(oauth2_scheme)):
    async with httpx.AsyncClient() as client:
        userinfo_response = await client.get(
            f"http://keycloak:8080/realms/{os.getenv('KEYCLOAK_REALM')}/protocol/openid-connect/userinfo",
            headers={"Authorization": f"Bearer {token}"}
        )
    if userinfo_response.status_code != 200:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")
    return userinfo_response.json()


@router.post('/register')
async def register_user(user: UserCreate):
    token = await get_admin_token()
    async with httpx.AsyncClient() as client:
        data = {
            "username": user.username,
            "enabled": True,
            "email": user.email,
            "firstName": user.first_name,
            "lastName": user.last_name,
            "credentials": [{"type": "password", "value": user.password, "temporary": False}]
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }

        response = await client.post(
            f"{os.getenv('NETWORK_KEYCLOAK_SERVER_URL')}/admin/realms/{os.getenv('KEYCLOAK_REALM')}/users",
            json=data,
            headers=headers
        )

        if response.status_code != 201:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User registration failed")
        return JSONResponse(status_code=status.HTTP_201_CREATED, content={"msg": "User created successfully"})


async def get_admin_token():
    async with httpx.AsyncClient() as client:
        data = {
            "client_id": "admin-cli",
            "grant_type": "password",
            "username": os.getenv("KEYCLOAK_ADMIN"),
            "password": os.getenv("KEYCLOAK_ADMIN_PASSWORD"),
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        response = await client.post(
            f"{os.getenv('NETWORK_KEYCLOAK_SERVER_URL')}/realms/master/protocol/openid-connect/token",
            data=data,
            headers=headers
        )

        if response.status_code != 200:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get admin token")
        return response.json()["access_token"]


@router.get('/protected')
async def protected_route(current_user: dict = Depends(get_current_user)):
    return {"message": "Protected endpoint", "user": current_user}
