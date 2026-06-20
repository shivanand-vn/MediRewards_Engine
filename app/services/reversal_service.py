from sqlalchemy.orm import Session
from app.models.event import Event
from app.models.ledger import LedgerEntry
from app.services.ledger_service import LedgerService
from app.utils.exceptions import EventNotFoundError, EventAlreadyReversedError

class ReversalService:
    @staticmethod
    def reverse_event(db: Session, event_id: str) -> tuple[int, int]:
        """
        Reverses a previously processed event by creating a compensating REVERSAL ledger entry.
        Allows the points balance to temporarily go negative to reflect business reality.
        Prevents double reversal.
        Returns a tuple of (points_reversed, new_balance).
        """
        # Fetch the event
        event = db.query(Event).filter(Event.event_id == event_id).first()
        if not event:
            raise EventNotFoundError(f"Event {event_id} not found")

        # Double reversal protection
        if event.status == "reversed":
            raise EventAlreadyReversedError(f"Event {event_id} has already been reversed")

        # Find the original CREDIT ledger entry to determine the exact points to compensate
        original_entry = db.query(LedgerEntry).filter(
            LedgerEntry.event_id == event_id,
            LedgerEntry.entry_type == "CREDIT"
        ).first()

        if not original_entry:
            # Fallback if ledger entry was missing (should not happen in healthy system)
            raise EventNotFoundError(f"Original ledger credit entry for event {event_id} not found")

        points_to_reverse = original_entry.points

        # Update event status
        event.status = "reversed"

        # Record compensating REVERSAL ledger entry
        # points is negative of original credit points
        LedgerService.record_entry(
            db=db,
            user_id=event.user_id,
            entry_type="REVERSAL",
            points=-points_to_reverse,
            event_id=event_id,
            reference_id=str(original_entry.id)
        )

        db.flush()

        # Calculate new balance
        new_balance = LedgerService.get_balance(db, event.user_id)

        return points_to_reverse, new_balance
