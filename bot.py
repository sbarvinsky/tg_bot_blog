import telebot
from telebot.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from database import save_idea, get_ideas, get_categories, add_category
import config
import random

bot = telebot.TeleBot(config.TELEGRAM_TOKEN)
user_categories = {}

def create_main_menu():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = [
        '💡 Новая идея', '📚 Мои материалы',
        '🏷️ Мои рубрики', '✨ Вдохновение',
    ]
    keyboard.add(*buttons)
    return keyboard

MOTIVATION = [
    "Твои мысли уникальны — мир ждет твоего поста! 🌍",
    "Каждое слово имеет значение, особенно твое! ✍️",
    "Сегодня кто-то найдет вдохновение в твоем блоге! 🔥",
    "Несовершенство делает тебя настоящим — пиши от души! 💖",
    "Твоя аудитория растет с каждым постом! 🚀"
]

@bot.message_handler(commands=['start'])
def start(message):
    welcome = (
        "🌟 Привет, блогер!\n\n"
        "Я твой личный помощник в создании контента!\n"
        "Генерируй идеи, храни их по рубрикам, вдохновляйся и веди библиотеку."
    )
    bot.send_message(message.chat.id, welcome, reply_markup=create_main_menu())
    bot.send_message(message.chat.id, random.choice(MOTIVATION))

    # Создаём базовые рубрики, если их нет
    if not get_categories(message.chat.id):
        for category in config.DEFAULT_CATEGORIES:
            add_category(message.chat.id, category)

@bot.message_handler(func=lambda msg: msg.text == '💡 Новая идея')
def new_idea(message):
    user_id = message.chat.id
    categories = get_categories(user_id)
    if not categories:
        bot.send_message(user_id, "У вас пока нет рубрик. Сначала создайте их через меню '🏷️ Мои рубрики'")
        return
    keyboard = InlineKeyboardMarkup()
    for category in categories:
        keyboard.add(InlineKeyboardButton(category, callback_data=f"cat_{category}"))
    bot.send_message(user_id, "Выбери рубрику для новой идеи:", reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data.startswith('cat_'))
def process_text_category(call):
    try:
        user_id = call.message.chat.id
        category = call.data[4:]
        bot.edit_message_text(
            chat_id=user_id,
            message_id=call.message.message_id,
            text=f"💡 Введи тему/идею для рубрики '{category}':"
        )
        user_categories[user_id] = category
    except Exception as e:
        bot.answer_callback_query(call.id, f"❌ Ошибка: {e}")

@bot.message_handler(func=lambda msg: msg.chat.id in user_categories)
def process_idea_text(message):
    try:
        user_id = message.chat.id
        category = user_categories[user_id]
        theme = message.text
        save_idea(theme, user_id, category)
        bot.send_message(
            user_id,
            f"🎯 Идея для поста в рубрике '{category}':\n\n{theme}\n\n💾 Идея сохранена в библиотеку!"
        )
        del user_categories[user_id]
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка: {e}. Попробуй еще раз.")

@bot.message_handler(func=lambda msg: msg.text == '🏷️ Мои рубрики')
def manage_categories(message):
    user_id = message.chat.id
    categories = get_categories(user_id)
    if not categories:
        categories = ["Пока нет рубрик"]
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("➕ Добавить рубрику", callback_data="add_category"))
    bot.send_message(
        user_id,
        f"📂 Твои текущие рубрики:\n\n" + "\n".join([f"• {cat}" for cat in categories]),
        reply_markup=keyboard
    )

@bot.callback_query_handler(func=lambda call: call.data == "add_category")
def add_new_category(call):
    user_id = call.message.chat.id
    bot.send_message(user_id, "✏️ Введи название новой рубрики:")
    bot.register_next_step_handler(call.message, save_new_category)

def save_new_category(message):
    try:
        user_id = message.chat.id
        category = message.text.strip()
        if not category:
            bot.send_message(user_id, "❌ Название рубрики не может быть пустым!")
            return
        if len(category) > 30:
            bot.send_message(user_id, "❌ Название слишком длинное (макс. 30 символов)")
            return
        add_category(user_id, category)
        bot.send_message(user_id, f"✅ Рубрика '{category}' успешно добавлена!")
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка: {e}")

@bot.message_handler(func=lambda msg: msg.text == '📚 Мои материалы')
def my_ideas(message):
    user_id = message.chat.id
    ideas = get_ideas(user_id)
    if not ideas:
        bot.send_message(user_id, "У вас пока нет идей.")
    else:
        text = "🗃️ Ваши идеи:\n\n"
        for idx, idea in enumerate(ideas, 1):
            text += f"{idx}. [{idea['category']}] {idea['text']} ({idea['date']})\n"
        bot.send_message(user_id, text)

@bot.message_handler(func=lambda msg: msg.text == '✨ Вдохновение')
def inspire(message):
    bot.send_message(message.chat.id, random.choice(MOTIVATION))

if __name__ == "__main__":
    bot.infinity_polling()
