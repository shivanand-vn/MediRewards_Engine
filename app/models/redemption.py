from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.database import Base

class Redemption(Base):
    __tablename__ = "redemptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    reward_id = Column(Integer, ForeignKey("rewards.id"), nullable=False)
    points_spent = Column(Integer, nullable=False)
    redeemed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    reward = relationship("Reward")
