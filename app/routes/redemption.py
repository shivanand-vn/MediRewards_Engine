from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.redemption import RedemptionRequest, RedemptionResponse
from app.services.redemption_service import RedemptionService
from app.services.ledger_service import LedgerService
from app.utils.exceptions import RewardNotFoundError, InsufficientBalanceError

router = APIRouter()

@router.post("/redeem", response_model=None)
def redeem_reward(payload: RedemptionRequest, db: Session = Depends(get_db)):
    """
    Deducts loyalty points to redeem a reward. Enforces non-negative balance constraints.
    """
    try:
        redemption = RedemptionService.redeem_reward(
            db=db,
            user_id=payload.user_id,
            reward_id=payload.reward_id
        )
        db.commit()
    except RewardNotFoundError:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": "Reward not found"}
        )
    except InsufficientBalanceError:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "Insufficient balance"}
        )
    except Exception as e:
        db.rollback()
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": f"An unexpected error occurred during redemption: {str(e)}"}
        )

    # Calculate the updated balance dynamically
    updated_balance = LedgerService.get_balance(db, payload.user_id)

    return RedemptionResponse(
        redemption_id=redemption.id,
        user_id=redemption.user_id,
        reward_id=redemption.reward_id,
        reward_name=redemption.reward.reward_name,
        points_spent=redemption.points_spent,
        updated_balance=updated_balance,
        redeemed_at=redemption.redeemed_at
    )
