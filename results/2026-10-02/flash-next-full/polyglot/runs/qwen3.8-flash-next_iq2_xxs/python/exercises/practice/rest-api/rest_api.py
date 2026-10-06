import json

class RestAPI:
    def __init__(self, database=None):
        if database is None:
            self.database = {"users": []}
        else:
            self.database = database

    def get(self, url, payload=None):
        if payload is not None:
            payload = json.loads(payload)
            
        if url == "/users":
            if payload is None:
                return json.dumps({"users": self.database["users"]})
            else:
                users_to_get = payload.get("users", [])
                filtered_users = [user for user in self.database["users"] if user["name"] in users_to_get]
                return json.dumps({"users": filtered_users})
        return json.dumps({})

    def post(self, url, payload=None):
        if payload is not None:
            payload = json.loads(payload)

        if url == "/add":
            if payload is None:
                return json.dumps({})
            name = payload.get("user")
            new_user = {"name": name, "owes": {}, "owed_by": {}, "balance": 0.0}
            self.database["users"].append(new_user)
            return json.dumps(new_user)
        elif url == "/iou":
            if payload is None:
                return json.dumps({})
            lender = payload.get("lender")
            borrower = payload.get("borrower")
            amount = payload.get("amount")

            lender_user = None
            borrower_user = None
            for user in self.database["users"]:
                if user["name"] == lender:
                    lender_user = user
                if user["name"] == borrower:
                    borrower_user = user

            if lender_user and borrower_user:
                # Update lender's records
                if borrower in lender_user["owed_by"]:
                    lender_user["owed_by"][borrower] += amount
                else:
                    lender_user["owed_by"][borrower] = amount

                # Update borrower's records
                if lender in borrower_user["owes"]:
                    borrower_user["owes"][lender] += amount
                else:
                    borrower_user["owes"][lender] = amount

                # Recalculate balances
                lender_user["balance"] = sum(lender_user["owed_by"].values()) - sum(lender_user["owes"].values())
                borrower_user["balance"] = sum(borrower_user["owed_by"].values()) - sum(borrower_user["owes"].values())

                # Clean up zero balances
                if lender_user["owed_by"].get(borrower, 0) == 0:
                    del lender_user["owed_by"][borrower]
                if borrower_user["owes"].get(lender, 0) == 0:
                    del borrower_user["owes"][lender]

                # Sort users by name for response
                users = sorted([lender_user, borrower_user], key=lambda u: u["name"])
                return json.dumps({"users": users})
            return json.dumps({})
        return json.dumps({})
