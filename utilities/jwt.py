from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import os

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

def create_access_token(data: dict, expires_delta: timedelta):
    """ Writes data, and adds the key exp, that is when it expires """
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def read_access_token(token: str):
    """ Returns the contents of a jwt, None if the data is bad """
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None

def read_unexpired_access_token(token: str):
    """ Returns the contents of a jwt, if it hasn't expired, and None if it has expired or the data is bad """
    payload = read_access_token(token)
    if payload == None:
        return None
    if payload["exp"] < datetime.utcnow().timestamp():
        return None
    return payload
