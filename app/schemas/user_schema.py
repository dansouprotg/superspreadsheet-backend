from pydantic import BaseModel, EmailStr, Field
from typing import Annotated

class UserCreate(BaseModel):
    email: EmailStr
    password: Annotated[str, Field(min_length=8, max_length=72)]

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class SetupRequest(BaseModel):
    email: EmailStr

class SetupComplete(BaseModel):
    email: EmailStr
    password: Annotated[str, Field(min_length=8, max_length=72)]
    code: str