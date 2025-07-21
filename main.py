import telebot
from telebot import types
import json
import random

bot = telebot.TeleBot("6686451745:AAHb1ZKud-ancEFkXdfPI7inPVXcTShXG98")

user_progress = {}
def send_prophet_story(message, prophet_name):
    with open("stories.json", "r", encoding="utf-8") as f:
        stories = json.load(f)

    for prophet in stories:
        if prophet["name"] == prophet_name:
            user_id = message.chat.id
            user_progress[user_id] = {
                "prophet": prophet_name,
                "part": 0
            }

            story_part = prophet["story"][0]
            markup = types.InlineKeyboardMarkup()
            if len(prophet["story"]) > 1:
                markup.add(types.InlineKeyboardButton("التالي ⏭️", callback_data="next_part"))
            bot.send_message(user_id, story_part, reply_markup=markup)
            return

with open("stories.json", "r", encoding="utf-8") as f:
        stories = json.load(f) 

@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(message.chat.id, "مرحبًا بك في بوت قصص الأنبياء 🌟\nاكتب /list لرؤية جميع القصص.")

@bot.message_handler(commands=['list'])
def list_stories(message):
    with open("stories.json", "r", encoding="utf-8") as f:
        stories = json.load(f)
    buttons = [telebot.types.InlineKeyboardButton(text=s['name'], callback_data=s['name']) for s in stories]
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(*buttons)
    bot.send_message(message.chat.id, "اختر قصة نبي:", reply_markup=markup)
    
@bot.message_handler(commands=["random"])
def random_story(message):
    s = random.choice(stories)
    bot.send_message(message.chat.id, f"📖 قصة {s['name']}\n\n{s['story']}")

@bot.message_handler(commands=["story"])
def story_by_name(message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.send_message(message.chat.id, "❗ استخدم الأمر هكذا: /story اسم_النبي")
        return
    name = parts[1].strip()
    for s in stories:
        if s["name"] == name:
            bot.send_message(message.chat.id, f"📖 قصة {s['name']}\n\n{s['story']}")
            return
    bot.send_message(message.chat.id, "❌ لم أجد قصة لهذا الاسم.")

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    prophet_name = call.data
    send_prophet_story(call.message, prophet_name)

@bot.callback_query_handler(func=lambda call: call.data == "next_part")
def handle_next_part(call):
    user_id = call.message.chat.id
    if user_id not in user_progress:
        bot.answer_callback_query(call.id, "لا توجد قصة جارية.")
        return

    prophet_name = user_progress[user_id]["prophet"]
    part_index = user_progress[user_id]["part"] + 1

    with open("stories.json", "r", encoding="utf-8") as f:
        stories = json.load(f)

    for prophet in stories:
        if prophet["name"] == prophet_name:
            if part_index < len(prophet["story"]):
                user_progress[user_id]["part"] = part_index
                story_part = prophet["story"][part_index]

                markup = types.InlineKeyboardMarkup()
                if part_index < len(prophet["story"]) - 1:
                    markup.add(types.InlineKeyboardButton("التالي ⏭️", callback_data="next_part"))
                else:
                    markup.add(types.InlineKeyboardButton("✅ انتهت القصة", callback_data="end_story"))

                bot.edit_message_text(
                    chat_id=user_id,
                    message_id=call.message.message_id,
                    text=story_part,
                    reply_markup=markup
                )
            return

@bot.callback_query_handler(func=lambda call: call.data == "end_story")
def end_story(call):
    bot.answer_callback_query(call.id, "انتهت القصة ✅")


    
bot.infinity_polling()
