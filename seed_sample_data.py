import datetime
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.models.event import Event
from app.models.ledger import LedgerEntry
from app.models.reward import Reward
from app.models.redemption import Redemption

def seed_sample_data():
    print("Connecting to the database...")
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    try:
        # Check if we already seeded sample data to avoid duplicates
        existing_event = db.query(Event).filter(Event.event_id == "EVT101").first()
        if existing_event:
            print("Sample data is already present in the database.")
            return

        # Seed rewards if not present
        rewards_to_seed = [
            {"reward_name": "Free Delivery Coupon", "points_required": 100, "reward_type": "delivery_coupon"},
            {"reward_name": "Wallet Credit ₹50", "points_required": 250, "reward_type": "wallet_credit"},
            {"reward_name": "Wallet Credit ₹100", "points_required": 500, "reward_type": "wallet_credit"},
            {"reward_name": "Wallet Credit ₹200", "points_required": 1000, "reward_type": "wallet_credit"},
            {"reward_name": "Premium Membership", "points_required": 1500, "reward_type": "premium_membership"},
        ]
        for r_data in rewards_to_seed:
            existing = db.query(Reward).filter(Reward.reward_name == r_data["reward_name"]).first()
            if not existing:
                db.add(Reward(**r_data))
        db.commit()

        delivery_coupon = db.query(Reward).filter(Reward.reward_name == "Free Delivery Coupon").first()

        print("Seeding sample data for USER001...")
        # 1. USER001 - Medicine Purchase (Saturday 2026-06-20 -> earns 55 points)
        evt101 = Event(
            event_id="EVT101",
            user_id="USER001",
            event_type="medicine_purchase",
            amount=2500.0,
            timestamp=datetime.datetime(2026, 6, 20, 10, 0, 0),
            status="processed"
        )
        db.add(evt101)
        db.flush()

        ledger101 = LedgerEntry(
            user_id="USER001",
            event_id="EVT101",
            entry_type="CREDIT",
            points=55,
            reference_id=None
        )
        db.add(ledger101)

        # 2. USER001 - Referral (Monday 2026-06-22 -> earns 50 points)
        evt102 = Event(
            event_id="EVT102",
            user_id="USER001",
            event_type="referral",
            amount=0.0,
            timestamp=datetime.datetime(2026, 6, 22, 12, 0, 0),
            status="processed"
        )
        db.add(evt102)
        db.flush()

        ledger102 = LedgerEntry(
            user_id="USER001",
            event_id="EVT102",
            entry_type="CREDIT",
            points=50,
            reference_id=None
        )
        db.add(ledger102)

        # 3. USER001 - Redeem Reward (Free Delivery Coupon -> costs 100 points)
        redemption101 = Redemption(
            user_id="USER001",
            reward_id=delivery_coupon.id,
            points_spent=100,
            redeemed_at=datetime.datetime(2026, 6, 23, 14, 0, 0)
        )
        db.add(redemption101)
        db.flush()

        ledger_red101 = LedgerEntry(
            user_id="USER001",
            event_id=None,
            entry_type="DEBIT",
            points=-100,
            reference_id=str(redemption101.id)
        )
        db.add(ledger_red101)


        print("Seeding sample data for USER002...")
        # 4. USER002 - Subscription Purchase (Sunday 2026-06-21 -> earns 75 points)
        evt201 = Event(
            event_id="EVT201",
            user_id="USER002",
            event_type="subscription_purchase",
            amount=3000.0,
            timestamp=datetime.datetime(2026, 6, 21, 10, 0, 0),
            status="processed"
        )
        db.add(evt201)
        db.flush()

        ledger201 = LedgerEntry(
            user_id="USER002",
            event_id="EVT201",
            entry_type="CREDIT",
            points=75,
            reference_id=None
        )
        db.add(ledger201)

        # 5. USER002 - Repeat Purchase (Wednesday 2026-06-24 -> earns 15 points)
        evt202 = Event(
            event_id="EVT202",
            user_id="USER002",
            event_type="repeat_purchase",
            amount=1000.0,
            timestamp=datetime.datetime(2026, 6, 24, 10, 0, 0),
            status="processed"
        )
        db.add(evt202)
        db.flush()

        ledger202 = LedgerEntry(
            user_id="USER002",
            event_id="EVT202",
            entry_type="CREDIT",
            points=15,
            reference_id=None
        )
        db.add(ledger202)

        # 6. USER002 - Medicine Purchase (Thursday 2026-06-25 -> earns 10 points, then reversed)
        evt203 = Event(
            event_id="EVT203",
            user_id="USER002",
            event_type="medicine_purchase",
            amount=200.0,
            timestamp=datetime.datetime(2026, 6, 25, 10, 0, 0),
            status="reversed" # Marked as reversed
        )
        db.add(evt203)
        db.flush()

        ledger203 = LedgerEntry(
            user_id="USER002",
            event_id="EVT203",
            entry_type="CREDIT",
            points=10,
            reference_id=None
        )
        db.add(ledger203)
        db.flush()

        ledger_rev203 = LedgerEntry(
            user_id="USER002",
            event_id="EVT203",
            entry_type="REVERSAL",
            points=-10,
            reference_id=str(ledger203.id)
        )
        db.add(ledger_rev203)

        db.commit()
        print("Database seeded with sample data successfully!")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_sample_data()
