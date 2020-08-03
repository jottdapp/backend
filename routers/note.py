from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from utilities.db import stores
from utilities.auth import get_active_user_required
from pydantic import BaseModel
from typing import Dict
from uuid import uuid4


router = APIRouter()


@router.get("/list")
def list_notes(store_uuid: str, user=Depends(get_active_user_required)):
    store = stores.get(store_uuid)
    if store is None:
        return JSONResponse(
            status_code=400, content={"detail": "Store does not exist."},
        )
    if user.username not in store["members"]:
        return JSONResponse(
            status_code=400,
            content={"detail": "User does not have access to this store."},
        )

    return {} if store["items"] is None else store["items"]


class NewNoteData(BaseModel):
    store_uuid: str
    note: Dict


@router.post("/new")
def new_note(note_data: NewNoteData, user=Depends(get_active_user_required)):
    store = stores.get(note_data.store_uuid)
    if store is None:
        return JSONResponse(
            status_code=400, content={"detail": "Store does not exist."},
        )
    if (user.username not in store["members"]) or (
        store["members"][user.username]["permissions"] == "read"
    ):
        return JSONResponse(
            status_code=400,
            content={"detail": "User does not have write access to this store."},
        )

    note_uuid = uuid4().hex
    if store["items"] is None:
        stores.update({"items": {note_uuid: note_data.note}}, note_data.store_uuid)
    else:
        stores.update(
            {"items.{}".format(note_uuid): note_data.note}, note_data.store_uuid
        )

    return note_uuid


class EditNoteData(BaseModel):
    store_uuid: str
    note_uuid: str
    note: Dict


@router.post("/edit")
def edit_note(note_data: EditNoteData, user=Depends(get_active_user_required)):
    store = stores.get(note_data.store_uuid)
    if store is None:
        return JSONResponse(
            status_code=400, content={"detail": "Store does not exist."},
        )
    if (user.username not in store["members"]) or (
        store["members"][user.username]["permissions"] == "read"
    ):
        return JSONResponse(
            status_code=400,
            content={"detail": "User does not have write access to this store."},
        )

    if note_data.note_uuid not in store["items"]:
        return JSONResponse(
            status_code=400, content={"detail": "Note does not exist."},
        )

    stores.update(
        {"items.{}".format(note_data.note_uuid): note_data.note}, note_data.store_uuid
    )
