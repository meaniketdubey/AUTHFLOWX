from sqlalchemy import Column, Integer, String, DateTime, Boolean
from datetime import datetime


from app.core.database import Base

is_active = Column(Boolean, default=True)


class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer)

    refresh_token = Column(String, unique=True)

    device_info = Column(String)

    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    expires_at = Column(DateTime)           