from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.reversal_service import ReversalService
from app.utils.exceptions import EventNotFoundError, EventAlreadyReversedError

router = APIRouter()

@router.post("/reverse/{event_id}", response_model=None)
def reverse_event(event_id: str, db: Session = Depends(get_db)):
    """
    Reverses an event, inserting a compensating ledger entry.
    Allows the points balance to temporarily go negative to reflect business reality.
    Enforces double reversal protection.
    """
    try:
        points_reversed, new_balance = ReversalService.reverse_event(db, event_id)
        db.commit()
    except EventNotFoundError as e:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": str(e)}
        )
    except EventAlreadyReversedError as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": str(e)}
        )
    except Exception as e:
        db.rollback()
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": f"An unexpected error occurred during reversal: {str(e)}"}
        )

    return {
        "message": "Event reversed successfully",
        "event_id": event_id,
        "points_reversed": points_reversed,
        "updated_balance": new_balance
    }
