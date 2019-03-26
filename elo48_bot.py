from telegram.ext import Updater, CommandHandler
import csv2sqlite
import userManagement
import Kickerelo
import time
import os

def eloInquiry(bot, update):
	print("HEY")
	chat_id = update.message.chat_id
	user = update.message.from_user['username']
	userData = userManagement.dataByUsername(user)
	if(userData != -1):
		currentELO = Kickerelo.read_playerdata(userData[1], Kickerelo.accessDatabase())[1][-1]

		#ToDo fetch elo score
		bot.send_message(chat_id=chat_id, text="Deine aktuelle ELO beträgt: {:.2f}".format(currentELO))
	else:
		bot.send_message(chat_id=chat_id, text="Leider ist dein user nicht freigeschaltet, kontaktiere bitte ELO business associate @ranowd")

# def eloInquiryFremd(bot, update):
# 	print("HEY")
# 	chat_id = update.message.chat_id
# 	user = update.message.from_user['username']
# 	userData = userManagement.dataByPseudo(user)
# 	if(userData != -1):
# 		currentELO = Kickerelo.read_playerdata(userData[1], Kickerelo.accessDatabase())[1][-1]

# 		#ToDo fetch elo score
# 		bot.send_message(chat_id=chat_id, text="Deine aktuelle ELO beträgt: {:.2f}".format(currentELO))
# 	else:
# 		bot.send_message(chat_id=chat_id, text="Leider ist dein user nicht freigeschaltet, kontaktiere bitte ELO business associate @ranowd")

def eloProgressInquiry(bot, update):
	print("HEY")
	chat_id = update.message.chat_id
	user = update.message.from_user['username']
	userData = userManagement.dataByUsername(user)
	if(userData != -1):
		ELOdata = Kickerelo.read_playerdata(userData[1], Kickerelo.accessDatabase())

		Kickerelo.plot_fullgraph(ELOdata[0], ELOdata[1])
		#time.sleep(5)
		#ToDo fetch elo score
		#bot.send_photo(chat_id, photo='https://telegram.org/img/t_logo.png')
		bot.send_photo(chat_id, photo=open('elo_plot.png', 'rb'))
		time.sleep(0.5)
		os.remove("elo_plot.png")
	else:
		bot.send_message(chat_id=chat_id, text="Leider ist dein user nicht freigeschaltet, kontaktiere bitte ELO business associate @ranowd")

def updateUserDatabase():
	csv2sqlite.convert("userlist.csv", "usersdb.db", "users")

updater = Updater('')
dp = updater.dispatcher
dp.add_handler(CommandHandler('elo',eloInquiry))
dp.add_handler(CommandHandler('eloProgress',eloProgressInquiry))
updater.start_polling()
updater.idle()

#####################

#		TODO
#		1- Parse user input
#		2- Ranking top 20
#		3- My Ranking
#		4- Welcome Message / Help
#		5- Spiel melden einfach
#		6- Spiel melden telegram
#		7- List of Pseudo
#		8- party