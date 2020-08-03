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

    return [] if store["items"] is None else store["items"]


class NoteData(BaseModel):
    store_uuid: str
    note: Dict


@router.post("/new")
def new_note(note_data: NoteData, user=Depends(get_active_user_required)):
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
    note_object = {"id": note_uuid, "note": note_data.note}

    if store["items"] is None:
        stores.update({"items": [note_object]}, note_data.store_uuid)
    else:
        stores.update({"items": stores.util.append(note_object)}, note_data.store_uuid)

    return note_uuid
