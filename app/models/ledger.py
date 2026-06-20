from sqlalchemy import Column, Integer, String, DateTime, func
from app.database import Base

class LedgerEntry(Base):
    __tablename__ = "ledger"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    event_id = Column(String, index=True, nullable=True)  # Nullable, e.g., for redemption DEBITs
    entry_type = Column(String, nullable=False)  # "CREDIT", "DEBIT", "REVERSAL"
    points = Column(Integer, nullable=False)  # Signed points value (+ve for credit, -ve for debit/reversal)
    reference_id = Column(String, nullable=True)  # Reference to redemption ID or reversed ledger ID
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
