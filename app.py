"""Flask API and web application for the banking system."""
from decimal import Decimal
from flask import Flask, render_template, request, jsonify
from bank import Bank
from customer import Customer
from exceptions import BankingError, StorageError

app = Flask(__name__)
bank = Bank("SecureBank")
next_customer_id = max([int(x) for x in bank.customers if str(x).isdigit()] + [100]) + 1

@app.route("/")
def home():
    return render_template("index.html")

def body():
    return request.get_json(silent=True) or {}

def error_response(error, status=400):
    return jsonify({"success": False, "message": str(error)}), status

@app.route("/api/customers", methods=["POST"])
def register_customer():
    global next_customer_id
    data = body()
    try:
        customer = Customer(next_customer_id, data.get("name"), data.get("phone"), data.get("email"))
        bank.add_customer(customer)
        customer_id = next_customer_id
        next_customer_id += 1
        return jsonify({"success": True, "message": "Customer registered successfully.",
                        "customer_id": customer_id}), 201
    except BankingError as exc:
        return error_response(exc)

@app.route("/api/accounts", methods=["POST"])
def create_account():
    data = body()
    account_number = str(data.get("account_number", "")).strip()
    try:
        customer_id = data.get("customer_id")
        balance = data.get("balance", 0)
        kind = str(data.get("account_type", "")).strip().lower()
        if not account_number:
            raise ValueError("Account number is required.")
        if kind == "savings":
            account = bank.create_savings_account(account_number, customer_id, balance)
        elif kind == "current":
            account = bank.create_current_account(account_number, customer_id, balance)
        else:
            raise ValueError("Choose savings or current account.")
        return jsonify({"success": True, "message": "Account created successfully.",
                        "account_number": account.account_number}), 201
    except BankingError as exc:
        status = 404 if "not found" in str(exc).lower() else 400
        return error_response(exc, status)
    except (ValueError, TypeError) as exc:
        return error_response(exc)

@app.route("/api/transactions", methods=["POST"])
def process_transaction():
    data = body()
    account_number = str(data.get("account_number", "")).strip()
    kind = str(data.get("transaction_type", "")).strip().lower()
    try:
        if kind == "deposit":
            balance = bank.deposit_money(account_number, data.get("amount"))
        elif kind in ("withdraw", "withdrawal"):
            balance = bank.withdraw_money(account_number, data.get("amount"))
        else:
            raise ValueError("Choose deposit or withdraw.")
        return jsonify({"success": True, "message": "Transaction completed successfully.",
                        "account_number": account_number, "balance": balance})
    except BankingError as exc:
        status = 404 if "not found" in str(exc).lower() else 400
        return error_response(exc, status)
    except (ValueError, TypeError) as exc:
        return error_response(exc)

@app.route("/api/transfers", methods=["POST"])
def transfer():
    data = body()
    try:
        result = bank.transfer_money(
            data.get("sender_account"), data.get("receiver_account"), data.get("amount")
        )
        return jsonify({"success": True, "message": "Transfer completed successfully.",
                        **result})
    except BankingError as exc:
        status = 404 if "not found" in str(exc).lower() else 400
        return error_response(exc, status)
    except (ValueError, TypeError) as exc:
        return error_response(exc)

@app.route("/api/accounts/<account_number>", methods=["GET"])
def get_account(account_number):
    try:
        account = bank.find_account(account_number)
        return jsonify({"success": True, "account_number": account.account_number,
                        "customer_name": account.customer.name,
                        "account_type": account.account_type, "balance": account.get_balance()})
    except BankingError as exc:
        return error_response(exc, 404)

@app.route("/api/accounts/<account_number>/statement", methods=["GET"])
def get_statement(account_number):
    try:
        return jsonify({"success": True, **bank.account_statement(account_number)})
    except BankingError as exc:
        return error_response(exc, 404)

@app.route("/api/accounts/<account_number>/interest", methods=["GET"])
def get_interest(account_number):
    try:
        return jsonify({"success": True, "account_number": account_number,
                        "interest_preview": bank.calculate_interest(account_number),
                        "note": "Preview only; interest is not credited."})
    except BankingError as exc:
        return error_response(exc, 404)

@app.route("/api/dashboard", methods=["GET"])
def dashboard():
    total_balance = sum(account.get_balance() for account in bank.accounts.values())
    return jsonify({
        "total_customers": len(bank.customers),
        "total_accounts": len(bank.accounts),
        "total_balance": round(total_balance, 2),
        "total_transactions": bank.total_transactions,
    })

@app.errorhandler(StorageError)
def storage_error(error):
    return error_response(error, 500)

if __name__ == "__main__":
    app.run(debug=False)
