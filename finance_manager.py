import json
import os


class FinanceManager:
    def __init__(self):
        self.file_name = "data.json"
        self.balance = 0
        self.transactions = []

        self.load_data()

    def load_data(self):
        if os.path.exists(self.file_name):
            with open(self.file_name, "r") as file:
                try:
                    data = json.load(file)
                    self.balance = data.get("balance", 0)
                    self.transactions = data.get("transactions", [])
                except json.JSONDecodeError:
                    self.balance = 0
                    self.transactions = []

    def save_data(self):
        data = {
            "balance": self.balance,
            "transactions": self.transactions
        }

        with open(self.file_name, "w") as file:
            json.dump(data, file, indent=4)

    def add_income(self):
        amount = float(input("Enter income amount: "))
        self.balance += amount

        self.transactions.append({
            "type": "income",
            "amount": amount
        })

        self.save_data()

        print("Income added successfully!")

    def add_expense(self):
        amount = float(input("Enter expense amount: "))
        self.balance -= amount

        self.transactions.append({
            "type": "expense",
            "amount": amount
        })

        self.save_data()

        print("Expense added successfully!")

    def show_balance(self):
        print(f"\nCurrent Balance: ${self.balance}")

    def show_transactions(self):
        print("\n=== Transactions ===")

        if not self.transactions:
            print("No transactions found.")
            return

        for transaction in self.transactions:
            print(
                f"{transaction['type'].capitalize()} - ${transaction['amount']}"
            )

    def run(self):
        while True:
            print("\n=== Personal Finance Manager ===")
            print("1. Add Income")
            print("2. Add Expense")
            print("3. Show Balance")
            print("4. Show Transactions")
            print("5. Exit")

            choice = input("Choose an option: ")

            if choice == "1":
                self.add_income()

            elif choice == "2":
                self.add_expense()

            elif choice == "3":
                self.show_balance()

            elif choice == "4":
                self.show_transactions()

            elif choice == "5":
                print("Goodbye!")
                break

            else:
                print("Invalid option.")