import datetime as dt
import redis
from sqlalchemy.orm import Session
from intuitlib.client import AuthClient
from quickbooks import QuickBooks
from ..utils.lock import RedisLock
from ..core.config import REDIS_URL, REDIS_PORT, REDIS_DB

from ..core.config import (
    QUICKBOOKS_CLIENT_ID,
    QUICKBOOKS_CLIENT_SECRET,
    QUICKBOOKS_REDIRECT_URI,
    QUICKBOOKS_ENV,
)
from ..database.crud_qbo import get_decrypted_tokens, upsert_tokens
from ..core.exceptions import BusinessValidationError

redis_client = redis.from_url(REDIS_URL, db = int(REDIS_DB) if REDIS_DB else 0, decode_responses=False)
TOKEN_SAFETY_WINDOW_SECONDS = 5 * 60  # refresh 5 minutes before expiry
UTC = dt.timezone.utc # all times in UTC

# Get the authentication client for QuickBooks
def get_auth_client() -> AuthClient:
    return AuthClient(
        client_id=QUICKBOOKS_CLIENT_ID,
        client_secret=QUICKBOOKS_CLIENT_SECRET,
        environment=QUICKBOOKS_ENV,         # "sandbox" or "production"
        redirect_uri=QUICKBOOKS_REDIRECT_URI,
    )


def now_utc() -> dt.datetime:
    # always timezone-aware UTC
    return dt.datetime.utcnow().replace(tzinfo=UTC)

# Ensure a datetime object is timezone-aware
def ensure_aware(dt_obj: dt.datetime | None) -> dt.datetime | None:
    # normalize DB datetimes; assume UTC when naive
    if dt_obj is None:
        return None
    if dt_obj.tzinfo is None:
        return dt_obj.replace(tzinfo=UTC)
    return dt_obj

# Get the number of seconds until a token expires
def expires_in_seconds(expires_at: dt.datetime | None) -> float:
    if not expires_at:
        return -1e9  # treat as already expired
    expires_at = ensure_aware(expires_at)
    return (expires_at - now_utc()).total_seconds()

# Check if a token needs to be refreshed
def needs_refresh(expires_at: dt.datetime | None) -> bool:
    if not expires_at:
        return True
    return expires_in_seconds(expires_at) < TOKEN_SAFETY_WINDOW_SECONDS


  
def refresh_tokens(db: Session, auth_client: AuthClient, realm_id: str, refresh_token: str, env: str):
    """
    Refresh tokens with Intuit and persist the rotated refresh token.
    Intuit rotates the refresh token on every refresh.
    """
    lock_key = f"lock:refresh_token:{realm_id}"  # Clave única para el lock
    lock = RedisLock(redis_client, lock_key)

    # Intentar obtener el lock
    if lock.acquire():
        try:
            # Si el lock es adquirido, procede con el refresh de los tokens
            print(f"Acquired lock for refreshing tokens for realm_id {realm_id}")

            auth_client.refresh(refresh_token)

            # Access token + expiry
            access_token = auth_client.access_token
            access_expires_in = getattr(auth_client, "expires_in", None) or getattr(auth_client, "access_token_expires_in", 3600)
            access_expires_at = now_utc() + dt.timedelta(seconds=int(access_expires_in))

            # New refresh token + expiry
            new_refresh = auth_client.refresh_token
            refresh_expires_in = getattr(auth_client, "x_refresh_token_expires_in", None) or getattr(auth_client, "refresh_token_expires_in", 100 * 24 * 3600)
            new_refresh_expires_at = now_utc() + dt.timedelta(seconds=int(refresh_expires_in))

            # Persist tokens
            upsert_tokens(
                db=db,
                realm_id=realm_id,
                environment=env,
                access_token=access_token,
                access_token_expires_at=access_expires_at,
                refresh_token=new_refresh,
                refresh_token_expires_at=new_refresh_expires_at,
                scopes="accounting",
            )

            print(f"Tokens refreshed successfully for realm_id {realm_id}")

            return access_token, access_expires_at, new_refresh, new_refresh_expires_at
        finally:
            # Siempre libera el lock al final del proceso
            lock.release()
            print(f"Released lock for refreshing tokens for realm_id {realm_id}")
    else:
        # Si no se pudo adquirir el lock, espera o aborta
        print(f"Lock already acquired for realm_id {realm_id}. Skipping token refresh.")
        return None


def get_qbo_client(realm_id: str, db: Session) -> QuickBooks:
    """
    Returns a QuickBooks client with valid tokens.
    Automatically refreshes & persists tokens when needed.
    """
    record = get_decrypted_tokens(db, realm_id)
    if not record:
        raise BusinessValidationError("QuickBooks is not connected yet. Go to /qbo/connect")

    # normalize DB datetimes to avoid naive/aware subtraction errors
    record["access_token_expires_at"]  = ensure_aware(record["access_token_expires_at"])
    record["refresh_token_expires_at"] = ensure_aware(record["refresh_token_expires_at"])

    env = record["environment"] or QUICKBOOKS_ENV
    auth_client = get_auth_client()

    if needs_refresh(record["access_token_expires_at"]) or not record["access_token"]:
        if not record["refresh_token"]:
            raise BusinessValidationError("Missing refresh token. Reconnect QuickBooks at /qbo/connect")

        # Asegúrate de que no se refresquen los tokens simultáneamente
        lock_key = f"lock:refresh_token:{realm_id}"
        lock = RedisLock(redis_client, lock_key)

        if lock.acquire():
            try:
                # Si el lock se adquiere, refresca los tokens
                refresh_tokens(db, auth_client, realm_id, record["refresh_token"], env)
            finally:
                # Libera el lock después de refrescar los tokens
                lock.release()
        else:
            # Si ya hay otro proceso refrescando los tokens, simplemente usa los tokens existentes
            print(f"Lock already acquired for token refresh for realm_id {realm_id}. Using existing tokens.")

    else:
        # reuse current tokens
        auth_client.access_token = record["access_token"]
        auth_client.refresh_token = record["refresh_token"]

    # IMPORTANT: QuickBooks ctor wants company_id, not realm_id
    qb = QuickBooks(
        auth_client=auth_client,
        company_id=realm_id,
        refresh_token=auth_client.refresh_token,
        sandbox=(env == "sandbox"),
    )
    return qb

