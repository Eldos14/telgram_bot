import telebot
import requests
from config import TOKEN, WHITE_LIST

bot = telebot.TeleBot(TOKEN)


def get_reviews(article):
    if len(article) > 10:
        return None
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://www.wildberries.ru/catalog/76460152/detail.aspx"
    }
    url = f"https://card.wb.ru/cards/v2/detail?appType=1&curr=kzt&dest=82&spp=30&hide_dtype=10;13;14&ab_testing=false&lang=ru&nm={article}"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        product = data["data"]["products"][0]
        return product.get("reviewRating"), product.get("feedbacks")
    except Exception as e:
        print(f"[get_reviews] Error: {e}")
        return None


def get_reviews_and_questions(article):
    if len(article) > 10:
        return None
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://www.wildberries.ru/catalog/76460152/detail.aspx"
    }
    total_data = get_total(article)
    if not total_data:
        return None
    imtID = total_data.get("imt_id")
    if not imtID:
        return None
    url = f"https://questions.wildberries.ru/api/v1/questions?imtId={imtID}&take=20&skip=0"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        return [q["text"] for q in data.get("questions", [])]
    except Exception as e:
        print(f"[get_reviews_and_questions] Error: {e}")
        return None

def get_now_time(article):
    if len(article) > 10:
        return None
    headers = {"User-Agent": "Mozilla/5.0"}
    url = f"https://basket-15.wbbasket.ru/vol{article[0:4]}/part{article[0:6]}/{article}/info/price-history.json"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data[-1]["price"]["RUB"]
    except Exception as e:
        print(f"[get_now_time] Error: {e}")
        return None

def get_total(article):
    if len(article) != 9:
        return None
    headers = {"User-Agent": "Mozilla/5.0"}
    url = f"https://basket-15.wbbasket.ru/vol{article[0:4]}/part{article[0:6]}/{article}/info/ru/card.json"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"[get_total] Error: {e}")
        return None

def get_inf(article):
    if len(article) > 10:
        return None
    headers = {"User-Agent": "Mozilla/5.0"}
    url = f"https://basket-15.wbbasket.ru/vol{article[0:4]}/part{article[0:6]}/{article}/info/price-history.json"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        total = sum([i["price"]["RUB"] for i in data])
        return total / len(data) if data else None
    except Exception as e:
        print(f"[get_inf] Error: {e}")
        return None

def bool_login(chat_id):
    return chat_id in WHITE_LIST


@bot.message_handler(commands=['start'])
def send_welcome(message):
    if bool_login(message.chat.id):
        bot.reply_to(message, "Добро пожаловать!")
    else:
        bot.send_message(message.chat.id, "Нет доступа! Купите подписку.")


@bot.message_handler(content_types=['text'])
def analytics(message):
    if not bool_login(message.chat.id):
        bot.send_message(message.chat.id, "Доступа нет к боту, купите подписку.")
        return

    article = message.text.strip()
    avg_price = get_inf(article)
    now_price = get_now_time(article)
    total_info = get_total(article)
    reviews_data = get_reviews(article)
    questions = get_reviews_and_questions(article)

    if not avg_price or not now_price or not total_info:
        bot.send_message(message.chat.id, "❌ Не удалось получить информацию о товаре.")
        return

 
    avg_kzt = round(avg_price * 6.42)
    now_kzt = round(now_price * 6.42)

    product_name = total_info.get("imt_name", "Неизвестно")
    characteristics = {opt["name"]: opt["value"] for opt in total_info.get("options", [])}

    bot.send_message(message.chat.id, f"🛍 Товар: {product_name}")
    bot.send_message(message.chat.id, "📋 Характеристики:")
    for k, v in characteristics.items():
        bot.send_message(message.chat.id, f"- {k}: {v}")

    bot.send_message(message.chat.id, f"💰 Текущая цена: {now_kzt} тг")
    bot.send_message(message.chat.id, f"📊 Средняя цена: {avg_kzt} тг")

    if now_kzt > avg_kzt:
        bot.send_message(message.chat.id, f"⚠️ Цена {now_kzt} выше средней ({avg_kzt}) — *НЕВЫГОДНО* покупать.")
    elif now_kzt < avg_kzt:
        bot.send_message(message.chat.id, f"✅ Цена {now_kzt} ниже средней ({avg_kzt}) — *ВЫГОДНО* покупать.")
    else:
        bot.send_message(message.chat.id, f"➖ Цена совпадает со средней.")

    if questions:
        bot.send_message(message.chat.id, "❓ Вопросы к товару:")
        for q in questions:
            bot.send_message(message.chat.id, f"- {q}")

    if reviews_data:
        review_rating, feedbacks = reviews_data
        bot.send_message(message.chat.id, f"⭐️ Рейтинг: {review_rating}, Отзывов: {feedbacks}")
        if feedbacks > 0:
            bot.send_message(message.chat.id, f"📈 Отношение: {round(float(review_rating) / float(feedbacks), 4)}")
        else:
            bot.send_message(message.chat.id, "🔍 Нет отзывов.")
    else:
        bot.send_message(message.chat.id, "⚠️ Отзывы не найдены.")

bot.polling(none_stop=True)
