from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from utilities.db import users, stores
from utilities.auth import get_active_user_required
from pydantic import BaseModel
from uuid import uuid4

router = APIRouter()


class StoreData(BaseModel):
    view: str
    shortcut: str


@router.get("/list")
def list_stores(user=Depends(get_active_user_required)):
    user_stores = users.get(user.username)["stores"]
    return {} if user_stores is None else user_stores


@router.post("/new")
def new_store(store: StoreData, user=Depends(get_active_user_required)):
    user_stores = list_stores(user=user)
    if store.shortcut in user_stores:
        return JSONResponse(
            status_code=400,
            content={"detail": "Store with this shortcut already exists."},
        )

    store_uuid = uuid4().hex
    user_stores[store.shortcut] = store_uuid
    users.update({"stores": user_stores}, user.username)

    stores.put(
        {
            "view": store.view,
            "items": [],
            "members": [{"username": user.username, "permissions": "owner"}],
        },
        key=store_uuid,
    )

    return store_uuid
