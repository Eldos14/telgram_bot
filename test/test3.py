from telegram_bot import bool_login



def test_case_1():
    article = "229251896"
    return (get_now_time(article) != None) 
def test_case_2():
    article = "0000000000"
    return (get_now_time(article) == None)
def test_case_3():
        article = "229251896"
        return (get_total(article) != None)
def test_case_4():
        article = "0000000"
        return (get_total(article) == None)
    
if __name__ == "__main__":
    print(test_case_1())
    print(test_case_2())
    print(test_case_3())
    print(test_case_4())
