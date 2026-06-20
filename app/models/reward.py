from sqlalchemy import Column, Integer, String
from app.database import Base

class Reward(Base):
    __tablename__ = "rewards"

    id = Column(Integer, primary_key=True, index=True)
    reward_name = Column(String, nullable=False, unique=True)
    points_required = Column(Integer, nullable=False)
    reward_type = Column(String, nullable=False)
