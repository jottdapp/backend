from fastapi import APIRouter, Cookie
from fastapi.responses import JSONResponse
import hashlib
from passlib.context import CryptContext
from deta import Deta
from pydantic import BaseModel
from uuid import uuid4
import os

router = APIRouter()

deta = Deta(os.getenv("DETA_BASE_KEY"))
users = deta.Base("users")


class SignupData(BaseModel):
    username: str
    password: str


class LoginData(BaseModel):
    username: str
    password: str


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


@router.post("/signup")
async def signup(data: SignupData):
    if users.get(data.username):
        return {"error": "Username already in use."}

    users.put({"password": get_password_hash(data.password)}, data.username)
    return {"success": True}


@router.post("/login")
async def login(data: LoginData):
    entry = users.get(data.username)
    if not entry:
        return {"error": "Unknown username."}
    elif not verify_password(data.password, entry["password"]):
        return {"error": "Wrong password."}
    else:
        session_cookie = str(uuid4())
        response = JSONResponse(content={"success": True})
        response.set_cookie(key="session", value=session_cookie)
        return response
