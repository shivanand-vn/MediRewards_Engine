from sqlalchemy.orm import Session
from app.models.reward import Reward
from app.models.redemption import Redemption
from app.services.ledger_service import LedgerService
from app.utils.exceptions import RewardNotFoundError, InsufficientBalanceError

class RedemptionService:
    @staticmethod
    def redeem_reward(db: Session, user_id: str, reward_id: int) -> Redemption:
        """
        Redeems a reward for a user.
        Verifies that the reward exists, user balance is sufficient, creates the
        Redemption record, and records a DEBIT in the ledger.
        Runs inside an atomic transaction.
        """
        # Fetch reward
        reward = db.query(Reward).filter(Reward.id == reward_id).first()
        if not reward:
            raise RewardNotFoundError("Reward not found")

        # Verify sufficient balance
        balance = LedgerService.get_balance(db, user_id)
        if balance < reward.points_required:
            raise InsufficientBalanceError("Insufficient balance")

        # Create redemption record
        redemption = Redemption(
            user_id=user_id,
            reward_id=reward.id,
            points_spent=reward.points_required
        )
        db.add(redemption)
        db.flush()  # Populates redemption.id

        # Create DEBIT ledger entry
        LedgerService.record_entry(
            db=db,
            user_id=user_id,
            entry_type="DEBIT",
            points=-reward.points_required,
            event_id=None,
            reference_id=str(redemption.id)
        )

        return redemption
