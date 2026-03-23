# A text-based slot machine!
import random

MAX_LINES = 3
MAX_BET = 100
MIN_BET = 1

ROWS = 3
COLS = 3

# Frequency table of all symbols in the slot machine.
# A is the most valuable with the lowest frequency
# while D is the less valuable so plenty of D's!
symbol_count = {
    "A": 2,
    "B": 4,
    "C": 6,
    "D": 8,
}

symbol_values = {
    "A": 5,
    "B": 4,
    "C": 3,
    "D": 2,
}


def check_winnings(columns: list, lines: int, bet: int, values: dict):
    winnings = 0
    winning_lines = []
    for line in range(lines):  # the number of lines user decided to bet on (1-3)
        symbol = columns[0][line]  # [[A,B,D],[D,C,A],[C,D,B]]
        for column in columns:  #    [0][0] is A
            symbol_to_check = column[line]
            if symbol != symbol_to_check:
                break
        else:
            winnings += values[symbol] * bet
            winning_lines.append(line + 1)

    return winnings, winning_lines


def get_slot_machine_spin(rows: int, cols: int, symbols: dict):
    """The actual slot machine spinning!"""
    # Calculate what symbols are going to be on each column
    # based on the frequency information about the symbols provided.
    all_symbols = []
    for key, value in symbols.items():
        for _ in range(value):
            all_symbols.append(key)

    # Now the all_symbols list contains all the symbols that many times as their frequency
    columns = []
    # For each of the three columns,
    for _ in range(cols):
        column = []
        # make a copy of the original list because once a symbol
        # has been chosen, we must remove it from this list (the copy).
        current_symbols = all_symbols.copy()
        #  generate the 3 rows.
        for _ in range(rows):
            value = random.choice(current_symbols)
            current_symbols.remove(value)  # remove the choice from the list
            column.append(value)  # add the choice to the current column

        # when the column is ready, add it to the list of columns
        # in the end columns will have the form: [[A,B,D],[D,C,A],[C,D,B]]
        columns.append(column)

    return columns


def print_slot_machine(columns: list):
    for row in range(len(columns[0])):
        for i, column in enumerate(columns):
            if i != len(columns) - 1:
                print(column[row], end=" | ")
            else:
                print(column[row], end="")
        print()


def deposit():
    """Collect the cash the user deposits in the game"""
    # continuously ask the user for a valid amount
    while True:
        amount = input("What would you like to deposit? $")

        # check that the amount entered is a number, before getting out of the loop
        if amount.isdigit():
            # OK, it's a string of numbers, so convert it to a number format
            amount = int(amount)
            # but is it greater than zero?
            if amount > 0:
                break  # break out of the loop and return
            else:
                # print a warning and loop again
                print("Amount must be greater than 0.")
        # reached this point if the amount is not a sequence of digits
        else:
            # print a warning and loop again
            print("Please enter a number.")

    return amount


def get_number_of_lines():
    """Ask the player to decide on how many slot machine lines they will bet"""
    # continuously ask the user for number of lines
    while True:
        lines = input(f"Enter the number of lines to bet on (1-{MAX_LINES})? ")

        # check that the amount entered is a number, before getting out of the loop
        if lines.isdigit():
            # OK, it's a string of numbers, so convert it to a number format
            lines = int(lines)
            # but is it between 1-3?
            if 1 <= lines <= MAX_LINES:
                break  # break out of the loop and return
            else:
                # print a warning and loop again
                print(f"Number of lines must be between 1-{MAX_LINES}.")
        # reached this point if the amount is not a sequence of digits
        else:
            # print a warning and loop again
            print("Please enter a number.")

    return lines


def get_bet():
    """Ask the user for the cash they will bet on each line"""
    # continuously ask the user for a valid amount
    while True:
        amount = input("What would you like to bet on each line? $")

        # check that the amount entered is a number, before getting out of the loop
        if amount.isdigit():
            # OK, it's a string of numbers, so convert it to a number format
            amount = int(amount)
            # but is it in the range of allowable bettings?
            if MIN_BET <= amount <= MAX_BET:
                break  # break out of the loop and return
            else:
                # print a warning and loop again
                print(f"The bet must be between ${MIN_BET} - ${MAX_BET}.")
        # reached this point if the amount is not a sequence of digits
        else:
            # print a warning and loop again
            print("Please enter a number.")

    return amount

def spin(balance):
    lines = get_number_of_lines()

    while True:
        bet = get_bet()
        total_bet = bet * lines

        # We must check it the total bet exceeds the player's current balance:
        if total_bet > balance:
            print(f"You do not have enough to bet that amount, your current balance is ${balance}.")
        # break from the loop if there's enough cash in player's balance
        else:
            break

    print(f"You are betting ${bet} on {lines} lines. Total bet is equal to ${total_bet}.")
    slots = get_slot_machine_spin(ROWS, COLS, symbol_count)
    print_slot_machine(slots)
    winnings, winning_lines = check_winnings(slots, lines, bet, symbol_values)
    print(f"You won ${winnings}.")
    print(f"You won on lines:", *winning_lines)

    return winnings-total_bet

def main():
    balance = deposit()
    while True;
        print(f"Current balance is ${balance}")
        answer=input("Press enter to play (q to quit).")
        if answer=="q":
            break
        balance+=spin(balance)

    print(f"You left with")

main()
