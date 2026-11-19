# Advanced Bank Management System Using OOP

A Python OOP educational banking application with a command-line interface and Flask web interface.

## Features
- Customer registration with backend name, Indian mobile number and email validation.
- Abstract `Account` contract with `SavingsAccount` and `CurrentAccount`.
- Validated deposits and withdrawals; current accounts support an overdraft limit.
- Fund transfer with validation before either account is changed.
- Dated transaction history and account statements.
- Annual savings-interest preview; current-account interest is zero by documented rule.
- JSON data stored in `data/bank_data.txt`, with atomic temporary-file replacement.
- Data is loaded at startup; damaged data raises a storage error and is not silently replaced.
- Dashboard totals, including business transaction count (a transfer counts once).

## Project structure
```text
advanced_bank_management_system_corrected/
├── account.py
├── bank.py
├── customer.py
├── current_account.py
├── exceptions.py
├── main.py
├── savings_account.py
├── storage.py
├── transaction.py
├── app.py
├── requirements.txt
├── README.md
├── data/
│   └── bank_data.txt   # created after first successful save
├── templates/
│   └── index.html
└── static/
    ├── script.js
    └── style.css
```

## Requirements
- Python 3.10 or later
- Flask (for the web interface)

## Run the CLI
```bash
python main.py
```

## Run the web application
```bash
python -m pip install -r requirements.txt
python app.py
```
Open `http://127.0.0.1:5000/` in your browser.

## Important rules
- All transaction amounts must be finite, positive and rounded to two decimal places.
- Opening balances must be finite and nonnegative.
- Savings interest preview = current balance × annual interest rate, for one annual period.
- Current-account interest preview is zero.
- Interest is a preview only; it is not automatically credited.
- `total_transactions` counts successful business operations, not individual account ledger rows. A transfer is counted once although it creates two account-history entries.
- Account numbers are stored as strings consistently; customer IDs are numeric where possible.

## Verification checklist
1. Register a customer and reject duplicate IDs.
2. Reject malformed phone numbers and email addresses.
3. Create savings and current accounts and reject duplicate account numbers.
4. Deposit a valid amount.
5. Reject zero, negative, NaN and infinite transaction amounts.
6. Reject a savings withdrawal beyond the balance.
7. Enforce the current-account overdraft boundary.
8. Transfer between two different accounts and reject self-transfer.
9. Confirm both account statements show matching transfer entries.
10. Restart the app and verify customers, account types, balances and histories persist.
11. Confirm rejected operations do not change balances or increase transaction counts.
