"""Abstract bank account contract with validated monetary operations."""
from abc import ABC, abstractmethod
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
import math
from exceptions import InvalidAmountError, InsufficientFundsError
from transaction import make_transaction

CENT = Decimal("0.01")

def money(value, *, allow_zero=True):
    try:
        if isinstance(value, bool):
            raise InvalidOperation
        # Reject NaN and +/- infinity before quantizing.
        if isinstance(value, float) and not math.isfinite(value):
            raise InvalidOperation
        amount = Decimal(str(value))
        if not amount.is_finite():
            raise InvalidOperation
        amount = amount.quantize(CENT, rounding=ROUND_HALF_UP)
    except (InvalidOperation, ValueError, TypeError):
        raise InvalidAmountError("Enter a finite valid monetary amount.") from None
    if amount < 0 or (not allow_zero and amount <= 0):
        raise InvalidAmountError("Amount must be positive." if not allow_zero else "Amount cannot be negative.")
    return amount

class Account(ABC):
    def __init__(self, account_number, customer, balance=0):
        account_number = str(account_number).strip()
        if not account_number:
            raise ValueError("Account number is required.")
        self.account_number = account_number
        self.customer = customer
        self._balance = money(balance)
        self.transactions = []
        self._record("opening_balance", self._balance)

    def _record(self, kind, amount, counterparty=None, transaction_id=None):
        self.transactions.append(make_transaction(
            kind, amount, self._balance, counterparty, transaction_id
        ))

    def deposit(self, amount, *, persist_callback=None):
        amount = money(amount, allow_zero=False)
        old_balance = self._balance
        old_history_len = len(self.transactions)
        self._balance += amount
        self._record("deposit", amount)
        try:
            if persist_callback:
                persist_callback()
        except Exception:
            self._balance = old_balance
            del self.transactions[old_history_len:]
            raise
        return self._balance

    def withdraw(self, amount, *, persist_callback=None):
        amount = money(amount, allow_zero=False)
        if amount > self._balance:
            raise InsufficientFundsError("Insufficient balance.")
        old_balance = self._balance
        old_history_len = len(self.transactions)
        self._balance -= amount
        self._record("withdrawal", amount)
        try:
            if persist_callback:
                persist_callback()
        except Exception:
            self._balance = old_balance
            del self.transactions[old_history_len:]
            raise
        return self._balance

    def get_balance(self):
        return float(self._balance)

    @property
    def balance_decimal(self):
        return self._balance

    @abstractmethod
    def calculate_interest(self):
        """Return a preview of interest; this does not credit the account."""

    @abstractmethod
    def display_account_type(self):
        """Display account-specific policy information."""

    def to_dict(self):
        return {
            "account_number": self.account_number,
            "customer_id": self.customer.customer_id,
            "balance": f"{self._balance:.2f}",
            "transactions": self.transactions,
            "account_type": self.account_type,
            "policy": self.policy_dict(),
        }

    @abstractmethod
    def policy_dict(self):
        pass
