from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    password: str
    email: str
    first_name: str
    last_name: str
