import json


class RestAPI:
    def __init__(self, database=None):
        self.database = database or {"users": []}

    def get(self, url, payload=None):
        if url == "/users":
            if payload:
                payload = json.loads(payload)
                users = payload.get("users", [])
                return {"users": [self._get_user(name) for name in sorted(users)]}
            else:
                return {"users": [self._get_user(user["name"]) for user in self.database["users"]]}
        return {}

    def post(self, url, payload=None):
        if payload:
            payload = json.loads(payload)
            
        if url == "/add":
            user_name = payload.get("user")
            if user_name not in [u["name"] for u in self.database["users"]]:
                self.database["users"].append({
                    "name": user_name,
                    "owes": {},
                    "owed_by": {},
                    "balance": 0.0
                })
            return self._get_user(user_name)
        elif url == "/iou":
            lender = payload.get("lender")
            borrower = payload.get("borrower")
            amount = payload.get("amount")

            # Ensure users exist
            if lender not in [u["name"] for u in self.database["users"]]:
                self.database["users"].append({
                    "name": lender,
                    "owes": {},
                    "owed_by": {},
                    "balance": 0.0
                })
            if borrower not in [u["name"] for u in self.database["users"]]:
                self.database["users"].append({
                    "name": borrower,
                    "owes": {},
                    "owed_by": {},
                    "balance": 0.0
                })

            # Update IOU
            self._update_iou(lender, borrower, amount)

            # Return updated user objects sorted by name
            users = sorted([lender, borrower])
            return {"users": [self._get_user(name) for name in users]}
        return {}

    def _get_user(self, name):
        for user in self.database["users"]:
            if user["name"] == name:
                return {
                    "name": user["name"],
                    "owes": user["owes"],
                    "owed_by": user["owed_by"],
                    "balance": user["balance"]
                }
        return None

    def _update_iou(self, lender, borrower, amount):
        lender_user = next(u for u in self.database["users"] if u["name"] == lender)
        borrower_user = next(u for u in self.database["users"] if u["name"] == borrower)

        # Update lender's data
        if borrower in lender_user["owed_by"]:
            lender_user["owed_by"][borrower] += amount
        else:
            lender_user["owed_by"][borrower] = amount

        # Update borrower's data
        if lender in borrower_user["owes"]:
            borrower_user["owes"][lender] += amount
        else:
            borrower_user["owes"][lender] = amount

        # Update balances
        lender_user["balance"] += amount
        borrower_user["balance"] -= amount
