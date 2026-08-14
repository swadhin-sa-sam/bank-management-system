import random
import json
import os
from datetime import datetime


ACCOUNT_FILE = "accounts.json"
TRANSACTION_FILE = "transactions.json"


# Load account data
def load_data():
    if not os.path.exists(ACCOUNT_FILE):
        return []

    try:
        with open(ACCOUNT_FILE, "r") as file:
            data = json.load(file)

            if isinstance(data, list):
                return data

    except (json.JSONDecodeError, OSError):
        return []

    return []


# Save account data
def save_data(accounts):
    with open(ACCOUNT_FILE, "w") as file:
        json.dump(accounts, file, indent=4)


# Save transaction
def save_transaction(card_no, transaction_type, amount):
    if os.path.exists(TRANSACTION_FILE):
        try:
            with open(TRANSACTION_FILE, "r") as file:
                transactions = json.load(file)

                if not isinstance(transactions, list):
                    transactions = []

        except (json.JSONDecodeError, OSError):
            transactions = []
    else:
        transactions = []

    transactions.append({
        "card_no": card_no,
        "type": transaction_type,
        "amount": amount,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

    with open(TRANSACTION_FILE, "w") as file:
        json.dump(transactions, file, indent=4)


# Create account
def create_account():
    accounts = load_data()

    print("""
==================================================
              CREATE NEW ACCOUNT
==================================================
""")

    name = input("Enter Account Holder Name: ")
    father_name = input("Enter Father's Name: ")

    # Generate unique 12-digit account number
    while True:
        card = str(random.randint(100000000000, 999999999999))

        if not any(acc["card_no"] == card for acc in accounts):
            break

    print("Your Account Number Is:", card)

    # PIN
    while True:
        pin = input("Create 4-digit PIN: ")

        if len(pin) == 4 and pin.isdigit():
            break

        print("PIN must be exactly 4 digits.")

    # Initial deposit
    while True:
        try:
            balance = float(input("Enter Initial Deposit: "))

            if balance < 0:
                print("Deposit cannot be negative.")
                continue

            break

        except ValueError:
            print("Please enter a valid amount.")

    new_account = {
        "name": name,
        "father_name": father_name,
        "card_no": card,
        "pin": pin,
        "balance": balance
    }

    accounts.append(new_account)
    save_data(accounts)

    if balance > 0:
        save_transaction(card, "Initial Deposit", balance)

    print("""
==================================================
           ACCOUNT CREATED SUCCESSFULLY
==================================================
""")

    print("Account Holder :", name)
    print("Father's Name  :", father_name)
    print("Account Number :", card)
    print("Balance        :", balance)

    return new_account


# Login
def login():
    accounts = load_data()

    for attempt in range(2):

        print("""
==================================================
                     LOGIN
==================================================
""")

        card = input("Enter Account Number: ")

        if len(card) != 12 or not card.isdigit():
            print("Account Number must be exactly 12 digits.")
            continue

        pin = input("Enter PIN: ")

        if len(pin) != 4 or not pin.isdigit():
            print("PIN must be exactly 4 digits.")
            continue

        for account in accounts:
            if account["card_no"] == card and account["pin"] == pin:

                print("Login Successful")
                print(f"Welcome, {account['name']}!")

                return account, accounts

        print("Incorrect Account Number or PIN.")

    print("Too many failed attempts.")
    return None


# Check balance
def check_balance(account):
    print("""
==================================================
                    BALANCE
==================================================
""")

    print(f"Available Balance: ₹{account['balance']:.2f}")

    print("==================================================")


# Deposit
def deposit(account, accounts):
    try:
        amount = float(input("Enter deposit amount: "))

        if amount <= 0:
            print("Deposit amount must be greater than zero.")
            return

    except ValueError:
        print("Please enter a valid amount.")
        return

    account["balance"] += amount

    save_data(accounts)
    save_transaction(account["card_no"], "Deposit", amount)

    print("Deposit Successful")
    print(f"New Balance: ₹{account['balance']:.2f}")


# Withdraw
def withdraw(account, accounts):
    try:
        amount = float(input("Enter withdraw amount: "))

        if amount <= 0:
            print("Withdrawal amount must be greater than zero.")
            return

    except ValueError:
        print("Please enter a valid amount.")
        return

    if amount > account["balance"]:
        print("Insufficient Balance")
        return

    account["balance"] -= amount

    save_data(accounts)
    save_transaction(account["card_no"], "Withdrawal", amount)

    print("Withdrawal Successful")
    print(f"Remaining Balance: ₹{account['balance']:.2f}")


# Transfer
def transfer(account, accounts):
    receiver_card = input("Enter Receiver Account Number: ")

    if receiver_card == account["card_no"]:
        print("You cannot transfer money to your own account.")
        return

    receiver = None

    for acc in accounts:
        if acc["card_no"] == receiver_card:
            receiver = acc
            break

    if receiver is None:
        print("Receiver account not found.")
        return

    try:
        amount = float(input("Enter transfer amount: "))

        if amount <= 0:
            print("Transfer amount must be greater than zero.")
            return

    except ValueError:
        print("Please enter a valid amount.")
        return

    if amount > account["balance"]:
        print("Insufficient balance.")
        return

    account["balance"] -= amount
    receiver["balance"] += amount

    save_data(accounts)

    save_transaction(
        account["card_no"],
        f"Transfer to {receiver_card}",
        amount
    )

    save_transaction(
        receiver["card_no"],
        f"Transfer from {account['card_no']}",
        amount
    )

    print("Transfer Successful")
    print("Transferred Amount: ₹", amount)
    print("Remaining Balance: ₹", account["balance"])


# Change PIN
def change_pin(account, accounts):
    old_pin = input("Enter Current PIN: ")

    if old_pin != account["pin"]:
        print("Incorrect Current PIN")
        return

    for _ in range(2):
        new_pin = input("Enter New PIN: ")

        if len(new_pin) == 4 and new_pin.isdigit():

            if new_pin == old_pin:
                print("New PIN cannot be the same as old PIN.")
                continue

            account["pin"] = new_pin
            save_data(accounts)

            print("PIN Changed Successfully")
            return

        print("PIN must be exactly 4 digits.")

    print("Too many invalid attempts.")


# Transaction History
def transaction_history(account):

    if os.path.exists(TRANSACTION_FILE):

        try:
            with open(TRANSACTION_FILE, "r") as file:
                transactions = json.load(file)

        except (json.JSONDecodeError, OSError):
            transactions = []

    else:
        transactions = []

    print("""
==================================================
                TRANSACTION HISTORY
==================================================
""")

    found = False

    for transaction in transactions:

        if transaction["card_no"] == account["card_no"]:

            found = True

            print("Type   :", transaction["type"])
            print("Amount :", transaction["amount"])
            print("Date   :", transaction["date"])
            print("----------------------------------------")

    if not found:
        print("No transactions found.")

    print("==================================================")


# ATM operation
def operation(account, accounts):

    while True:

        print("""
==================================================
                ATM MAIN MENU
==================================================
        1. Check Balance
        2. Deposit Money
        3. Withdraw Money
        4. Transfer Money
        5. Change PIN
        6. Transaction History
        7. Exit
==================================================
""")

        try:
            choice = int(input("Enter your choice (1-7): "))

        except ValueError:
            print("Please enter a number between 1 and 7.")
            continue

        if choice == 1:
            check_balance(account)

        elif choice == 2:
            deposit(account, accounts)

        elif choice == 3:
            withdraw(account, accounts)

        elif choice == 4:
            transfer(account, accounts)

        elif choice == 5:
            change_pin(account, accounts)

        elif choice == 6:
            transaction_history(account)

        elif choice == 7:
            print("\nThank you for using our ATM.")
            print("Have a great day!")
            break

        else:
            print("Invalid choice. Please enter a number between 1 and 7.")


# Main function
while True:
    print("""
==================================================
                    ATM
==================================================
        1. Create Account
        2. Login
        3. Exit
==================================================
""")

    choice = input("Enter your choice: ")

    if choice == "1":
        create_account()

    elif choice == "2":
        user = login()

        if user:
            account, accounts = user
            operation(account, accounts)
        else:
            print("Login Failed.")

    elif choice == "3":
        print("Thank you for using our ATM.")
        break

    else:
        print("Invalid choice.")

