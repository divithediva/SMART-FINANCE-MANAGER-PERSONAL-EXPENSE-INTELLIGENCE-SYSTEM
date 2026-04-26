# week1.py
date = input("Enter date: ")
amount = float(input("Enter amount: "))
t_type = input("Enter type: ")
merchant = input("Enter merchant: ")
if amount > 0:
    print("Date:", date)
    print("Amount:", amount)
    print("Type:", t_type)
    print("Merchant:", merchant)
else:
    print("Invalid amount")

# week2.py
date = ""
amount = 0
t_type = ""
merchant = ""
saved = False
while True:
    print("1.Add 2.View 3.Exit")
    ch = input()
    if ch == "1":
        date = input("Date: ")
        amount = float(input("Amount: "))
        t_type = input("Type: ")
        merchant = input("Merchant: ")
        saved = True
    elif ch == "2":
        if saved:
            print(date, amount, t_type, merchant)
        else:
            print("No data")
    elif ch == "3":
        Break

# week3.py
transactions = []
while True:
    print("1.Add 2.View 3.Exit")
    ch = input()
    if ch == "1":
        date = input()
        amount = input()
        t_type = input()
        merchant = input()
        transactions.append([date, amount, t_type, merchant])
    elif ch == "2":
        for t in transactions:
            print(t)
    elif ch == "3":
        break

# week4.py
transactions = []


def add():
    date = input()
    amount = float(input())
    t_type = input()
    merchant = input()
    transactions.append([date, amount, t_type, merchant])


def view():
    for t in transactions:
        print(t)


while True:
    print("1.Add 2.View 3.Exit")
    ch = input()
    if ch == "1":
        add()
    elif ch == "2":
        view()
    elif ch == "3":
        Break

# week5.py
transactions = {}
id = 1
while True:
    print("1.Add 2.View 3.Exit")
    ch = input()
    if ch == "1":
        date = input()
        amount = float(input())
        t_type = input()
        merchant = input()
        transactions[id] = (date, amount, t_type, merchant)
        id += 1
    elif ch == "2":
        for i in transactions:
            print(i, transactions[i])
    elif ch == "3":
        Break


# week6.py
class Transaction:
    def __init__(self, d, a, t, m):
        self.date = d
        self.amount = a
        self.type = t
        self.merchant = m

    def show(self):
        print(self.date, self.amount, self.type, self.merchant)


data = []
while True:
    print("1.Add 2.View 3.Exit")
    ch = input()
    if ch == "1":
        t = Transaction(input(), float(input()), input(), input())
        data.append(t)

    elif ch == "2":
        for t in data:
            t.show()

    elif ch == "3":
        Break


# week7.py
class Record:
    def __init__(self):
        self.id = 1
        self.timestamp = input()


class Transaction(Record):
    def __init__(self, a, t, m):
        super().__init__()
        self.amount = a
        self.type = t
        self.merchant = m

    def show(self):
        print(self.id, self.timestamp, self.amount, self.type, self.merchant)


# week8.py
import json
import csv

data = [{"date": "1", "amount": 100, "type": "d", "merchant": "a"}]
# JSON
f = open("data.json", "w")
json.dump(data, f)
f.close()
# CSV
f = open("data.csv", "w", newline="")
w = csv.writer(f)
w.writerow(["date", "amount", "type", "merchant"])
for t in data:
    w.writerow([t["date"], t["amount"], t["type"], t["merchant"]])
f.close()

# main.py
from week6 import Transaction

t = Transaction("1", 100, "d", "shop")
t.show()

# __init__.py
print("Package loaded")
#Week 9: [Modules & Multi module]

#utils/validators.py
def valid_amount(amount):
 if amount > 0:
    return True
 return False

#storage/ data-store.py

transactions: []
def add_transaction(transaction):
    transactions, append (transaction)
def get_transactions():
  return transactions
#models/transaction.py
class Transaction:
    def__init__(self,date,amount,t_type,merchant):
    self.date = date
    self.amount= amount
    self.type=t_type
    self.merchant=merchant
 def display (self):
    print(self.date, "|", self.amount, "|", self.type, "|", self.merchant)
from models.transaction import Transaction
from utils.validators import valid_amount
from storage.data_store import add_transaction, get_transactions
while True:
 print("\n, Add_Transaction")
print("2. View transications")
print("3. Exit")
choice =input ("Enter choice: ")
if choice=="1":
   date-input( "Enter date:")
   amount=float(input ("Enter amount: "))
   t_type=input("Entef type:")
   merchant=input ("Enter merchant:")
if valid-amount(amount):
        t =Transaction (date, amount, t. type_merchant)
add_transaction(t)
print("Transaction added")
else:
print("Invalid amount")
elif choice = "2":
transactions=get_transactions()
for t in transactions:
 t.display
elif choice == "3":
     break
else:
print("invali choice")
 #week10
# sfmpeis/__init__.py

print("SFM-PEIS Package Loaded")
# sfmpeis/models/transaction.py

