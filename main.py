import os

from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from app.authorization import auth, users

app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY"))

app.include_router(auth.router, prefix="/auth")
app.include_router(users.router, prefix="/users")


@app.get('/')
def read_root():
    return {"message": "Hello World"}
