from typing import List, Dict, Any

class Transaction:
    def __init__(self, date: str, payment_ref: str, amount: float, rj_number: str):
        self.date = date
        self.payment_ref = payment_ref
        self.amount = amount
        self.rj_number = rj_number

class ReconciliationResult:
    def __init__(self, matched_transactions: List[Transaction], unmatched_transactions: List[Transaction]):
        self.matched_transactions = matched_transactions
        self.unmatched_transactions = unmatched_transactions

class MatchCriteria:
    def __init__(self, date_match: bool, payment_ref_match: bool, amount_match: bool):
        self.date_match = date_match
        self.payment_ref_match = payment_ref_match
        self.amount_match = amount_match

class ReconciliationBatch:
    def __init__(self, status: str, transactions: List[Transaction]):
        self.status = status
        self.transactions = transactions

class ReconciliationSummary:
    def __init__(self, balanced: List[ReconciliationBatch], eighty_percent: List[ReconciliationBatch], sixty_percent: List[ReconciliationBatch], unmatched: List[ReconciliationBatch]):
        self.balanced = balanced
        self.eighty_percent = eighty_percent
        self.sixty_percent = sixty_percent
        self.unmatched = unmatched