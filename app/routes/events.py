from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List

from app.database import get_db
from app.models.event import Event
from app.schemas.event import EventCreate, EventResponse
from app.schemas.balance import BalanceResponse
from app.schemas.ledger import LedgerEntryResponse
from app.services.rules_engine import RulesEngine
from app.services.ledger_service import LedgerService
from app.utils.tz import ensure_utc_naive

router = APIRouter()
rules_engine = RulesEngine()

@router.post("/events", response_model=None)
def create_event(event_in: EventCreate, db: Session = Depends(get_db)):
    """
    Processes a loyalty event, calculates points, records credit to ledger.
    Handles duplicate events gracefully using strict database constraints.
    """
    # Quick pre-check for idempotency (non-blocking)
    existing_event = db.query(Event).filter(Event.event_id == event_in.event_id).first()
    if existing_event:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Event already processed"}
        )

    # Validate repeat purchase criteria if applicable
    if event_in.event_type == "repeat_purchase":
        has_prior = rules_engine.validate_repeat_purchase(db, event_in.user_id, event_in.timestamp)
        if not has_prior:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Repeat purchase event requires a previous purchase within 30 days."
            )

    # Calculate loyalty points
    try:
        points = rules_engine.calculate_points(
            event_type=event_in.event_type,
            amount=event_in.amount,
            timestamp=event_in.timestamp
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    # Normalize event timestamp to UTC naive for consistent database storage
    db_timestamp = ensure_utc_naive(event_in.timestamp)

    # Create event record
    db_event = Event(
        event_id=event_in.event_id,
        user_id=event_in.user_id,
        event_type=event_in.event_type,
        amount=event_in.amount,
        timestamp=db_timestamp,
        status="processed"
    )
    db.add(db_event)

    # Try flushing to catch unique constraints violations (concurrency protection)
    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Event already processed"}
        )

    # Create compensating/credit ledger entry
    LedgerService.record_entry(
        db=db,
        user_id=event_in.user_id,
        entry_type="CREDIT",
        points=points,
        event_id=event_in.event_id
    )

    try:
        db.commit()
        db.refresh(db_event)
    except IntegrityError:
        db.rollback()
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Event already processed"}
        )

    # Return structured response manually to include points_awarded
    return EventResponse(
        event_id=db_event.event_id,
        user_id=db_event.user_id,
        event_type=db_event.event_type,
        amount=db_event.amount,
        timestamp=db_event.timestamp,
        points_awarded=points,
        status=db_event.status,
        created_at=db_event.created_at
    )

@router.get("/users/{user_id}/balance", response_model=BalanceResponse)
def get_user_balance(user_id: str, db: Session = Depends(get_db)):
    """
    Calculates the user's current loyalty point balance.
    """
    balance = LedgerService.get_balance(db, user_id)
    return BalanceResponse(user_id=user_id, balance=balance)

@router.get("/users/{user_id}/ledger", response_model=List[LedgerEntryResponse])
def get_user_ledger(user_id: str, db: Session = Depends(get_db)):
    """
    Returns the complete list of ledger entries for a user, ordered by date.
    """
    return LedgerService.get_ledger(db, user_id)
