from fastapi import FastAPI
from routers import auth, store, note
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ORIGINS").split(" "),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth")
app.include_router(store.router, prefix="/api/store")
app.include_router(note.router, prefix="/api/note")
