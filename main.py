import telebot
from telebot import types
import json
import random

# التوكن الخاص بك هنا
bot = telebot.TeleBot("6686451745:AAHb1ZKud-ancEFkXdfPI7inPVXcTShXG98")

# لتتبع تقدم كل مستخدم في القصة
user_progress = {}

# عند بدء البوت
@bot.message_handler(commands=['start'])
def send_welcome(message):
    with open("stories.json", "r", encoding="utf-8") as f:
        stories = json.load(f)

    markup = types.InlineKeyboardMarkup(row_width=2)
    for story in stories:
        button = types.InlineKeyboardButton(
            text=story["name"], callback_data=f"story_{story['name']}"
        )
        markup.add(button)

    bot.send_message(message.chat.id, "📜 اختر قصة نبي من القائمة:", reply_markup=markup)

# عند اختيار نبي من القائمة
@bot.callback_query_handler(func=lambda call: call.data.startswith("story_"))
def show_story(call):
    prophet_name = call.data.split("_", 1)[1]
    send_prophet_story(call.message, prophet_name)

# إرسال الجزء الأول من القصة
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

# زر التالي ⏭️
@bot.callback_query_handler(func=lambda call: call.data == "next_part")
def send_next_part(call):
    user_id = call.message.chat.id
    progress = user_progress.get(user_id)

    if not progress:
        bot.answer_callback_query(call.id, "⚠️ لم تبدأ قصة بعد.")
        return

    with open("stories.json", "r", encoding="utf-8") as f:
        stories = json.load(f)

    for prophet in stories:
        if prophet["name"] == progress["prophet"]:
            next_part_index = progress["part"] + 1
            if next_part_index < len(prophet["story"]):
                user_progress[user_id]["part"] = next_part_index
                story_part = prophet["story"][next_part_index]

                markup = types.InlineKeyboardMarkup()
                if next_part_index + 1 < len(prophet["story"]):
                    markup.add(types.InlineKeyboardButton("التالي ⏭️", callback_data="next_part"))

                bot.edit_message_text(chat_id=user_id, message_id=call.message.message_id,
                                      text=story_part, reply_markup=markup)
            else:
                bot.answer_callback_query(call.id, "✅ انتهت القصة.")
            return

# بدء التشغيل
print("✅ البوت يعمل الآن...")
bot.infinity_polling()
