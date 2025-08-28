from typing import Optional
from sqlalchemy.orm import Session
from app.database.models.QuickBooksToken import QboConnection

from app.security.fernet import encrypt, decrypt

def upsert_refresh_token(db: Session, company_id: str, refresh_token: str, environment=None, scopes=None):
    obj = db.get(QboConnection, company_id)
    if obj is None:
        obj = QboConnection(
            company_id=company_id,
            refresh_token=encrypt(refresh_token),
            environment=environment,
            scopes=scopes,
        )
        db.add(obj)
    else:
        obj.refresh_token = encrypt(refresh_token)
        if environment:
            obj.environment = environment
        if scopes:
            obj.scopes = scopes
    db.commit()
    db.refresh(obj)
    return obj

def get_refresh_token(db: Session, company_id: str) -> Optional[str]:
    obj = db.get(QboConnection, company_id)
    return decrypt(obj.refresh_token) if obj else None
