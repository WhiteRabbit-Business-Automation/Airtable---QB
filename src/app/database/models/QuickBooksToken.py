from sqlalchemy import Column, String, Integer, DateTime, UniqueConstraint, func
from app.database.engine import Base

class QboConnection(Base):
    __tablename__ = "qbo_connections"
    # realmId of QuickBooks (company_id) as PK
    company_id = Column(String(64), primary_key=True, index=True)
    # refresh token (see below for encrypted variant)
    refresh_token = Column(String(4096), nullable=False)
    # optional: scopes, environment, etc.
    environment = Column(String(32), nullable=True)
    scopes = Column(String(512), nullable=True)

    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint('company_id', name='uq_qbo_company'),
    )
