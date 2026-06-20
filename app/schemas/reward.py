from pydantic import BaseModel, ConfigDict

class RewardResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    reward_name: str
    points_required: int
    reward_type: str

