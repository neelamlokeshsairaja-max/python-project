"""Current account with a validated overdraft limit."""
from account import Account, money
from exceptions import InsufficientFundsError

class CurrentAccount(Account):
    account_type = "current"

    def __init__(self, account_number, customer, balance=0, overdraft_limit=5000):
        super().__init__(account_number, customer, balance)
        self.overdraft_limit = money(overdraft_limit)

    def withdraw(self, amount, *, persist_callback=None):
        amount = money(amount, allow_zero=False)
        if amount > self.balance_decimal + self.overdraft_limit:
            raise InsufficientFundsError("Overdraft limit exceeded.")
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
        return self.get_balance()

    def calculate_interest(self):
        # Current accounts earn no interest under this project's documented rule.
        return 0.0

    def display_account_type(self):
        print("Account Type: Current Account")
        print(f"Overdraft Limit: ₹{self.overdraft_limit:.2f}")

    def policy_dict(self):
        return {"overdraft_limit": f"{self.overdraft_limit:.2f}"}
