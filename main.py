from fastapi import FastAPI
from routers import auth
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI()

app.add_middleware(
        CORSMiddleware,
        allow_origins=os.getenv("ORIGINS").split(" "),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
)

app.include_router(auth.router, prefix="/api/auth")
