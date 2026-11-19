"""Savings account implementation."""
from decimal import Decimal
from account import Account, money
from exceptions import InvalidAmountError

class SavingsAccount(Account):
    account_type = "savings"

    def __init__(self, account_number, customer, balance=0, interest_rate=0.04):
        super().__init__(account_number, customer, balance)
        try:
            rate = Decimal(str(interest_rate))
            if not rate.is_finite() or rate < 0:
                raise ValueError
        except Exception:
            raise InvalidAmountError("Interest rate must be a finite nonnegative number.") from None
        self.interest_rate = rate

    def calculate_interest(self):
        # Simple annual interest preview for one annual period.
        return float((self.balance_decimal * self.interest_rate).quantize(Decimal("0.01")))

    def display_account_type(self):
        print("Account Type: Savings Account")
        print(f"Interest Rate: {self.interest_rate * 100}%")

    def policy_dict(self):
        return {"interest_rate": str(self.interest_rate)}
