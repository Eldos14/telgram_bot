import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


import requests
from telegram_bot import get_inf

def test_case_1():
    return("0000000")==None
def test_case_2():
    return("229251896")==None

if __name__ == "__main__":
    print(test_case_1())
    print(test_case_2())
