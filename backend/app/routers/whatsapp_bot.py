from typing import Annotated

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.whatsapp_bot_service import process_webhook

router = APIRouter(prefix="/whatsapp", tags=["WhatsApp Bot"])


@router.post("/webhook/{transport}")
def whatsapp_webhook(transport: str, request: Request, db: Annotated[Session, Depends(get_db)]):
    payload = await_request_json(request)
    result = process_webhook(db, transport, payload)
    db.commit()
    return result


@router.post("/webhook")
def whatsapp_webhook_default(request: Request, db: Annotated[Session, Depends(get_db)]):
    payload = await_request_json(request)
    result = process_webhook(db, "twilio", payload)
    db.commit()
    return result


async def await_request_json(request: Request) -> dict:
    try:
        return await request.json()
    except Exception:
        form = await request.form()
        return dict(form)
