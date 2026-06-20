from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.reward import Reward
from app.schemas.reward import RewardResponse

router = APIRouter()

@router.get("/rewards", response_model=List[RewardResponse])
def list_rewards(db: Session = Depends(get_db)):
    """
    Returns all available rewards in the catalog.
    """
    return db.query(Reward).all()
