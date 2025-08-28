from fastapi import HTTPException
from intuitlib.client import AuthClient
from quickbooks import QuickBooks
from sqlalchemy.orm import Session

from app.core.config import QUICKBOOKS_CLIENT_ID, QUICKBOOKS_CLIENT_SECRET, QUICKBOOKS_REDIRECT_URI
from app.database.crud_qbo import get_refresh_token, upsert_refresh_token

def get_qbo_client(company_id: str, db: Session) -> QuickBooks:
    ac = get_auth_client()
    rt = get_refresh_token(db, company_id)
    if not rt:
        raise HTTPException(status_code=400, detail="QuickBooks is not connected for this company_id")
    # refresh
    ac.refresh(rt)
    upsert_refresh_token(db, company_id=company_id, refresh_token=ac.refresh_token)
    return QuickBooks(auth_client=ac, company_id=company_id)
  
def get_auth_client() -> AuthClient:
  return AuthClient(
    client_id=QUICKBOOKS_CLIENT_ID,
    client_secret=QUICKBOOKS_CLIENT_SECRET,
    environment='sandbox',
    redirect_uri=QUICKBOOKS_REDIRECT_URI,
  )
