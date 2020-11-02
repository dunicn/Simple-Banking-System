import random
import sqlite3

conn = sqlite3.connect("card.s3db")
c = conn.cursor()


def num_generator(digit):
    number = ""
    for x in range(digit):
        x = str(random.randrange(0, 9))
        number = number + str(x)
    return number


def create_db():
    c.execute("""CREATE TABLE IF NOT EXISTS card (
                id INTEGER, 
                number TEXT, 
                pin TEXT, 
                balance INTEGER DEFAULT 0
                )""")


def insert_user(number, pin, balance):
    with conn:
        c.execute("INSERT INTO card VALUES (:id, :number, :pin, :balance)",
                  {"id": len(c.fetchall()) + 1, "number": number, "pin": pin, "balance": balance})


def get_user(card_number):
    c.execute("SELECT * FROM card WHERE number=:number", {"number": card_number})
    return c.fetchone()


def luhn_algorithm(card_number):
    control_number = int(card_number[-1])
    short_card_number = card_number[:-1]
    short_card_sum = 0
    short_list = []
    for elem in short_card_number:
        short_list.append(int(elem))
    for i in range(0, len(short_list), 2):
        short_list[i] = short_list[i] * 2
    for i in range(len(short_list)):
        if short_list[i] > 9:
            short_list[i] = short_list[i] - 9

    for digit in short_list:
        short_card_sum += int(digit)

    if (short_card_sum + control_number) % 10 == 0:
        return True
    else:
        return False


class SimpleBankingSystem:

    def __init__(self):
        self.base_card_number = "400000"
        self.card_number = 0
        self.card_PIN = ""
        self.balance = 0

    def card_number_generator(self):  # Card Number
        card_generator = num_generator(10)
        self.card_number = str(self.base_card_number + card_generator)
        if not luhn_algorithm(self.card_number):
            self.card_number_generator()

    def create_account(self):
        self.card_number_generator()
        #  pin_generator = random.randrange(1, 10 ** 4)
        pin_generator = num_generator(4)
        self.card_PIN = str(pin_generator)
        print("Your card has been created")
        print("Your card number: ")
        print(self.card_number)
        print("Your PIN: ")
        print(self.card_PIN)
        print()
        insert_user(self.card_number, self.card_PIN, self.balance)

    def logging_in(self):
        card_input = int(input("Enter your card number: "))
        self.card_number = card_input
        pin_input = int(input("Enter your PIN: "))
        print()
        if get_user(str(card_input)) is None:
            print("Wrong card number or PIN!")
            print()
            self.main_menu()
        elif str(pin_input) in get_user(str(card_input)):
            print("You have successfully logged in!")
            self.account_menu()
        else:
            print("Wrong card number or PIN!")
            self.main_menu()

    def main_menu(self):

        create_db()
        print("1. Create an account \n2. Log into account \n0. Exit")
        print()
        while True:
            user_input = int(input())
            if user_input == 1:
                self.create_account()
                self.main_menu()
            elif user_input == 2:
                self.logging_in()
            elif user_input == 0:
                print("Bye!")
                exit()

    def add_income(self):
        print("Enter income: ")
        income_input = int(input())

        with conn:
            c.execute("UPDATE card SET balance= balance + {} WHERE number = {}".format(income_input, self.card_number))
        print("Income was added!")

    def get_balance(self):
        c.execute("SELECT balance FROM card WHERE number=:number", {"number": self.card_number})
        curr_balance = c.fetchone()
        if curr_balance is None:
            curr_balance = 0
        return curr_balance[0]

    def transfer_method(self):
        sending_card = self.card_number
        print("Enter card number: ")
        receiving_card = input()
        if not luhn_algorithm(receiving_card):
            print("Probably you made a mistake in the card number. Please try again!")
        elif get_user(str(receiving_card)) is None:
            print("Such a card does not exist.")
        elif receiving_card == sending_card:
            print("You can't transfer money to the same account!")
        else:
            print("Enter how much money you want to transfer:")
            transfer_input = int(input())
            if transfer_input > self.get_balance():
                print("Not enough money!")
            else:
                with conn:
                    c.execute("UPDATE card SET balance= balance - {} WHERE number = {}".format(transfer_input, sending_card))
                with conn:
                    c.execute("UPDATE card SET balance= balance + {} WHERE number = {}".format(transfer_input, receiving_card))
                print("Success!")

    def close_account(self):
        with conn:
            c.execute("DELETE FROM card WHERE number = {}".format(self.card_number))
        print("The account has been closed!")

    def account_menu(self):
        print()
        print("1. Balance \n2. Add income \n3. Do transfer \n4. Close account \n5. Log out \n0. Exit")
        user_choice = int(input())
        if user_choice == 1:
            balance = self.get_balance()
            print("Balance: {}".format(balance))
            self.account_menu()
        if user_choice == 2:
            self.add_income()
            self.account_menu()
        if user_choice == 3:
            self.transfer_method()
            self.account_menu()
        if user_choice == 4:
            self.close_account()
            self.main_menu()
        if user_choice == 5:
            self.main_menu()
        if user_choice == 0:
            print("Bye!")
            exit()


test = SimpleBankingSystem()

test.main_menu()

conn.close()
