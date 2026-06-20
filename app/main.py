from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from app.database import Base, engine, SessionLocal
from app.models.reward import Reward
from app.routes import events, rewards, redemption, reversal

def seed_rewards(db):
    """
    Seeds the default rewards catalog during application startup if not already seeded.
    """
    rewards_to_seed = [
        {
            "reward_name": "Free Delivery Coupon",
            "points_required": 100,
            "reward_type": "delivery_coupon"
        },
        {
            "reward_name": "Wallet Credit ₹50",
            "points_required": 250,
            "reward_type": "wallet_credit"
        },
        {
            "reward_name": "Wallet Credit ₹100",
            "points_required": 500,
            "reward_type": "wallet_credit"
        },
        {
            "reward_name": "Wallet Credit ₹200",
            "points_required": 1000,
            "reward_type": "wallet_credit"
        },
        {
            "reward_name": "Premium Membership",
            "points_required": 1500,
            "reward_type": "premium_membership"
        }
    ]

    for r_data in rewards_to_seed:
        existing = db.query(Reward).filter(Reward.reward_name == r_data["reward_name"]).first()
        if not existing:
            reward = Reward(
                reward_name=r_data["reward_name"],
                points_required=r_data["points_required"],
                reward_type=r_data["reward_type"]
            )
            db.add(reward)
    db.commit()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Automatically create database tables (migrations) on startup
    Base.metadata.create_all(bind=engine)
    
    # Seed default rewards catalog
    db = SessionLocal()
    try:
        seed_rewards(db)
    finally:
        db.close()
    yield

app = FastAPI(
    title="MediRewards_Engine",
    description="A production-quality loyalty and rewards backend management system.",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")

# Register routes
app.include_router(events.router)
app.include_router(rewards.router)
app.include_router(redemption.router)
app.include_router(reversal.router)
