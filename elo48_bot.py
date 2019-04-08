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

def eloProgressInquiry(update, conext):
  print("HEY")
  chat_id = update.message.chat_id
  user = update.message.from_user['username']
  userData = userManagement.dataByUsername(user)
  if(userData != -1):
      ELOdata = Kickerelo.read_playerdata(userData[1], Kickerelo.accessDatabase())
      Kickerelo.plot_fullgraph(ELOdata[0], ELOdata[1])
      #time.sleep(5)
      #ToDo fetch elo score
      print("HEY")
      context.bot.send_photo(chat_id=chat_id, photo = open('elo_plot.png', 'rb'))
      time.sleep(0.5)
      os.remove("elo_plot.png")
  else:
      notAllowed(bot, chat_id, "Own progress Inquiry")

def checkAdmin(update):
  user = update.message.from_user['username']
  userData = userManagement.dataByUsername(user)
  if(userData[0] == elomaster): return True
  else: return False

def updateUserDatabase(update, context):
  chat_id = update.message.chat_id
  if(checkAdmin(update)):
    userManagement.csvUpdatePlayerDb()
    context.bot.send_message(chat_id=chat_id, text="Aktualisiert!")
  else:
      notAllowed(bot, chat_id, "Update user Database")

def bla(update, context):
  print(update.message.text)
  print(context.args)
  context.bot.send_message(chat_id=chat_id, text="Hi")

def newresult(update, context):
  if(checkAdmin(update)):
    print(Kickerelo.getLastGame())
    lastGameNum = int(Kickerelo.getLastGame()[0].split(";")[0]) # Get the first part of the last macht, which is the game number
    print(lastGameNum)
    Game1Str = "{};{}\n".format((lastGameNum+1), context.args[0])
    Game2Str = "{};{}\n".format((lastGameNum+2), context.args[1])
    Kickerelo.addResultLine(Game1Str)
    Kickerelo.addResultLine(Game2Str)
    chat_id = update.message.chat_id
    context.bot.send_message(chat_id=chat_id, text="Spiele {} und {} wurden erfolgreich hinzugefügt.".format((lastGameNum+1), (lastGameNum+2)))
    players = Game1Str.split(";")[1:5] # extract player names for the analysis part
    elosBefore = Kickerelo.elo_extract(players) # extract the elo before updating the results
    Kickerelo.updateDatabase() # update the elo database
    elosAfter = Kickerelo.elo_extract(players)
    ## Match analysis
    # elo difference
    elosDifference = elosAfter - elosBefore # calculate elo difference
    elosDifferenceText = "ELO Difference:\n"
    for player, diff in zip(players,elosDifference):
      elosDifferenceText += "{}: {}\n".format(player, diff)
    #ranking
    ranking = Kickerelo.ranking() # get current ranking
    rankingText = Kickerelo.rankingFormat(ranking, True, players, 0)
    #todo match analysis: graphs with progress
    #todo print match analysis: elo difference, ranking, graphs with progress
    context.bot.send_message(chat_id=chat_id, text=elosDifferenceText)
    context.bot.send_message(chat_id=chat_id, text=rankingText)
    #todo send the analysis results to all the players
  else:
    notAllowed(bot, chat_id, "Add new results")




updater = Updater(token, use_context=True)
dp = updater.dispatcher

#logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#                     level=logging.INFO)

dp.add_handler(CommandHandler('start',start))
dp.add_handler(CommandHandler('help',helpText))
dp.add_handler(CommandHandler('elo',eloInquiry))
dp.add_handler(CommandHandler('elovon',eloInquiryFremd))
dp.add_handler(CommandHandler('newresult',newresult))

# dp.add_handler(CommandHandler('upUsers',updateUserDatabase))
dp.add_handler(CommandHandler('eloProgress',eloProgressInquiry))
dp.add_handler(CommandHandler('bla',bla))
updater.start_polling()
updater.idle()

#####################
#     TODO
#
#     2- Ranking top 20
#     3- My Ranking
#     4- Welcome Message / Help
#     5- Spiel melden einfach
#     6- Spiel melden telegram
#     7- List of Pseudo
#     8- party
