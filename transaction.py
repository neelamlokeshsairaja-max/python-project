"""Transaction helpers. Entries are stored as dictionaries for easy JSON/TXT persistence."""
from datetime import datetime, timezone
from uuid import uuid4

def make_transaction(transaction_type, amount, balance, counterparty=None, transaction_id=None):
    return {
        "transaction_id": transaction_id or str(uuid4()),
        "date": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
        "type": str(transaction_type),
        "amount": f"{amount:.2f}",
        "balance": f"{balance:.2f}",
        "counterparty": counterparty,
    }