class Transaction:
    def __init__(self, date, amount, t_type, merchant):
        self.date = date
        self.amount = amount
        self.type = t_type
        self.merchant = merchant

    def display(self):
        print(self.date, "|", self.amount, "|", self.type, "|", self.merchant)
# sfmpeis/utils/validators.py

def valid_amount(amount):
    if amount > 0:
        return True
    return False
# sfmpeis/storage/data_store.py

transactions = []

def add_transaction(transaction):
    transactions.append(transaction)

def get_transactions():
    return transactions
# main.py (outside package)

from sfmpeis.models.transaction import Transaction
from sfmpeis.utils.validators import valid_amount
from sfmpeis.storage.data_store import add_transaction, get_transactions

while True:
    print("\n1. Add Transaction")
    print("2. View Transactions")
    print("3. Exit")

    choice = input("Enter choice: ")

    if choice == "1":
        date = input("Enter date: ")
        amount = float(input("Enter amount: "))
        t_type = input("Enter type: ")
        merchant = input("Enter merchant: ")

        if valid_amount(amount):
            t = Transaction(date, amount, t_type, merchant)
            add_transaction(t)
            print("Transaction added")
        else:
            print("Invalid amount")

    elif choice == "2":
        transactions = get_transactions()
        for t in transactions:
            t.display()

    elif choice == "3":
        break

    else:
        print("Invalid choice")
# week11_exceptions.py

import json


class InvalidAmountError(Exception):
    pass


class InvalidDateError(Exception):
    pass


class MissingFieldError(Exception):
    pass


def validate_amount(amount):
    if amount <= 0:
        raise InvalidAmountError("Amount must be greater than 0")


def validate_date(date):
    if len(date) != 10 or date[4] != "-" or date[7] != "-":
        raise InvalidDateError("Date must be in YYYY-MM-DD format")


def validate_fields(date, amount, t_type, merchant):
    if date == "" or t_type == "" or merchant == "":
        raise MissingFieldError("All fields are required")
    validate_amount(amount)
    validate_date(date)


def save_transactions(transactions):
    try:
        file = open("transactions.json", "w")
        json.dump(transactions, file)
    except:
        print("Error while saving file")
    finally:
        file.close()


def load_transactions():
    try:
        file = open("transactions.json", "r")
        data = json.load(file)
    except FileNotFoundError:
        print("File not found")
        data = []
    except json.JSONDecodeError:
        print("Corrupted JSON file")
        data = []
    finally:
        try:
            file.close()
        except:
            pass
    return data


transactions = load_transactions()

while True:
    print("\n1. Add Transaction")
    print("2. View Transactions")
    print("3. Save Transactions")
    print("4. Exit")

    choice = input("Enter choice: ")

    if choice == "1":
        try:
            date = input("Enter date (YYYY-MM-DD): ")
            amount = float(input("Enter amount: "))
            t_type = input("Enter type: ")
            merchant = input("Enter merchant: ")

            validate_fields(date, amount, t_type, merchant)

        except InvalidAmountError as e:
            print(e)

        except InvalidDateError as e:
            print(e)

        except MissingFieldError as e:
            print(e)

        else:
            transaction = {
                "date": date,
                "amount": amount,
                "type": t_type,
                "merchant": merchant
            }
            transactions.append(transaction)
            print("Transaction added successfully")

        finally:
            print("Add transaction process completed")

    elif choice == "2":
        for t in transactions:
            print(t)

    elif choice == "3":
        save_transactions(transactions)
        print("Transactions saved")

    elif choice == "4":
        break

    else:
        print("Invalid choice")
# week12.py

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# sample data (you can replace with CSV later)
data = {
    "date": ["2025-03-25", "2025-03-26"],
    "amount": [600, 300],
    "category": ["shopping", "food"],
    "merchant": ["lenovo", "swiggy"]
}

df = pd.DataFrame(data)

while True:
    print("\n1. Category Wise Spending")
    print("2. Merchant Analysis")
    print("3. Monthly Spending")
    print("4. Daily Average Spend")
    print("5. Predict Next Month Expense")
    print("6. Show Chart")
    print("7. Exit")

    choice = input("Enter choice: ")

    if choice == "1":
        print("\nCategory Wise Spending")
        print(df.groupby("category")["amount"].sum())

    elif choice == "2":
        print("\nMerchant Analysis")
        print(df.groupby("merchant")["amount"].sum())

    elif choice == "3":
        df["date"] = pd.to_datetime(df["date"])
        df["month"] = df["date"].dt.month
        print("\nMonthly Spending")
        print(df.groupby("month")["amount"].sum())

    elif choice == "4":
        avg = np.mean(df["amount"])
        print("\nDaily Average Spend:", avg)

    elif choice == "5":
        prediction = np.mean(df["amount"])
        print("\nPredicted Next Month Expense:", prediction)

    elif choice == "6":
        plt.bar(df["merchant"], df["amount"])
        plt.title("Spending Chart")
        plt.xlabel("Merchant")
        plt.ylabel("Amount")
        plt.savefig("chart.png")
        print("Chart saved as chart.png")

    elif choice == "7":
        break

    else:
        print("Invalid choice")
