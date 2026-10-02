import json


class User:
    def __init__(self, name):
        self.name = name
        self.owes = {}
        self.owed_by = {}

    def get_balance(self):
        total_owed_by = sum(self.owed_by.values())
        total_owes = sum(self.owes.values())
        return total_owed_by - total_owes

    def to_dict(self):
        return {
            "name": self.name,
            "owes": self.owes,
            "owed_by": self.owed_by,
            "balance": self.get_balance()
        }


class RestAPI:
    def __init__(self, data=None):
        self.users = {}
        if data:
            for user_data in data.get("users", []):
                user = User(user_data["name"])
                user.owes = user_data.get("owes", {})
                user.owed_by = user_data.get("owed_by", {})
                self.users[user.name] = user

    def get(self, url, payload=None):
        if isinstance(payload, str):
            try:
                payload = json.loads(payload)
            except json.JSONDecodeError:
                payload = None
        
        if url == "/users":
            return self._handle_get_users(payload)
        return json.dumps({"error": "Not found"})

    def post(self, url, payload=None):
        if isinstance(payload, str):
            try:
                payload = json.loads(payload)
            except json.JSONDecodeError:
                payload = None

        if url == "/add":
            return self._handle_add_user(payload)
        elif url == "/iou":
            return self._handle_iou(payload)
        return json.dumps({"error": "Not found"})

    def _handle_get_users(self, payload):
        if payload and "users" in payload:
            requested_names = payload["users"]
            users_to_return = []
            for name in sorted(requested_names):
                if name in self.users:
                    users_to_return.append(self.users[name].to_dict())
                else:
                    return json.dumps({"error": f"User {name} not found"})
            return json.dumps({"users": users_to_return})
        else:
            all_users = [user.to_dict() for user in sorted(self.users.values(), key=lambda u: u.name)]
            return json.dumps({"users": all_users})

    def _handle_add_user(self, payload):
        if not payload or "user" not in payload:
            return json.dumps({"error": "Missing user name"})
        
        name = payload["user"]
        if name in self.users:
            return json.dumps({"error": "User already exists"})
            
        new_user = User(name)
        self.users[name] = new_user
        return json.dumps(new_user.to_dict())

    def _handle_iou(self, payload):
        if not payload:
            return json.dumps({"error": "Missing payload"})
            
        lender_name = payload.get("lender")
        borrower_name = payload.get("borrower")
        amount = payload.get("amount")

        if not lender_name or not borrower_name or amount is None:
            return json.dumps({"error": "Missing lender, borrower, or amount"})
            
        if lender_name not in self.users:
            return json.dumps({"error": f"Lender {lender_name} not found"})
            
        if borrower_name not in self.users:
            return json.dumps({"error": f"Borrower {borrower_name} not found"})
            
        if not isinstance(amount, (int, float)) or amount <= 0:
            return json.dumps({"error": "Amount must be a positive number"})

        lender = self.users[lender_name]
        borrower = self.users[borrower_name]

        # Update borrower's owes
        borrower.owes[lender_name] = borrower.owes.get(lender_name, 0) + amount
        
        # Update lender's owed_by
        lender.owed_by[borrower_name] = lender.owed_by.get(borrower_name, 0) + amount

        # Clean up zero balances to keep data clean (optional but good practice)
        if borrower.owes.get(lender_name) == 0:
            del borrower.owes[lender_name]
        if lender.owed_by.get(borrower_name) == 0:
            del lender.owed_by[borrower_name]

        # Return updated user objects sorted by name
        updated_users = [lender.to_dict(), borrower.to_dict()]
        updated_users.sort(key=lambda u: u["name"])
        
        return json.dumps({"users": updated_users})
