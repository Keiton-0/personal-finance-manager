import json
import os
from datetime import datetime


INCOME_CATEGORIES = {
    "salary":     {"name": "Rrogë",     "icon": "💼"},
    "freelance":  {"name": "Freelance", "icon": "💻"},
    "investment": {"name": "Investim",  "icon": "📈"},
    "gift":       {"name": "Dhuratë",   "icon": "🎁"},
    "other_in":   {"name": "Tjetër",    "icon": "💰"},
}

EXPENSE_CATEGORIES = {
    "food":          {"name": "Ushqim",    "icon": "🍔"},
    "transport":     {"name": "Transport", "icon": "🚌"},
    "housing":       {"name": "Banim",     "icon": "🏠"},
    "health":        {"name": "Shëndet",   "icon": "💊"},
    "education":     {"name": "Arsim",     "icon": "📚"},
    "entertainment": {"name": "Argëtim",   "icon": "🎬"},
    "clothing":      {"name": "Veshje",    "icon": "👕"},
    "utilities":     {"name": "Faturat",   "icon": "💡"},
    "travel":        {"name": "Udhëtim",   "icon": "✈️"},
    "other_ex":      {"name": "Tjetër",    "icon": "🛒"},
}

ALL_CATEGORIES = {**INCOME_CATEGORIES, **EXPENSE_CATEGORIES}


class FinanceManager:
    def __init__(self, file_name="data.json"):
        self.file_name = file_name
        self.balance = 0.0
        self.transactions = []
        self.load_data()

    # ── persistence ──────────────────────────────────────────────────────────

    def load_data(self):
        if os.path.exists(self.file_name):
            with open(self.file_name, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                    self.balance = data.get("balance", 0.0)
                    self.transactions = data.get("transactions", [])
                except json.JSONDecodeError:
                    self.balance = 0.0
                    self.transactions = []

    def save_data(self):
        with open(self.file_name, "w", encoding="utf-8") as f:
            json.dump(
                {"balance": self.balance, "transactions": self.transactions},
                f,
                indent=4,
                ensure_ascii=False,
            )

    # ── core actions ──────────────────────────────────────────────────────────

    def add_transaction(self, tx_type, amount, category, description="", date=None):
        """Add an income or expense transaction.

        Args:
            tx_type:     'income' or 'expense'
            amount:      positive float
            category:    key from INCOME_CATEGORIES or EXPENSE_CATEGORIES
            description: optional free-text note
            date:        ISO date string YYYY-MM-DD; defaults to today
        """
        if amount <= 0:
            raise ValueError("Shuma duhet të jetë pozitive.")

        cats = INCOME_CATEGORIES if tx_type == "income" else EXPENSE_CATEGORIES
        if category not in cats:
            raise ValueError(f"Kategoria '{category}' nuk është e vlefshme.")

        date = date or datetime.today().strftime("%Y-%m-%d")
        cat_meta = cats[category]

        tx = {
            "id": int(datetime.now().timestamp() * 1000),
            "type": tx_type,
            "amount": round(amount, 2),
            "category": category,
            "category_name": cat_meta["name"],
            "category_icon": cat_meta["icon"],
            "description": description.strip(),
            "date": date,
        }

        self.transactions.insert(0, tx)

        if tx_type == "income":
            self.balance += amount
        else:
            self.balance -= amount

        self.balance = round(self.balance, 2)
        self.save_data()
        return tx

    def delete_transaction(self, tx_id):
        """Remove a transaction by id and reverse its effect on balance."""
        tx = next((t for t in self.transactions if t["id"] == tx_id), None)
        if tx is None:
            raise ValueError(f"Transaksioni me id={tx_id} nuk u gjet.")

        if tx["type"] == "income":
            self.balance -= tx["amount"]
        else:
            self.balance += tx["amount"]

        self.balance = round(self.balance, 2)
        self.transactions = [t for t in self.transactions if t["id"] != tx_id]
        self.save_data()
        return tx

    # ── queries ───────────────────────────────────────────────────────────────

    def get_transactions(self, month=None, year=None, tx_type=None, category=None):
        """Filter transactions; month/year are ints, tx_type is 'income'/'expense'."""
        result = self.transactions
        if month is not None and year is not None:
            result = [
                t for t in result
                if datetime.fromisoformat(t["date"]).month == month
                and datetime.fromisoformat(t["date"]).year == year
            ]
        if tx_type:
            result = [t for t in result if t["type"] == tx_type]
        if category:
            result = [t for t in result if t["category"] == category]
        return result

    def monthly_summary(self, month=None, year=None):
        """Return dict with total income, expenses, net for the given month."""
        now = datetime.today()
        month = month or now.month
        year = year or now.year
        txs = self.get_transactions(month=month, year=year)
        income = sum(t["amount"] for t in txs if t["type"] == "income")
        expense = sum(t["amount"] for t in txs if t["type"] == "expense")
        return {"income": round(income, 2), "expense": round(expense, 2), "net": round(income - expense, 2)}

    def category_breakdown(self, tx_type, month=None, year=None):
        """Return {category_id: amount} for the given type and period."""
        txs = self.get_transactions(month=month, year=year, tx_type=tx_type)
        breakdown = {}
        for t in txs:
            breakdown[t["category"]] = round(breakdown.get(t["category"], 0) + t["amount"], 2)
        return dict(sorted(breakdown.items(), key=lambda x: x[1], reverse=True))