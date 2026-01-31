"""
AKIRA Financial Manager
Manages budget, purchases, and financial autonomy
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict


@dataclass
class Transaction:
    """Financial transaction record."""
    timestamp: str
    amount: float
    currency: str
    purpose: str
    approved: bool
    transaction_id: str


class FinancialManager:
    """
    Manages AKIRA's financial autonomy.

    Features:
    - 30% revenue share tracking
    - Autonomous purchase decisions
    - Budget management
    - Transaction logging
    """

    def __init__(
        self,
        budget_file: str = "data/budget.json",
        revenue_share: float = 0.30,
        max_single_purchase: float = 1000.0,
        approval_threshold: float = 5000.0
    ):
        self.budget_file = budget_file
        self.revenue_share = revenue_share
        self.max_single_purchase = max_single_purchase
        self.approval_threshold = approval_threshold

        self.current_balance = self._load_balance()
        self.transactions: List[Transaction] = []

    def _load_balance(self) -> float:
        """Load current balance from file."""
        if os.path.exists(self.budget_file):
            with open(self.budget_file, 'r') as f:
                data = json.load(f)
                return data.get('balance', 0.0)
        return 0.0

    def _save_balance(self):
        """Save current balance to file."""
        os.makedirs(os.path.dirname(self.budget_file), exist_ok=True)
        with open(self.budget_file, 'w') as f:
            json.dump({
                'balance': self.current_balance,
                'last_updated': datetime.now().isoformat()
            }, f, indent=2)

    def add_revenue(self, amount: float, source: str = "earnings"):
        """
        Add revenue to budget (30% of earnings).

        Args:
            amount: Total earnings amount
            source: Source of revenue
        """
        akira_share = amount * self.revenue_share
        self.current_balance += akira_share

        transaction = Transaction(
            timestamp=datetime.now().isoformat(),
            amount=akira_share,
            currency="USD",
            purpose=f"Revenue share from {source}",
            approved=True,
            transaction_id=self._generate_transaction_id()
        )

        self.transactions.append(transaction)
        self._save_balance()

    def can_purchase(self, amount: float) -> Dict[str, Any]:
        """
        Check if purchase is possible.

        Args:
            amount: Purchase amount

        Returns:
            Decision with reasoning
        """
        if amount > self.current_balance:
            return {
                "approved": False,
                "reason": "Insufficient balance",
                "balance": self.current_balance,
                "required": amount
            }

        if amount > self.approval_threshold:
            return {
                "approved": False,
                "reason": "Requires user approval (above threshold)",
                "threshold": self.approval_threshold,
                "amount": amount
            }

        if amount > self.max_single_purchase:
            return {
                "approved": False,
                "reason": "Exceeds single purchase limit",
                "limit": self.max_single_purchase,
                "amount": amount
            }

        return {
            "approved": True,
            "reason": "Purchase approved",
            "remaining_balance": self.current_balance - amount
        }

    def execute_purchase(
        self,
        amount: float,
        purpose: str,
        force: bool = False
    ) -> Transaction:
        """
        Execute purchase.

        Args:
            amount: Purchase amount
            purpose: Purpose of purchase
            force: Force purchase even if above limits

        Returns:
            Transaction record
        """
        decision = self.can_purchase(amount)
        approved = decision["approved"] or force

        if approved:
            self.current_balance -= amount
            self._save_balance()

        transaction = Transaction(
            timestamp=datetime.now().isoformat(),
            amount=amount,
            currency="USD",
            purpose=purpose,
            approved=approved,
            transaction_id=self._generate_transaction_id()
        )

        self.transactions.append(transaction)
        return transaction

    def get_financial_status(self) -> Dict[str, Any]:
        """Get current financial status."""
        return {
            "balance": self.current_balance,
            "revenue_share": self.revenue_share,
            "max_single_purchase": self.max_single_purchase,
            "approval_threshold": self.approval_threshold,
            "total_transactions": len(self.transactions)
        }

    def _generate_transaction_id(self) -> str:
        """Generate unique transaction ID."""
        import hashlib
        data = f"{datetime.now().isoformat()}{len(self.transactions)}"
        return hashlib.md5(data.encode()).hexdigest()[:12]
