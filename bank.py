"""Bank service: account operations, transaction history and TXT persistence."""
from pathlib import Path
from uuid import uuid4
from customer import Customer
from savings_account import SavingsAccount
from current_account import CurrentAccount
from account import money
from transaction import make_transaction
from storage import save_snapshot, load_snapshot
from exceptions import (
    AccountNotFoundError, CustomerNotFoundError, DuplicateAccountError,
    DuplicateCustomerError, InvalidAmountError, StorageError
)

class Bank:
    def __init__(self, bank_name, data_file=None, load_existing=True):
        self.bank_name = bank_name
        self.customers = {}
        self.accounts = {}
        default_path = Path(__file__).resolve().parent / "data" / "bank_data.txt"
        self.data_file = Path(data_file) if data_file else default_path
        if load_existing:
            self.load_data()

    def add_customer(self, customer):
        key = customer.customer_id
        if key in self.customers:
            raise DuplicateCustomerError(f"Customer ID {key} already exists.")
        self.customers[key] = customer
        try:
            self.save_data()
        except Exception:
            self.customers.pop(key, None)
            raise
        return customer

    def _get_customer(self, customer_id):
        # Accept numeric IDs from JSON forms while retaining one canonical integer key.
        key = int(customer_id) if str(customer_id).isdigit() else customer_id
        if key not in self.customers:
            raise CustomerNotFoundError("Customer not found.")
        return self.customers[key]

    def _create_account(self, account_number, customer_id, balance, account_class):
        account_number = str(account_number).strip()
        if not account_number:
            raise ValueError("Account number is required.")
        if account_number in self.accounts:
            raise DuplicateAccountError("Account number already exists.")
        customer = self._get_customer(customer_id)
        account = account_class(account_number, customer, balance)
        self.accounts[account_number] = account
        try:
            self.save_data()
        except Exception:
            self.accounts.pop(account_number, None)
            raise
        return account

    def create_savings_account(self, account_number, customer_id, balance=0):
        return self._create_account(account_number, customer_id, balance, SavingsAccount)

    def create_current_account(self, account_number, customer_id, balance=0):
        return self._create_account(account_number, customer_id, balance, CurrentAccount)

    def find_account(self, account_number):
        account = self.accounts.get(str(account_number).strip())
        if account is None:
            raise AccountNotFoundError("Account not found.")
        return account

    def deposit_money(self, account_number, amount):
        account = self.find_account(account_number)
        return account.deposit(amount, persist_callback=self.save_data)

    def withdraw_money(self, account_number, amount):
        account = self.find_account(account_number)
        return account.withdraw(amount, persist_callback=self.save_data)

    def transfer_money(self, sender_number, receiver_number, amount):
        sender_number, receiver_number = str(sender_number).strip(), str(receiver_number).strip()
        if sender_number == receiver_number:
            raise ValueError("Sender and receiver accounts must be different.")
        sender = self.find_account(sender_number)
        receiver = self.find_account(receiver_number)
        amount = money(amount, allow_zero=False)
        # Validate sender policy before mutating either account.
        if amount > sender.balance_decimal + getattr(sender, "overdraft_limit", 0):
            from exceptions import InsufficientFundsError
            raise InsufficientFundsError("Sender has insufficient funds or overdraft capacity.")
        sender_old, receiver_old = sender._balance, receiver._balance
        sender_len, receiver_len = len(sender.transactions), len(receiver.transactions)
        transaction_id = str(uuid4())
        sender._balance -= amount
        receiver._balance += amount
        sender._record("transfer_out", amount, receiver_number, transaction_id)
        receiver._record("transfer_in", amount, sender_number, transaction_id)
        try:
            self.save_data()
        except Exception:
            sender._balance, receiver._balance = sender_old, receiver_old
            del sender.transactions[sender_len:]
            del receiver.transactions[receiver_len:]
            raise
        return {"sender_balance": sender.get_balance(), "receiver_balance": receiver.get_balance()}

    def account_statement(self, account_number):
        account = self.find_account(account_number)
        return {
            "account_number": account.account_number,
            "customer_name": account.customer.name,
            "account_type": account.account_type,
            "balance": account.get_balance(),
            "transactions": list(account.transactions),
        }

    def calculate_interest(self, account_number):
        return self.find_account(account_number).calculate_interest()

    @property
    def total_transactions(self):
        # One transfer is one business transaction, despite two account-history entries.
        ids = set()
        for account in self.accounts.values():
            for item in account.transactions:
                if item["type"] != "opening_balance":
                    ids.add(item["transaction_id"])
        return len(ids)

    def save_data(self):
        payload = {
            "bank_name": self.bank_name,
            "customers": [customer.to_dict() for customer in self.customers.values()],
            "accounts": [account.to_dict() for account in self.accounts.values()],
        }
        save_snapshot(self.data_file, payload)

    def load_data(self):
        payload = load_snapshot(self.data_file)
        if payload is None:
            return
        try:
            customers = {
                item["customer_id"]: Customer.from_dict(item)
                for item in payload.get("customers", [])
            }
            accounts = {}
            for item in payload.get("accounts", []):
                customer_id = item["customer_id"]
                if customer_id not in customers:
                    raise ValueError(f"Account {item.get('account_number')} has no customer.")
                customer = customers[customer_id]
                kind = item["account_type"]
                policy = item.get("policy", {})
                if kind == "savings":
                    account = SavingsAccount(
                        item["account_number"], customer, item["balance"],
                        policy.get("interest_rate", "0.04")
                    )
                elif kind == "current":
                    account = CurrentAccount(
                        item["account_number"], customer, item["balance"],
                        policy.get("overdraft_limit", "5000.00")
                    )
                else:
                    raise ValueError(f"Unknown account type: {kind}")
                account.transactions = item.get("transactions", [])
                accounts[account.account_number] = account
            self.customers, self.accounts = customers, accounts
            self.bank_name = payload.get("bank_name", self.bank_name)
        except Exception as exc:
            raise StorageError(f"Bank data is invalid; it was not overwritten: {exc}") from exc

    def display_all_accounts(self):
        if not self.accounts:
            print("No accounts available.")
            return
        for account in self.accounts.values():
            print(f"\nAccount Number: {account.account_number}")
            print(f"Customer Name: {account.customer.name}")
            print(f"Balance: ₹{account.get_balance():.2f}")
            account.display_account_type()
