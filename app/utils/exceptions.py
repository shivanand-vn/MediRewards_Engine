class BusinessException(Exception):
    """Base class for all business logic exceptions."""
    pass

class RewardNotFoundError(BusinessException):
    """Raised when a requested reward does not exist."""
    pass

class InsufficientBalanceError(BusinessException):
    """Raised when a user attempts redemption with insufficient points balance."""
    pass

class EventNotFoundError(BusinessException):
    """Raised when reversing an event that does not exist."""
    pass

class EventAlreadyReversedError(BusinessException):
    """Raised when trying to reverse an event that has already been reversed."""
    pass

class InvalidEventError(BusinessException):
    """Raised when an event fails validation (e.g., repeat purchase with no prior purchases)."""
    pass
