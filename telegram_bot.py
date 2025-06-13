import telebot
import requests

token = "7846667446:AAGBBNpdLsHm17WsVYha2LOonO_tgIhGL4c"
bot = telebot.TeleBot(token)

white_list = [5305489290, 1213131313, 55464546, 4546546547, 5950972429]

def bool_login(chat_id):
    return chat_id in white_list


def get_exchange_rate():
    try:
        response = requests.get("https://api.exchangerate.host/latest?base=RUB&symbols=KZT")
        data = response.json()
        return data["rates"]["KZT"]
    except:
        return 6,43


def get_inf(article):
    if len(article) > 12 or not article.isdigit():
        print("Артикул введён неверно!")
        return None

    headers = {
        "User-Agent": "Mozilla/5.0",
        "referer": "https://www.wildberries.ru"
    }

    url = f"https://basket-15.wbbasket.ru/vol{article[:4]}/part{article[:6]}/{article}/info/ru/card.json"
    print(f"Запрос к: {url}")

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 404:
            print("Товар не найден (404).")
            return None
        if response.status_code == 200:
            return response.json()
        print("Запрос провален:", response.status_code, response.text)
        return None
    except Exception as e:
        print(f"Ошибка: {e}")
        return None

def get_price(article):
    if len(article) > 12 or not article.isdigit():
        return None

    headers = {
        "User-Agent": "Mozilla/5.0",
        "referer": "https://www.wildberries.ru"
    }

    url = f"https://basket-15.wbbasket.ru/vol{article[:4]}/part{article[:6]}/{article}/info/price-history.json"
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data:
                prices = [entry["price"]["RUB"] / 100 for entry in data if "price" in entry and "RUB" in entry["price"]]
                if prices:
                    last_price = prices[-1]
                    avg_price = sum(prices) / len(prices)
                    return last_price, avg_price
        return None
    except requests.RequestException as e:
        print(f"Ошибка запроса: {e}")
        return None

@bot.message_handler(commands=['start'])
def send_welcome(message):
    if bool_login(message.chat.id):
        bot.reply_to(message, f"Добро пожаловать! Ваш ID: {message.chat.id}")
    else:
        bot.send_message(message.chat.id, "Извините, у вас нет доступа.")

@bot.message_handler(content_types=["text"])
def analytics(message):
    if not bool_login(message.chat.id):
        bot.send_message(message.chat.id, "Доступ к боту отсутствует, купите подписку")
        return

    article = message.text.strip()
    answer = get_inf(article)

    if answer is None:
        bot.send_message(message.chat.id, "Такого товара не существует или артикул введён неверно.")
        return

    try:
        product_name = answer.get('imt_name', 'Без названия')
        main_characteristics = {opt["name"]: opt["value"] for opt in answer.get("options", [])}

        bot.send_message(message.chat.id, f"Название товара: {product_name}")
        for key, value in main_characteristics.items():
            bot.send_message(message.chat.id, f"- {key}: {value}")
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка обработки товара: {e}")
        return

    result = get_price(article)
    if result is not None:
        last_price, avg_price = result
        exchange_rate = get_exchange_rate()

        last_price_kzt = last_price * exchange_rate
        avg_price_kzt = avg_price * exchange_rate

        bot.send_message(
            message.chat.id,
            f""" Артикул: {article}
Текущая цена: {last_price:.2f} ₽ ({last_price_kzt:.2f} ₸)
Средняя цена: {avg_price:.2f} ₽ ({avg_price_kzt:.2f} ₸)"""
        )
    else:
        bot.send_message(message.chat.id, "Цены нет или товар не найден")

bot.polling()
