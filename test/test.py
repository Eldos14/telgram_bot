import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from telegram_bot import bool_login


def test_case_1():
    chat = 1213131313
    return (bool_login(chat)==False)

def test_case_2():
    white_list = 5305489290
    return (bool_login(chat)==False)




if __name__ == "__main__":
    print(test_case_1())
    print(test_case_2())

