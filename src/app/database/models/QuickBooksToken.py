from sqlalchemy import Column, String, DateTime, UniqueConstraint, func
from ..engine import Base

class QboConnection(Base):
    __tablename__ = "qbo_connections"

    # QuickBooks calls this the "realmId" (aka company id)
    realm_id = Column(String, primary_key=True, index=True)

    # Current access token + its expiration
    access_token = Column(String, nullable=True)
    access_token_expires_at = Column(DateTime, nullable=True)

    # Refresh token (rotates on every refresh) + its expiration (approx 100 days after last refresh)
    refresh_token = Column(String, nullable=False)
    refresh_token_expires_at = Column(DateTime, nullable=True)

    environment = Column(String, nullable=True)  # 'sandbox' | 'production'
    scopes = Column(String, nullable=True)

    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint('realm_id', name='uq_qbo_realm'),
    )
