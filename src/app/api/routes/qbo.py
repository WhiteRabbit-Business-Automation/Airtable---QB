from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from intuitlib.enums import Scopes
from sqlalchemy.orm import Session

from app.shared.quickbooks import get_auth_client
from app.shared.database import get_db
from app.database.crud_qbo import upsert_refresh_token, get_refresh_token

router = APIRouter()


@router.get("/connect")
def qbo_connect():
  auth_client = get_auth_client()
  url = auth_client.get_authorization_url([Scopes.ACCOUNTING])
  return RedirectResponse(url)

@router.get("/callback")
def qbo_callback(code: str, realmId: str, db: Session = Depends(get_db)):
  auth_client = get_auth_client()
  auth_client.get_bearer_token(code, realm_id=realmId)

  #Saves only the refresh token
  upsert_refresh_token(db, realmId, auth_client.refresh_token,
                      "sandbox","accounting")

  return {"message": "QuickBooks Online connected successfully.", "company": realmId}

