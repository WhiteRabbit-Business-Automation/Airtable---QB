from typing import Optional
from sqlalchemy.orm import Session
from app.database.models.QuickBooksToken import QboConnection
from app.security.fernet import encrypt, decrypt

def get_connection_by_realm(db: Session, realm_id: str) -> Optional[QboConnection]:
    return db.query(QboConnection).filter_by(realm_id=realm_id).first()

def upsert_tokens(
    db: Session,
    *,
    realm_id: str,
    environment: str,
    access_token: Optional[str],
    access_token_expires_at,
    refresh_token: str,
    refresh_token_expires_at,
    scopes: Optional[str] = None,
) -> QboConnection:
    """
    Upsert both access/refresh tokens and expirations.
    Tokens are stored encrypted at rest.
    """
    obj = get_connection_by_realm(db, realm_id)
    if obj is None:
        obj = QboConnection(
            realm_id=realm_id,
            environment=environment,
            scopes=scopes,
        )
        db.add(obj)

    # Always update tokens/expirations we were given
    if access_token is not None:
        obj.access_token = encrypt(access_token)
    obj.access_token_expires_at = access_token_expires_at

    obj.refresh_token = encrypt(refresh_token)
    obj.refresh_token_expires_at = refresh_token_expires_at

    if environment:
        obj.environment = environment
    if scopes:
        obj.scopes = scopes

    db.commit()
    db.refresh(obj)
    return obj

def upsert_refresh_token(
    db: Session,
    realm_id: str,
    refresh_token: str,
    environment: Optional[str] = None,
    scopes: Optional[str] = None,
    refresh_token_expires_at=None,
) -> QboConnection:
    """
    Minimal upsert for refresh-only flows (kept for compatibility).
    """
    obj = get_connection_by_realm(db, realm_id)
    if obj is None:
        obj = QboConnection(
            realm_id=realm_id,
            environment=environment,
            scopes=scopes,
        )
        db.add(obj)

    obj.refresh_token = encrypt(refresh_token)
    if refresh_token_expires_at:
        obj.refresh_token_expires_at = refresh_token_expires_at

    if environment:
        obj.environment = environment
    if scopes:
        obj.scopes = scopes

    db.commit()
    db.refresh(obj)
    return obj

def get_refresh_token(db: Session, realm_id: str) -> Optional[str]:
    obj = get_connection_by_realm(db, realm_id)
    return decrypt(obj.refresh_token) if obj and obj.refresh_token else None

def get_decrypted_tokens(db: Session, realm_id: str):
    """
    Helper to load a connection and return decrypted tokens + all metadata.
    """
    obj = get_connection_by_realm(db, realm_id)
    if not obj:
        return None
    return {
        "realm_id": obj.realm_id,
        "environment": obj.environment,
        "scopes": obj.scopes,
        "access_token": decrypt(obj.access_token) if obj.access_token else None,
        "access_token_expires_at": obj.access_token_expires_at,
        "refresh_token": decrypt(obj.refresh_token) if obj.refresh_token else None,
        "refresh_token_expires_at": obj.refresh_token_expires_at,
    }
