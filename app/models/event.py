from sqlalchemy import Column, Integer, String, Float, DateTime, func
from app.database import Base

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(String, index=True, nullable=False)
    event_type = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    status = Column(String, nullable=False, default="processed")  # "processed" or "reversed"
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
