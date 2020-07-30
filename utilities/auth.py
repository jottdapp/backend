from datetime import timedelta
from utilities.jwt import create_access_token, read_unexpired_access_token
from utilities.db import users
from passlib.context import CryptContext
from fastapi import Cookie, HTTPException

class UnknownUsernameError(Exception):
    pass

class WrongPasswordError(Exception):
    pass

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)


def cache_first_result(func):
    """ Calls the function the first time, and remembers the result. """
    result = None
    has_result = False

    def wrapper(*args, **kwargs):
        nonlocal result
        nonlocal has_result

        if not has_result:
            result = func(*args, *kwargs)
            has_result = True
        return result

    return wrapper

class User:
    def __init__(self, username):
        self.username = username

    @cache_first_result
    def exists(self):
        """ Returns whether the user is in the database """
        return users.get(self.username) != None
    
    @staticmethod
    def authenticate(username, password):
        """ Given a username and password, returns the User if this is the correct password, otherwise throws errors UnknownUsernameError and WrongPasswordError. """
        entry = users.get(username)
        if not entry:
            raise UnknownUsernameError
        elif not verify_password(password, entry["password"]):
            raise WrongPasswordError
        return User(username)

    def create_access_token(self, expires_delta: timedelta):
        return create_access_token({"usr": self.username}, expires_delta)


def get_active_user(session: str = Cookie(None)):
    """
    Returns a User or None if there is no active existing user.

    Usage example:
    @app.get("/test")
    def get_username(user = Depends(get_active_user_required)):
        return user.username
    """
    if session == None:
        return None
    payload = read_unexpired_access_token(session)
    if payload != None:
        if "usr" in payload and type(payload["usr"]) is str:
            user = User(payload["usr"])
            if user.exists():
                return user
    return None

def get_active_user_required(session: str = Cookie(None)):
    """
    Always returns a User, throws an HTTPException with "detail":"unauthorized" and status code 403 otherwise.

    Usage example:
    @app.get("/test")
    def get_username(user = Depends(get_active_user_required)):
        return user.username

    and /test will return {"detail":"unauthorized"} with status code 403 if there is no valid session or the session has expired.
    """
    user = get_active_user(session)
    if user == None:
        raise HTTPException(
                status_code=403, # 403 is Forbidden
                detail="unauthorized"
                )
    return user
