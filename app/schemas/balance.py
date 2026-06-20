from pydantic import BaseModel

class BalanceResponse(BaseModel):
    user_id: str
    balance: int
