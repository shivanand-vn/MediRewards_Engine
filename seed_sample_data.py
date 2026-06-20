import datetime
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.models.event import Event
from app.models.ledger import LedgerEntry
from app.models.reward import Reward
from app.models.redemption import Redemption

def seed_sample_data():
    print("Recreating database tables (wiping existing data)...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    db: Session = SessionLocal()

    try:
        # 1. Seed rewards catalog
        print("Seeding rewards catalog...")
        rewards_to_seed = [
            {"reward_name": "Free Delivery Coupon", "points_required": 100, "reward_type": "delivery_coupon"},
            {"reward_name": "Wallet Credit ₹50", "points_required": 250, "reward_type": "wallet_credit"},
            {"reward_name": "Wallet Credit ₹100", "points_required": 500, "reward_type": "wallet_credit"},
            {"reward_name": "Wallet Credit ₹200", "points_required": 1000, "reward_type": "wallet_credit"},
            {"reward_name": "Premium Membership", "points_required": 1500, "reward_type": "premium_membership"},
        ]
        rewards = {}
        for r_data in rewards_to_seed:
            reward = Reward(**r_data)
            db.add(reward)
            db.flush()
            rewards[r_data["reward_name"]] = reward
        db.commit()

        # Helper to log events and ledger entries
        def add_credit_event(user_id, event_id, event_type, amount, dt, points, is_reversed=False):
            evt = Event(
                event_id=event_id,
                user_id=user_id,
                event_type=event_type,
                amount=amount,
                timestamp=dt,
                status="reversed" if is_reversed else "processed"
            )
            db.add(evt)
            db.flush()
            
            ledger = LedgerEntry(
                user_id=user_id,
                event_id=event_id,
                entry_type="CREDIT",
                points=points,
                reference_id=None
            )
            db.add(ledger)
            db.flush()
            return ledger

        def add_reversal(user_id, event_id, original_ledger_id, points):
            ledger = LedgerEntry(
                user_id=user_id,
                event_id=event_id,
                entry_type="REVERSAL",
                points=-points,
                reference_id=str(original_ledger_id)
            )
            db.add(ledger)
            db.flush()

        def add_redemption(user_id, reward_name, points_spent, dt):
            reward = rewards[reward_name]
            red = Redemption(
                user_id=user_id,
                reward_id=reward.id,
                points_spent=points_spent,
                redeemed_at=dt
            )
            db.add(red)
            db.flush()
            
            ledger = LedgerEntry(
                user_id=user_id,
                event_id=None,
                entry_type="DEBIT",
                points=-points_spent,
                reference_id=str(red.id)
            )
            db.add(ledger)
            db.flush()

        # --- USER001 ---
        print("Seeding USER001...")
        # Medicine Purchase (Saturday -> earns 55 points)
        add_credit_event("USER001", "EVT101", "medicine_purchase", 2500.0, datetime.datetime(2026, 6, 20, 10, 0), 55)
        # Referral (Monday -> earns 50 points)
        add_credit_event("USER001", "EVT102", "referral", 0.0, datetime.datetime(2026, 6, 22, 12, 0), 50)
        # Redemption (Free Delivery Coupon -> costs 100 points)
        add_redemption("USER001", "Free Delivery Coupon", 100, datetime.datetime(2026, 6, 23, 14, 0))

        # --- USER002 ---
        print("Seeding USER002...")
        # Subscription Purchase (Sunday -> earns 75 points)
        add_credit_event("USER002", "EVT201", "subscription_purchase", 3000.0, datetime.datetime(2026, 6, 21, 10, 0), 75)
        # Repeat Purchase (Wednesday -> earns 15 points)
        add_credit_event("USER002", "EVT202", "repeat_purchase", 1000.0, datetime.datetime(2026, 6, 24, 10, 0), 15)
        # Medicine Purchase (Thursday -> earns 10 points, then reversed)
        led203 = add_credit_event("USER002", "EVT203", "medicine_purchase", 200.0, datetime.datetime(2026, 6, 25, 10, 0), 10, is_reversed=True)
        add_reversal("USER002", "EVT203", led203.id, 10)

        # --- USER003 (New User 1) ---
        print("Seeding USER003...")
        # Weekend high-value medicine purchase (Saturday -> earns 55 points)
        add_credit_event("USER003", "EVT301", "medicine_purchase", 2500.0, datetime.datetime(2026, 6, 20, 10, 0), 55)
        # Referral (Monday -> earns 50 points)
        add_credit_event("USER003", "EVT302", "referral", 0.0, datetime.datetime(2026, 6, 22, 12, 0), 50)
        # Redemption (Free Delivery Coupon -> costs 100 points)
        add_redemption("USER003", "Free Delivery Coupon", 100, datetime.datetime(2026, 6, 23, 14, 0))

        # --- USER004 (New User 2) ---
        print("Seeding USER004...")
        # Earns high points to redeem Wallet Credit
        add_credit_event("USER004", "EVT401", "subscription_purchase", 5000.0, datetime.datetime(2026, 6, 21, 10, 0), 75)
        add_credit_event("USER004", "EVT402", "medicine_purchase", 4000.0, datetime.datetime(2026, 6, 27, 10, 0), 55)
        add_credit_event("USER004", "EVT403", "referral", 0.0, datetime.datetime(2026, 6, 29, 12, 0), 50)
        add_credit_event("USER004", "EVT404", "referral", 0.0, datetime.datetime(2026, 6, 30, 12, 0), 50)
        add_credit_event("USER004", "EVT405", "repeat_purchase", 3000.0, datetime.datetime(2026, 7, 4, 10, 0), 60)
        # Redemption (Wallet Credit ₹50 -> costs 250 points)
        add_redemption("USER004", "Wallet Credit ₹50", 250, datetime.datetime(2026, 7, 5, 14, 0))

        # --- USER005 (New User 3) ---
        print("Seeding USER005...")
        # Regular small purchaser (no redemptions)
        add_credit_event("USER005", "EVT501", "medicine_purchase", 800.0, datetime.datetime(2026, 6, 22, 10, 0), 10)
        add_credit_event("USER005", "EVT502", "repeat_purchase", 900.0, datetime.datetime(2026, 6, 24, 10, 0), 15)
        add_credit_event("USER005", "EVT503", "repeat_purchase", 1200.0, datetime.datetime(2026, 6, 27, 10, 0), 40)

        # --- USER006 (New User 4) ---
        print("Seeding USER006...")
        # Reversal user (refunded order)
        led601 = add_credit_event("USER006", "EVT601", "medicine_purchase", 2500.0, datetime.datetime(2026, 6, 22, 10, 0), 30, is_reversed=True)
        add_reversal("USER006", "EVT601", led601.id, 30)
        add_credit_event("USER006", "EVT602", "referral", 0.0, datetime.datetime(2026, 6, 23, 12, 0), 50)

        # --- USER007 (New User 5) ---
        print("Seeding USER007...")
        # Capped high value purchaser + redemption
        add_credit_event("USER007", "EVT701", "subscription_purchase", 10000.0, datetime.datetime(2026, 6, 21, 10, 0), 75)
        add_credit_event("USER007", "EVT702", "referral", 0.0, datetime.datetime(2026, 6, 22, 12, 0), 50)
        # Redemption (Free Delivery Coupon -> costs 100 points)
        add_redemption("USER007", "Free Delivery Coupon", 100, datetime.datetime(2026, 6, 23, 14, 0))

        db.commit()
        print("Database seeded with sample data for all 7 users successfully!")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_sample_data()
