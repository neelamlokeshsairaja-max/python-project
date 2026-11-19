"""Command-line interface for the Advanced Bank Management System."""
from bank import Bank
from customer import Customer
from exceptions import BankingError

def print_statement(bank, account_number):
    statement = bank.account_statement(account_number)
    print(f"\nStatement for {statement['account_number']} - {statement['customer_name']}")
    print(f"Type: {statement['account_type']} | Current balance: ₹{statement['balance']:.2f}")
    print("-" * 78)
    for item in statement["transactions"]:
        print(
            item["date"], item["type"], f"₹{float(item['amount']):.2f}",
            f"Balance: ₹{float(item['balance']):.2f}",
            f"Counterparty: {item['counterparty'] or '-'}"
        )

def main():
    bank = Bank("Lokesh National Bank")
    while True:
        print("""
===== ADVANCED BANK MANAGEMENT SYSTEM =====
1. Register Customer
2. Create Savings Account
3. Create Current Account
4. Deposit Money
5. Withdraw Money
6. Check Balance
7. Display All Accounts
8. Fund Transfer
9. Account Statement
10. Calculate Interest (preview)
11. Dashboard Summary
12. Exit
""")
        choice = input("Enter your choice: ").strip()
        try:
            if choice == "1":
                customer = Customer(
                    input("Customer ID: ").strip(),
                    input("Customer name: "),
                    input("Phone (10 digits): "),
                    input("Email: ")
                )
                bank.add_customer(customer)
                print("Customer registered successfully.")
            elif choice in ("2", "3"):
                account_no = input("Account number: ").strip()
                customer_id = input("Customer ID: ").strip()
                balance = input("Opening balance: ").strip() or "0"
                account = (bank.create_savings_account if choice == "2"
                           else bank.create_current_account)(account_no, customer_id, balance)
                print(f"{account.account_type.title()} account created successfully.")
            elif choice in ("4", "5"):
                account_no = input("Account number: ").strip()
                amount = input("Amount: ").strip()
                balance = (bank.deposit_money if choice == "4"
                           else bank.withdraw_money)(account_no, amount)
                print(f"Transaction successful. New balance: ₹{balance:.2f}")
            elif choice == "6":
                account = bank.find_account(input("Account number: "))
                print(f"Available balance: ₹{account.get_balance():.2f}")
            elif choice == "7":
                bank.display_all_accounts()
            elif choice == "8":
                sender = input("From account number: ").strip()
                receiver = input("To account number: ").strip()
                amount = input("Transfer amount: ").strip()
                result = bank.transfer_money(sender, receiver, amount)
                print("Transfer successful.")
                print(f"Sender balance: ₹{result['sender_balance']:.2f}")
                print(f"Receiver balance: ₹{result['receiver_balance']:.2f}")
            elif choice == "9":
                print_statement(bank, input("Account number: ").strip())
            elif choice == "10":
                account_no = input("Account number: ").strip()
                print(f"Interest preview: ₹{bank.calculate_interest(account_no):.2f}")
                print("Note: Preview only; interest is not credited.")
            elif choice == "11":
                total_balance = sum(a.get_balance() for a in bank.accounts.values())
                print(f"Customers: {len(bank.customers)}")
                print(f"Accounts: {len(bank.accounts)}")
                print(f"Combined balance: ₹{total_balance:.2f}")
                print(f"Business transactions: {bank.total_transactions}")
            elif choice == "12":
                print("Thank you for using Lokesh National Bank.")
                break
            else:
                print("Invalid choice. Select 1 to 12.")
        except (BankingError, ValueError, TypeError) as error:
            print(f"Operation failed: {error}")

if __name__ == "__main__":
    main()
