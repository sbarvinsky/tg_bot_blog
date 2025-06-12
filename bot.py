import telebot

TOKEN = "1667810408:AAFoUREEdV5hNHuedD4CSuO6QI4QUhrPxKQ"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=["start"])
def send_welcome(message):
    bot.reply_to(message, "Привет! Я живой!!! Сделали репозиторий на гитхабе :) 🤖")

bot.polling()
