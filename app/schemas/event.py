from pydantic import BaseModel, ConfigDict, Field, field_validator
from datetime import datetime

class EventCreate(BaseModel):
    event_id: str = Field(..., min_length=1, description="Unique event identifier")
    user_id: str = Field(..., min_length=1, description="User identifier")
    event_type: str = Field(..., description="Event type (medicine_purchase, referral, subscription_purchase, repeat_purchase)")
    amount: float = Field(..., description="Purchase or event amount")
    timestamp: datetime = Field(..., description="Timestamp of the event in ISO 8601 format")

    @field_validator("amount")
    def amount_must_be_non_negative(cls, v):
        if v < 0:
            raise ValueError("Amount cannot be negative")
        return v

    @field_validator("event_type")
    def validate_event_type(cls, v):
        allowed_types = {"medicine_purchase", "referral", "subscription_purchase", "repeat_purchase"}
        if v not in allowed_types:
            raise ValueError(f"Invalid event_type. Allowed types: {', '.join(allowed_types)}")
        return v

class EventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    event_id: str
    user_id: str
    event_type: str
    amount: float
    timestamp: datetime
    points_awarded: int
    status: str
    created_at: datetime

