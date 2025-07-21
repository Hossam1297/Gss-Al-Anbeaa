import telebot
import json
import random

bot = telebot.TeleBot("6686451745:AAHb1ZKud-ancEFkXdfPI7inPVXcTShXG98")

user_progress = {}

with open("stories.json", encoding="utf-8") as f:
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

@bot.callback_query_handler(func=lambda call: call.data not in ["next_part", "end_story"])
def handle_callback(call):
    user_id = call.message.chat.id
    prophet_name = call.data

    for s in stories:
        if s["name"] == prophet_name:
            if isinstance(s["story"], list):
                # تسجيل تقدم المستخدم
                user_progress[user_id] = {"prophet": prophet_name, "part": 0}
                first_part = s["story"][0]

                markup = types.InlineKeyboardMarkup()
                if len(s["story"]) > 1:
                    markup.add(types.InlineKeyboardButton("التالي ⏭️", callback_data="next_part"))

                bot.send_message(user_id, f"📖 قصة {prophet_name}\n\n{first_part}", reply_markup=markup)
            else:
                # إذا كانت القصة ليست مجزأة
                bot.send_message(user_id, f"📖 قصة {prophet_name}\n\n{s['story']}")
            break
    
bot.infinity_polling()
