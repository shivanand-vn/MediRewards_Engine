import os
import json
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.event import Event
from app.utils.tz import ensure_utc_naive

class RulesEngine:
    def __init__(self, config_path: str = None):
        if config_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            config_path = os.path.join(base_dir, "config", "rules.json")
        
        with open(config_path, "r", encoding="utf-8") as f:
            self.rules = json.load(f)

    def calculate_points(self, event_type: str, amount: float, timestamp: datetime) -> int:
        """
        Calculates awarded loyalty points based on rules config (base + bonuses) capped at max per event.
        """
        base_points_config = self.rules.get("base_points", {})
        if event_type not in base_points_config:
            raise ValueError(f"Unknown event type: {event_type}")

        points = base_points_config[event_type]

        # Apply bonuses
        bonuses = self.rules.get("bonuses", {})

        # High value purchase bonus
        high_value = bonuses.get("high_value_purchase", {})
        if high_value:
            min_amount = high_value.get("minimum_amount", 2000)
            bonus_pts = high_value.get("bonus_points", 20)
            if amount >= min_amount:
                points += bonus_pts

        # Weekend purchase bonus (Saturday = 5, Sunday = 6 in python's weekday())
        weekend = bonuses.get("weekend_purchase", {})
        if weekend:
            min_amount = weekend.get("minimum_amount", 500)
            bonus_pts = weekend.get("bonus_points", 25)
            if amount >= min_amount and timestamp.weekday() in (5, 6):
                points += bonus_pts

        # Cap points per event
        max_points = self.rules.get("max_points_per_event", 100)
        if points > max_points:
            points = max_points

        return points

    def validate_repeat_purchase(self, db: Session, user_id: str, current_timestamp: datetime) -> bool:
        """
        Validates whether the user has a previous purchase within 30 days of the current event's timestamp.
        """
        # Normalize timestamps to UTC for DB queries
        db_current_ts = ensure_utc_naive(current_timestamp)
        thirty_days_ago = db_current_ts - timedelta(days=30)

        purchase_types = ["medicine_purchase", "subscription_purchase", "repeat_purchase"]

        # Search for any processed purchase event in the last 30 days prior to current_timestamp
        exists = db.query(Event).filter(
            Event.user_id == user_id,
            Event.event_type.in_(purchase_types),
            Event.status == "processed",
            Event.timestamp >= thirty_days_ago,
            Event.timestamp < db_current_ts
        ).first() is not None

        return exists
