"""Domain-specific exceptions for the banking application."""

class BankingError(Exception):
    """Base class for expected banking errors."""

class InvalidAmountError(BankingError):
    """Raised when a monetary amount is invalid."""

class InsufficientFundsError(BankingError):
    """Raised when a withdrawal exceeds the permitted balance/overdraft."""

class AccountNotFoundError(BankingError):
    """Raised when an account number cannot be found."""

class CustomerNotFoundError(BankingError):
    """Raised when a customer ID cannot be found."""

class DuplicateCustomerError(BankingError):
    """Raised when a customer ID is already registered."""

class DuplicateAccountError(BankingError):
    """Raised when an account number is already registered."""

class InvalidCustomerError(BankingError):
    """Raised when customer information is invalid."""

class StorageError(BankingError):
    """Raised when the application cannot safely save or load data."""
