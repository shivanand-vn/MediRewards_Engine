from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class LedgerEntryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: str
    event_id: Optional[str]
    entry_type: str
    points: int
    reference_id: Optional[str]
    created_at: datetime

