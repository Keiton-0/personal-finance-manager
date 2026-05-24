import tkinter as tk
from tkinter import messagebox
import json
import os


class FinanceGUI:
    def __init__(self):
        self.file_name = "data.json"
        self.balance = 0

        self.load_data()

        self.root = tk.Tk()
        self.root.title("Personal Finance Manager")
        self.root.geometry("400x400")
        self.root.configure(bg="#1e1e1e")

        self.title_label = tk.Label(
            self.root,
            text="Personal Finance Manager",
            font=("Arial", 18, "bold"),
            bg="#1e1e1e",
            fg="white"
        )
        self.title_label.pack(pady=20)

        self.balance_label = tk.Label(
            self.root,
            text=f"Balance: ${self.balance}",
            font=("Arial", 16),
            bg="#1e1e1e",
            fg="#00ff99"
        )
        self.balance_label.pack(pady=10)

        self.amount_entry = tk.Entry(
            self.root,
            font=("Arial", 14),
            justify="center"
        )
        self.amount_entry.pack(pady=10)

        self.income_button = tk.Button(
            self.root,
            text="Add Income",
            font=("Arial", 12, "bold"),
            bg="#00cc66",
            fg="white",
            width=20,
            command=self.add_income
        )
        self.income_button.pack(pady=10)

        self.expense_button = tk.Button(
            self.root,
            text="Add Expense",
            font=("Arial", 12, "bold"),
            bg="#cc3333",
            fg="white",
            width=20,
            command=self.add_expense
        )
        self.expense_button.pack(pady=10)

        self.exit_button = tk.Button(
            self.root,
            text="Exit",
            font=("Arial", 12, "bold"),
            bg="#444",
            fg="white",
            width=20,
            command=self.root.quit
        )
        self.exit_button.pack(pady=20)

    def load_data(self):
        if os.path.exists(self.file_name):
            with open(self.file_name, "r") as file:
                try:
                    data = json.load(file)
                    self.balance = data.get("balance", 0)
                except json.JSONDecodeError:
                    self.balance = 0

    def save_data(self):
        data = {
            "balance": self.balance
        }

        with open(self.file_name, "w") as file:
            json.dump(data, file, indent=4)

    def update_balance(self):
        self.balance_label.config(
            text=f"Balance: ${self.balance}"
        )

    def add_income(self):
        try:
            amount = float(self.amount_entry.get())

            self.balance += amount

            self.save_data()
            self.update_balance()

            self.amount_entry.delete(0, tk.END)

            messagebox.showinfo(
                "Success",
                "Income added successfully!"
            )

        except ValueError:
            messagebox.showerror(
                "Error",
                "Please enter a valid number."
            )

    def add_expense(self):
        try:
            amount = float(self.amount_entry.get())

            self.balance -= amount

            self.save_data()
            self.update_balance()

            self.amount_entry.delete(0, tk.END)

            messagebox.showinfo(
                "Success",
                "Expense added successfully!"
            )

        except ValueError:
            messagebox.showerror(
                "Error",
                "Please enter a valid number."
            )

    def run(self):
        self.root.mainloop()