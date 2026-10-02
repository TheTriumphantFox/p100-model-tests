import json

class RestAPI:
    def __init__(self, database=None):
        self.database = {}
        if database:
            users_list = database.get('users', [])
            for entry in users_list:
                name = entry['name']
                self.database[name] = {
                    'name': name,
                    'owes': dict(entry.get('owes', {})),
                    'owed_by': dict(entry.get('owed_by', {})),
                    'balance': 0.0
                }

    def get(self, url, payload=None):
        if url == '/users':
            if payload:
                data = json.loads(payload)
                users_to_return = [u for u in data.get('users', []) if u in self.database]
                users_to_return.sort()
                result = [self._format_user(self.database[u]) for u in users_to_return]
            else:
                users_to_return = sorted(self.database.keys())
                result = [self._format_user(self.database[u]) for u in users_to_return]
            return json.dumps({"users": result})
        return None

    def post(self, url, payload=None):
        if url == '/add':
            data = json.loads(payload)
            name = data['user']
            if name not in self.database:
                self.database[name] = {
                    'name': name,
                    'owes': {},
                    'owed_by': {},
                    'balance': 0.0
                }
                return json.dumps(self._format_user(self.database[name]))
            return None
            
        elif url == '/iou':
            data = json.loads(payload)
            lender = data['lender']
            borrower = data['borrower']
            amount = data['amount']
            
            # Ensure users exist
            if lender not in self.database:
                self.database[lender] = {
                    'name': lender,
                    'owes': {},
                    'owed_by': {},
                    'balance': 0.0
                }
            if borrower not in self.database:
                self.database[borrower] = {
                    'name': borrower,
                    'owes': {},
                    'owed_by': {},
                    'balance': 0.0
                }
                
            self._record_iou(lender, borrower, amount)
            
            users_to_return = sorted([lender, borrower])
            result = [self._format_user(self.database[u]) for u in users_to_return]
            return json.dumps({"users": result})
        return None

    def _record_iou(self, lender, borrower, amount):
        lender_data = self.database[lender]
        borrower_data = self.database[borrower]
        
        # Lender is owed money by borrower
        # Borrower owes money to lender
        
        # Check if there's an existing debt in the opposite direction to net it out
        if borrower in lender_data['owes']:
            owed_amount = lender_data['owes'][borrower]
            if amount <= owed_amount:
                lender_data['owes'][borrower] -= amount
                if lender_data['owes'][borrower] <= 1e-9: # Floating point tolerance
                    del lender_data['owes'][borrower]
                # Borrower's debt to lender decreases, so lender's owed_by decreases? 
                # No, if A owes B, and B lends to A, they cancel out.
                # Here: Lender owes Borrower (in lender_data['owes']). 
                # Now Borrower owes Lender.
                # So we reduce the debt Lender owes to Borrower.
                borrower_data['owed_by'][lender] -= amount
                if borrower_data['owed_by'][lender] <= 1e-9:
                    del borrower_data['owed_by'][lender]
                return
            else:
                del lender_data['owes'][borrower]
                amount -= owed_amount
                # Now we have a net amount where Borrower owes Lender
                
        if lender in borrower_data['owed_by']:
            owed_amount = borrower_data['owed_by'][lender]
            if amount <= owed_amount:
                borrower_data['owed_by'][lender] -= amount
                if borrower_data['owed_by'][lender] <= 1e-9:
                    del borrower_data['owed_by'][lender]
                # Lender's claim on borrower decreases
                lender_data['owes'][borrower] -= amount
                if lender_data['owes'][borrower] <= 1e-9:
                    del lender_data['owes'][borrower]
                return
            else:
                del borrower_data['owed_by'][lender]
                amount -= owed_amount
                # Now we have a net amount where Borrower owes Lender

        # Net amount is positive, Borrower owes Lender
        if amount > 1e-9:
            borrower_data['owes'][lender] = borrower_data.get('owes', {}).get(lender, 0) + amount
            lender_data['owed_by'][borrower] = lender_data.get('owed_by', {}).get(borrower, 0) + amount

    def _format_user(self, user_data):
        # Calculate balance
        total_owed_by_others = sum(user_data['owed_by'].values())
        total_owed_to_others = sum(user_data['owes'].values())
        balance = total_owed_by_others - total_owed_to_others
        
        # Round to avoid floating point issues in output if desired, though usually JSON handles floats
        # The spec shows floats like 12.0, 4.0. Python json.dumps handles this.
        
        return {
            "name": user_data['name'],
            "owes": user_data['owes'],
            "owed_by": user_data['owed_by'],
            "balance": balance
        }
