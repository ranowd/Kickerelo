from telegram.ext import Updater, CommandHandler

def bop(bot, update):
	chat_id = update.message.chat_id
	user = update.message.from_user['username']
	print (user)
	bot.send_message(chat_id=chat_id, text="I am alive.")


updater = Updater('')
dp = updater.dispatcher
dp.add_handler(CommandHandler('bop',bop))
updater.start_polling()
updater.idle()