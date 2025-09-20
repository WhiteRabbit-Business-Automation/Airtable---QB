import datetime as dt
import redis
from sqlalchemy.orm import Session
from intuitlib.client import AuthClient
from quickbooks import QuickBooks
import time
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
    Uses a Redis lock to prevent concurrent refreshes.
    """
    lock_key = f"lock:refresh_token:{realm_id}"
    lock = RedisLock(redis_client, lock_key, ttl=10)  # TTL 10s para evitar locks pegados

    if lock.acquire():
        try:
            print(f"Acquired lock for refreshing tokens for realm_id {realm_id}")

            if not refresh_token:
                raise ValueError("No refresh token provided")

            # Refresh the tokens with QuickBooks
            auth_client.refresh(refresh_token)

            # Access token + expiry
            access_token = auth_client.access_token
            access_expires_in = getattr(auth_client, "expires_in", None) or getattr(auth_client, "access_token_expires_in", 3600)
            access_expires_at = now_utc() + dt.timedelta(seconds=int(access_expires_in))

            # Refresh token + expiry
            new_refresh = auth_client.refresh_token
            refresh_expires_in = getattr(auth_client, "x_refresh_token_expires_in", None) or getattr(auth_client, "refresh_token_expires_in", 100 * 24 * 3600)
            new_refresh_expires_at = now_utc() + dt.timedelta(seconds=int(refresh_expires_in))

            # Persist tokens in DB
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
            lock.release()
            print(f"Released lock for refreshing tokens for realm_id {realm_id}")
    else:
        # Lock ocupado: espera a que el otro worker termine y lea los tokens de DB
        print(f"Lock already acquired for realm_id {realm_id}. Waiting for tokens...")
        timeout = 5  # segundos
        start = time.time()
        while time.time() - start < timeout:
            record = get_decrypted_tokens(db, realm_id)
            if record and record.get("refresh_token"):
                return (
                    record.get("access_token"),
                    record.get("access_token_expires_at"),
                    record.get("refresh_token"),
                    record.get("refresh_token_expires_at")
                )
            time.sleep(0.5)
        raise ValueError("Refresh token not available after waiting for lock release")


def get_qbo_client(realm_id: str, db: Session) -> QuickBooks:
    """
    Returns a QuickBooks client with valid tokens.
    Automatically refreshes & persists tokens when needed.
    """
    record = get_decrypted_tokens(db, realm_id)
    if not record:
        raise BusinessValidationError("QuickBooks is not connected yet. Go to /qbo/connect")

    # Normalize datetimes
    record["access_token_expires_at"] = ensure_aware(record["access_token_expires_at"])
    record["refresh_token_expires_at"] = ensure_aware(record["refresh_token_expires_at"])

    env = record.get("environment") or QUICKBOOKS_ENV
    auth_client = get_auth_client()

    # Si el access token está expirado o no existe
    if needs_refresh(record["access_token_expires_at"]) or not record["access_token"]:
        if not record.get("refresh_token"):
            raise BusinessValidationError("Missing refresh token. Reconnect QuickBooks at /qbo/connect")

        # Refresca tokens usando lock
        access_token, access_expires_at, refresh_token, refresh_expires_at = refresh_tokens(
            db, auth_client, realm_id, record["refresh_token"], env
        )
        auth_client.access_token = access_token
        auth_client.refresh_token = refresh_token
    else:
        # Reusa tokens existentes
        auth_client.access_token = record["access_token"]
        auth_client.refresh_token = record["refresh_token"]

    # Construye cliente QuickBooks
    qb = QuickBooks(
        auth_client=auth_client,
        company_id=realm_id,
        refresh_token=auth_client.refresh_token,
        sandbox=(env == "sandbox"),
    )
    return qb
