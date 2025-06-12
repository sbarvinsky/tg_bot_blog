import telebot

TOKEN = "твой_бот_токен_сюда"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=["start"])
def send_welcome(message):
    bot.reply_to(message, "Привет! Я живой 🤖")

bot.polling()
