from typing import Optional

from fastapi import FastAPI
from routers import auth

app = FastAPI()


@app.get("/")
def read_root():
    return {"hello": "world"}


app.include_router(auth.router, prefix="/api/auth")
