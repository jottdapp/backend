from fastapi import APIRouter, Depends
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
    return [] if user_stores is None else user_stores


@router.post("/new")
def new_store(store: StoreData, user=Depends(get_active_user_required)):
    store_uuid = uuid4().hex
    stores.put(
        {
            "view": store.view,
            "items": [],
            "members": [{"username": user.username, "permissions": "owner"}],
        },
        key=store_uuid,
    )

    # Temporary workaround code because of Deta's [] -> null bug
    user_stores = list_stores(user=user)
    user_stores.append({"key": store_uuid, "shortcut": store.shortcut})
    users.update({"stores": user_stores}, user.username)

    # Code to replace with once Deta bug is fixed
    # users.update(
    #     {"stores": users.util.append({"key": store_uuid, "shortcut": store.shortcut})},
    #     user.username,
    # )

    return store_uuid
