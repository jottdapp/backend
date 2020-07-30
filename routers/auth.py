from datetime import timedelta
from fastapi import APIRouter, Cookie, status
from fastapi.responses import JSONResponse
from passlib.context import CryptContext
from utilities.db import users
from pydantic import BaseModel
from uuid import uuid4
from utilities.jwt import create_access_token, read_unexpired_access_token
from utilities.auth import User, UnknownUsernameError, WrongPasswordError, get_password_hash
import os

router = APIRouter()


class SignupData(BaseModel):
    username: str
    password: str


class LoginData(BaseModel):
    username: str
    password: str

@router.post("/signup")
async def signup(data: SignupData):
    if users.get(data.username):
        return {"detail": "Username already in use."}

    users.put({"password": get_password_hash(data.password)}, data.username)
    return {"success": True}


@router.post("/login")
async def login(data: LoginData):
    user = None
    try:
        user = User.authenticate(data.username, data.password)
    except UnknownUsernameError:
        # 400 is Bad Request
        return JSONResponse(status_code=400, content={"detail": "Unkown username."})
    except WrongPasswordError:
        return JSONResponse(status_code=400, content={"detail": "Wrong password."})

    session_cookie = user.create_access_token(timedelta(days=1))
    response = JSONResponse(content={"success": True})
    response.set_cookie(key="session", value=session_cookie)
    return response

