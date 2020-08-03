from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from utilities.db import users, stores
from utilities.auth import get_active_user_required, User
from pydantic import BaseModel
from typing import Optional
from uuid import uuid4

router = APIRouter()


@router.get("/list")
def list_stores(user=Depends(get_active_user_required)):
    """
    Returns a dictionary of all user stores, in the following format:
    {store_shortcut: store_uuid, ...}
    """

    user_stores = users.get(user.username)["stores"]
    return {} if user_stores is None else user_stores


class StoreData(BaseModel):
    view: str
    shortcut: str


@router.post("/new")
def new_store(store: StoreData, user=Depends(get_active_user_required)):
    """
    Creates a new store, returns the uuid representing it.
    """

    user_stores = list_stores(user=user)
    if store.shortcut in user_stores:
        return JSONResponse(
            status_code=400,
            content={"detail": "Store with this shortcut already exists."},
        )

    # add store to user object
    store_uuid = uuid4().hex
    user_stores[store.shortcut] = store_uuid
    users.update({"stores": user_stores}, user.username)

    # create new store object, with user as owner
    stores.put(
        {
            "view": store.view,
            "items": {},
            "members": {user.username: {"permissions": "owner"}},
        },
        key=store_uuid,
    )

    return store_uuid


def _delete_store_user(store_data, username: str):
    # remove user from store members
    del store_data["members"][username]
    stores.update(
        {"members.{}".format(username): stores.util.trim()}, store_data["key"]
    )

    # if store has no members, delete it entirely
    if not store_data["members"]:
        stores.delete(store_data["key"])

    # remove store from user object
    user_stores = list_stores(user=User(username))
    for shortcut, store_uuid in user_stores.items():
        if store_uuid == store_data["key"]:
            del user_stores[shortcut]
            break
    users.update({"stores": user_stores}, username)


class DeleteStoreData(BaseModel):
    store_uuid: str
    delete_for_all: Optional[bool] = False


@router.post("/delete")
def delete_store(
    delete_store_data: DeleteStoreData, user=Depends(get_active_user_required)
):
    """
    Deletes an existing store, given uuid.
    If delete_for_all is true and user is the owner, deletes store entirely.
    If delete_for_all is false, deletes store from user only.
    """

    store_data = stores.get(delete_store_data.store_uuid)
    if store_data is None:
        return JSONResponse(
            status_code=400, content={"detail": "Store does not exist."},
        )

    if user.username not in store_data["members"]:
        return JSONResponse(
            status_code=400,
            content={"detail": "User does not have access to this store."},
        )

    if delete_store_data.delete_for_all:
        user_permission = store_data["members"][user.username]["permissions"]
        if user_permission != "owner":
            return JSONResponse(
                status_code=400,
                content={
                    "detail": "Only store owner can delete for all store members."
                },
            )

        members = store_data["members"].copy()
        for username in members:
            _delete_store_user(store_data, username)
    else:
        _delete_store_user(store_data, user.username)
