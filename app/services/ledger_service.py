from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.ledger import LedgerEntry
from typing import List, Optional

class LedgerService:
    @staticmethod
    def get_balance(db: Session, user_id: str) -> int:
        """
        Dynamically calculates the user's loyalty point balance by summing ledger entries.
        """
        balance = db.query(func.sum(LedgerEntry.points)).filter(LedgerEntry.user_id == user_id).scalar()
        return balance if balance is not None else 0

    @staticmethod
    def record_entry(
        db: Session,
        user_id: str,
        entry_type: str,
        points: int,
        event_id: Optional[str] = None,
        reference_id: Optional[str] = None
    ) -> LedgerEntry:
        """
        Creates and persists a new ledger entry.
        """
        entry = LedgerEntry(
            user_id=user_id,
            event_id=event_id,
            entry_type=entry_type,
            points=points,
            reference_id=reference_id
        )
        db.add(entry)
        db.flush()  # Flushes to get the auto-generated id
        return entry

    @staticmethod
    def get_ledger(db: Session, user_id: str) -> List[LedgerEntry]:
        """
        Retrieves the complete transaction history for a user, ordered by creation date descending.
        """
        return db.query(LedgerEntry).filter(LedgerEntry.user_id == user_id).order_by(LedgerEntry.created_at.desc(), LedgerEntry.id.desc()).all()
