from telegram.ext import Updater, CommandHandler
import telegram
from credentials import token, elomaster
import logging
import csv2sqlite
import userManagement
import Kickerelo
import time
import os

def readMessages(filePath):
  with open(filePath, encoding='utf8') as f:
    text = f.read()
    return text

def start(update, context):
  chat_id = update.message.chat_id
  context.bot.send_message(chat_id=chat_id, text=readMessages("messages/welcome.txt").format(elomaster))

def helpText(update, context):
  chat_id = update.message.chat_id
  context.bot.send_message(chat_id=chat_id, text=readMessages("messages/commands.txt"), parse_mode=telegram.ParseMode.MARKDOWN)

def notAllowed(context, chat_id, logmessage):
  context.bot.send_message(chat_id=chat_id, text="Leider ist dein user nicht freigeschaltet, kontaktiere bitte ELO business associate @{}}".format(elomaster))


def eloInquiry(update, context):
  chat_id = update.message.chat_id
  user = update.message.from_user['username']
  userData = userManagement.dataByUsername(user)
  if(userData != -1):
      currentELO = Kickerelo.read_playerdata(userData[1], Kickerelo.accessDatabase())[1][-1]
      context.bot.send_message(chat_id=chat_id, text="Deine aktuelle ELO beträgt: {:.2f}".format(currentELO))
  else:
    notAllowed(context, chat_id, "elo Inquiry")

def eloInquiryFremd(update, context):
  chat_id = update.message.chat_id
  user = update.message.from_user['username']
  userDataRequester = userManagement.dataByUsername(user)
  if(userDataRequester != -1):
    userDataFremd = userManagement.dataByPseudo(context.args[0])
    print(context.args[0])
    if(userDataFremd != -1):
      currentELO = Kickerelo.read_playerdata(userDataFremd[1], Kickerelo.accessDatabase())[1][-1]
      context.bot.send_message(chat_id=chat_id, text="Die aktuelle ELO von {} beträgt: {:.2f}".format(context.args[0], currentELO))
    else:
      context.bot.send_message(chat_id=chat_id, text="User Leider nicht gefunden.")
  else:
    notAllowed(context, chat_id, "elo Inquiry fremd")

# def eloProgressInquiry(bot, update):
#   print("HEY")
#   chat_id = update.message.chat_id
#   user = update.message.from_user['username']
#   userData = userManagement.dataByUsername(user)
#   if(userData != -1):
#       ELOdata = Kickerelo.read_playerdata(userData[1], Kickerelo.accessDatabase())

#       Kickerelo.plot_fullgraph(ELOdata[0], ELOdata[1])
#       #time.sleep(5)
#       #ToDo fetch elo score
#       #bot.send_photo(chat_id, photo='https://telegram.org/img/t_logo.png')
#       bot.send_photo(chat_id, photo=open('elo_plot.png', 'rb'))
#       time.sleep(0.5)
#       os.remove("elo_plot.png")
#   else:
#       notAllowed(bot, chat_id, "Own progress Inquiry")

# def checkAdmin(update):
#   user = update.message.from_user['username']
#   userData = userManagement.dataByUsername(user)
#   if(userData[0] == elomaster): return True
#   else: return False

# def updateUserDatabase(bot, update):
#   chat_id = update.message.chat_id
#   if(checkAdmin(update)):
#       os.remove("usersdb.db")
#       csv2sqlite.convert("userlist.csv", "usersdb.db", "users")
#       bot.send_message(chat_id=chat_id, text="Aktualisiert!")
#   else:
#       notAllowed(bot, chat_id, "Update user Database")

def bla(update, context):
  print(update.message.text)
  print(context.args)
  context.bot.send_message(chat_id=chat_id, text="Hi")

  # print(chat_id)

updater = Updater(token, use_context=True)
dp = updater.dispatcher

#logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#                     level=logging.INFO)

dp.add_handler(CommandHandler('start',start))
dp.add_handler(CommandHandler('help',helpText))
dp.add_handler(CommandHandler('elo',eloInquiry))
dp.add_handler(CommandHandler('elovon',eloInquiryFremd))

# dp.add_handler(CommandHandler('upUsers',updateUserDatabase))
# dp.add_handler(CommandHandler('eloProgress',eloProgressInquiry))
dp.add_handler(CommandHandler('bla',bla))
updater.start_polling()
updater.idle()

#####################
#     TODO
#     1- Parse user input
#     2- Ranking top 20
#     3- My Ranking
#     4- Welcome Message / Help
#     5- Spiel melden einfach
#     6- Spiel melden telegram
#     7- List of Pseudo
#     8- party
