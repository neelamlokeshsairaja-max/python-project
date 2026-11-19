"""Customer model and backend validation."""
import re
from exceptions import InvalidCustomerError

class Customer:
    def __init__(self, customer_id, name, phone, email):
        if isinstance(customer_id, bool) or not str(customer_id).strip():
            raise InvalidCustomerError("Customer ID is required.")
        name = str(name).strip() if name is not None else ""
        phone = str(phone).strip() if phone is not None else ""
        email = str(email).strip() if email is not None else ""
        if len(name) < 2 or not re.fullmatch(r"[A-Za-z][A-Za-z .'-]*", name):
            raise InvalidCustomerError("Enter a valid customer name.")
        if not re.fullmatch(r"[6-9]\d{9}", phone):
            raise InvalidCustomerError("Enter a valid 10-digit Indian mobile number.")
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
            raise InvalidCustomerError("Enter a valid email address.")
        self.customer_id = int(customer_id) if str(customer_id).isdigit() else str(customer_id)
        self.name = name
        self.phone = phone
        self.email = email

    def to_dict(self):
        return {
            "customer_id": self.customer_id,
            "name": self.name,
            "phone": self.phone,
            "email": self.email,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(data["customer_id"], data["name"], data["phone"], data["email"])

    def display_customer(self):
        print(f"Customer ID: {self.customer_id}")
        print(f"Name: {self.name}")
        print(f"Phone: {self.phone}")
        print(f"Email: {self.email}")
