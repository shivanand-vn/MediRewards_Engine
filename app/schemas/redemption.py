from pydantic import BaseModel, Field
from datetime import datetime

class RedemptionRequest(BaseModel):
    user_id: str = Field(..., min_length=1, description="ID of the user redeeming the reward")
    reward_id: int = Field(..., description="ID of the reward to redeem")

class RedemptionResponse(BaseModel):
    redemption_id: int
    user_id: str
    reward_id: int
    reward_name: str
    points_spent: int
    updated_balance: int
    redeemed_at: datetime
