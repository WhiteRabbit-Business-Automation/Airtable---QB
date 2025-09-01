from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from intuitlib.enums import Scopes
from sqlalchemy.orm import Session
import datetime as dt

from ...shared.quickbooks import get_auth_client, now_utc
from ...shared.database import get_db
from ...database.crud_qbo import upsert_tokens
from ...core.config import QUICKBOOKS_ENV

router = APIRouter()


@router.get("/connect", status_code=status.HTTP_302_FOUND)
def qbo_connect():
    """
    Starts the OAuth flow. You only need to do this once to seed the refresh token.
    """
    auth_client = get_auth_client()
    url = auth_client.get_authorization_url([Scopes.ACCOUNTING])
    return RedirectResponse(url)


@router.get("/callback", status_code=status.HTTP_200_OK)
def qbo_callback(code: str, realmId: str, db: Session = Depends(get_db)):
    """
    OAuth redirect URI. Exchanges code for tokens and persists both access & refresh tokens.
    After this, the server can refresh tokens automatically without a browser.
    """
    try:
        auth_client = get_auth_client()
        # Exchange authorization code for tokens
        auth_client.get_bearer_token(code, realm_id=realmId)

        # Access token + expiry
        access_token = auth_client.access_token
        access_expires_in = getattr(auth_client, "expires_in", None) or getattr(auth_client, "access_token_expires_in", 3600)
        access_expires_at = now_utc() + dt.timedelta(seconds=int(access_expires_in))

        # Refresh token (rotates) + expiry (SDKs expose either x_refresh_token_expires_in or refresh_token_expires_in)
        refresh_token = auth_client.refresh_token
        refresh_expires_in = getattr(auth_client, "x_refresh_token_expires_in", None) or getattr(auth_client, "refresh_token_expires_in", 100 * 24 * 3600)
        refresh_expires_at = now_utc() + dt.timedelta(seconds=int(refresh_expires_in))

        # Persist both tokens so the backend can refresh headlessly going forward
        upsert_tokens(
            db=db,
            realm_id=realmId,
            environment=QUICKBOOKS_ENV,
            access_token=access_token,
            access_token_expires_at=access_expires_at,
            refresh_token=refresh_token,
            refresh_token_expires_at=refresh_expires_at,
            scopes="accounting",
        )

        return {
            "message": "QuickBooks Online connected successfully.",
            "company": realmId,
            "environment": QUICKBOOKS_ENV,
        }

    except Exception as e:
        # Bubble up a clear HTTP error; logs should capture the original stack.
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": "Failed to complete QuickBooks OAuth callback", "error": str(e)},
        )
