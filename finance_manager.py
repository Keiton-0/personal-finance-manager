class FinanceManager:
    def __init__(self):
        self.balance = 0

    def run(self):
        print("=== Personal Finance Manager ===")

        while True:
            print("\n1. Add Income")
            print("2. Add Expense")
            print("3. Show Balance")
            print("4. Exit")

            choice = input("Choose an option: ")

            if choice == "1":
                amount = float(input("Enter income amount: "))
                self.balance += amount
                print("Income added successfully!")

            elif choice == "2":
                amount = float(input("Enter expense amount: "))
                self.balance -= amount
                print("Expense added successfully!")

            elif choice == "3":
                print(f"Current Balance: ${self.balance}")

            elif choice == "4":
                print("Goodbye!")
                break

            else:
                print("Invalid option.")