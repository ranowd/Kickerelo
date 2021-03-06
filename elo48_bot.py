from telegram.ext import Updater, CommandHandler
import telegram
from credentials import token, elomaster
import logging
import csv2sqlite
import userManagement
import Kickerelo
import time
import os
import pandas as pd
from datetime import datetime
from requests import get

## General
def readMessages(filePath):
  with open(filePath, encoding='utf8') as f:
    text = f.read()
    return text

## User Basic interaction
def start(update, context):
  chat_id = update.message.chat_id
  user = update.message.from_user['username']
  userData = userManagement.dataByUsername(user)
  if(userData != -1):
    context.bot.send_message(chat_id=chat_id, text=readMessages("messages/welcome.txt").format(elomaster))
    if(update.message.chat.type == "private"):
      dataList = 7*['-1']
      dataList[-1] = str(chat_id)
      userManagement.editSpecificPlayer(userData[1], dataList)
  else:
    notAllowed(update, context, chat_id, "start")

def helpText(update, context):
  chat_id = update.message.chat_id
  user = update.message.from_user['username']
  userData = userManagement.dataByUsername(user)
  if(userData != -1):
    context.bot.send_message(chat_id=chat_id, text=readMessages("messages/commands.txt"), parse_mode=telegram.ParseMode.MARKDOWN)
    print("Help text viewed")
  else:
    notAllowed(update, context, chat_id, "help")
  if(checkAdmin(update)):context.bot.send_message(chat_id=chat_id, text=readMessages("messages/commandsAdmin.txt"), parse_mode=telegram.ParseMode.MARKDOWN)

def eloInquiry(update, context):
  chat_id = update.message.chat_id
  user = update.message.from_user['username']
  userData = userManagement.dataByUsername(user)
  if(userData != -1):
      currentELO = Kickerelo.getELOs(userData[1]).iloc[-1]
      context.bot.send_message(chat_id=chat_id, text="Deine aktuelle ELO beträgt: {:.2f}".format(currentELO))
      print("Read Elo")
  else:
    notAllowed(update, context, chat_id, "elo Inquiry")

def eloInquiryFremd(update, context):
  chat_id = update.message.chat_id
  user = update.message.from_user['username']
  userDataRequester = userManagement.dataByUsername(user)
  if(userDataRequester != -1):
    userDataFremd = userManagement.dataByPseudo(context.args[0])
    print(context.args[0])
    if(userDataFremd != -1):
      currentELO = Kickerelo.getELOs(userDataFremd[1]).iloc[-1]
      context.bot.send_message(chat_id=chat_id, text="Die aktuelle ELO von {} beträgt: {:.2f}".format(context.args[0], currentELO))
      print("Read Elo von")
    else:
      context.bot.send_message(chat_id=chat_id, text="User Leider nicht gefunden.")
  else:
    notAllowed(update, context, chat_id, "elo Inquiry fremd")

def statsInquiry(update, context):
  chat_id = update.message.chat_id
  user = update.message.from_user['username']
  userData = userManagement.dataByUsername(user)
  if(userData != -1):
      playerStats = Kickerelo.getStats(userData[1])
      context.bot.send_message(chat_id=chat_id, text="*Deine stats*\n{}".format(Kickerelo.formatStats(playerStats,"private")), parse_mode=telegram.ParseMode.MARKDOWN)
      print("Read Stats")
  else:
    notAllowed(update, context, chat_id, "stats Inquiry")

def statsInquiryFremd(update, context):
  chat_id = update.message.chat_id
  user = update.message.from_user['username']
  userDataRequester = userManagement.dataByUsername(user)
  if(userDataRequester != -1):
    userDataFremd = userManagement.dataByPseudo(context.args[0])
    print(context.args[0])
    if(userDataFremd != -1):
      playerStats = Kickerelo.getStats(userDataFremd[1])
      context.bot.send_message(chat_id=chat_id, text="*Stats von {}*\n{}".format(context.args[0], Kickerelo.formatStats(playerStats,"fremd")), parse_mode=telegram.ParseMode.MARKDOWN)
      print("Read Stats von {}".format(context.args[0]))
    else:
      context.bot.send_message(chat_id=chat_id, text="User Leider nicht gefunden.")
  else:
    notAllowed(update, context, chat_id, "elo Inquiry fremd")

def eloProgressInquiry(update, context):
  chat_id = update.message.chat_id
  user = update.message.from_user['username']
  userData = userManagement.dataByUsername(user)
  if(userData != -1):

      Kickerelo.plotGameGraph([userData[1]], 100)
      #time.sleep(5)
      context.bot.send_photo(chat_id=chat_id, photo = open('elo_plot.png', 'rb'))
      time.sleep(0.5)
      os.remove("elo_plot.png")
      print("Elo progress")
  else:
      notAllowed(update, context, chat_id, "Own progress Inquiry")

def lastRoundInquiry(update, context):
  chat_id = update.message.chat_id
  user = update.message.from_user['username']
  userData = userManagement.dataByUsername(user)
  if(userData != -1):
    try:
      r = int(context.args[0])
    except: r = 1

    if(r > 0) & (r < 11):
      rounds = r
    else:
      rounds = 1

    textAlle = ""
    df = Kickerelo.getELOs(userData[1]).iloc[-(1 + rounds*2):].reset_index(drop=True)
    df2 = Kickerelo.getGames(userData[1]).iloc[-2*rounds:].reset_index(drop=True)
    df2['diffs'] = (df - df.shift(1)).shift(-1)
    df2[["goals_AR", "goals_BR", "diffsR"]] = df2[["goals_A", "goals_B", "diffs"]].shift(-1)
    df2 = df2.iloc[::2]

    #userData[2]

    df2['text'] = df2.apply(lambda x : x.to_list(), axis = 1)
    resString = "\n{}+{} vs.\n{}+{}:\nH: {:.0f} zu {:.0f} ({:.2f})\nR: {:.0f} zu {:.0f} ({:.2f})\n"

    text = df2['text'].apply(lambda x: resString.format(*([userManagement.dataByName(x[0])[2],
                                                          userManagement.dataByName(x[1])[2],
                                                          userManagement.dataByName(x[2])[2],
                                                          userManagement.dataByName(x[3])[2]]+x[4:]))).to_list()

    textAlle = "".join(text)
    context.bot.send_message(chat_id=chat_id, text="*Letzte Runde(n)*\n`{}`".format(textAlle), parse_mode=telegram.ParseMode.MARKDOWN)
    print("Get last round")
  else:
    notAllowed(update, context, chat_id, "lastRound Inquiry")

def getRanking(update, context):
  chat_id = update.message.chat_id
  user = update.message.from_user['username']
  userData = userManagement.dataByUsername(user)
  if(userData != -1):
    ranking = Kickerelo.ranking() # get current ranking
    if(checkAdmin(update)):
      rankingText = Kickerelo.rankingFormat(ranking, True, [userData[1]], 0)
      # rankingText = Kickerelo.rankingFormat(ranking, False, [userData[1]], 0)
    else:
      rankingText = Kickerelo.rankingFormat(ranking, False, [userData[1]], 0)
    context.bot.send_message( chat_id=chat_id,
                              text=rankingText,
                              parse_mode=telegram.ParseMode.HTML)
    print("get Ranking")
  else: notAllowed(update, context, chat_id, "get ranking")

def mahlzeit(update, context):
  chat_id = update.message.chat_id
  user = update.message.from_user['username']
  userData = userManagement.dataByUsername(user)
  if(userData != -1):
    now = datetime.now()
    dateNow = now.strftime("%d.%m.%Y")
    foodf = pd.read_csv('food.csv')
    try:
      veg = foodf.loc[foodf['text']==dateNow]['veg_g'].item()
      fleisch = foodf.loc[foodf['text']==dateNow]['fleisch_g'].item()
      if(foodf.loc[foodf['text']==dateNow]['dessert'].item()): dessert = "🍰"
      else: dessert = "🥗"
      foodText = "Mahlzeit! Heute gibt es folgendes in der Kantine:\n\n{}\n\n{}\n\n{}".format(fleisch, veg, dessert)

    except:
      foodText = "Mahlzeit! Leider weiß ich nicht, was es heute zum Essen gibt."

    context.bot.send_message( chat_id=chat_id,
                              text=foodText,
                              parse_mode=telegram.ParseMode.HTML)
  else: notAllowed(update, context, chat_id, "mahlzeit")
## Key User Interactions

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
    userManagement.autoAddNewPlayers()
    userManagement.csvUpdatePlayerDb()
    elosAfter = Kickerelo.elo_extract(players)
    ## Match analysis
    # elo difference
    elosDifference = [a_i - b_i for a_i, b_i in zip(elosAfter, elosBefore)] # calculate elo difference
    elosDifferenceText = "<b>ELO Difference:</b>\n"
    for player, diff in zip(players,elosDifference):
      elosDifferenceText += "{}: {:.2f}\n".format(player, diff)
    #ranking
    ranking = Kickerelo.ranking() # get current ranking
    rankingText = Kickerelo.rankingFormat(ranking, True, players, 0)

    Kickerelo.plotGameGraph(players, 30)
    #todo print match analysis: elo difference, ranking, graphs with progress
    context.bot.send_message(chat_id=chat_id, text=rankingText, parse_mode=telegram.ParseMode.HTML)
    context.bot.send_message(chat_id=chat_id, text=elosDifferenceText, parse_mode=telegram.ParseMode.HTML)
    context.bot.send_photo(chat_id=chat_id, photo = open('elo_plot.png', 'rb'))
    time.sleep(0.5)
    os.remove("elo_plot.png")
    notifyPlayers(players, elosAfter, elosDifference, context)
    #todo send the analysis results to all the players
  else: notAllowed(update, context, chat_id, "Add new results")

def notifyPlayers(players, elosAfter, elosDifference, context):
  for player, eAfter, eDiff in zip(players, elosAfter, elosDifference):
    chat_id = userManagement.dataByName(player)[6]
    if(chat_id != None):
      messageText = """
`-------Spieleintrag-------`
Neue ELO: *{:.2f}*
Differenz: *{:.2f}*
`--------------------------`
Mehr Infos: /lastround""".format(eAfter, eDiff)
      try:
        context.bot.send_message(chat_id=chat_id, text=messageText, parse_mode=telegram.ParseMode.MARKDOWN)
      except:pass


## Permissions and User Management
def notAllowed(update, context, chat_id, logmessage):
  print(elomaster)
  automessage = "Leider ist dein user nicht freigeschaltet, kontaktiere bitte ELO business associate @{}".format(elomaster)
  #print(automessage)
  context.bot.send_message(chat_id=chat_id, text=automessage)
  now = datetime.now()
  date_time = now.strftime("%d/%m/%Y - %H:%M:%S")
  username = update.message.chat.username
  first = update.message.chat.first_name
  last = update.message.chat.last_name
  logText = "{}: {} {}, {}, {}\n".format(date_time, first, last, username, logmessage)
  print(logText)
  with open('violations_log.csv','a') as f:
    f.write(logText)
    f.close()

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
      notAllowed(update, context, chat_id, "Update user Database")

def editPlayer(update, context):
  chat_id = update.message.chat_id
  if(checkAdmin(update)):
    userDataList = context.args[0].split(";")
    userDataList.append('-1')
    name = userDataList[1]
    if(len(userDataList)==7):
      userManagement.editSpecificPlayer(name, userDataList)
      context.bot.send_message(chat_id=chat_id, text="Spieler wurde aktualisiert.")
      userManagement.csvUpdatePlayerDb()
    else: context.bot.send_message(chat_id=chat_id, text="Geht nicht, falsche Eingabe.")
  else:
      notAllowed(update, context, chat_id, "send user list")

def sendUserList(update, context):
  chat_id = update.message.chat_id
  if(checkAdmin(update)):
    userManagement.createUserListFile()
    context.bot.send_document(chat_id=chat_id, document=open('players.py','rb'))
    try:
      os.remove('players.py')
    except:pass
  else:
      notAllowed(update, context, chat_id, "send user list")

## Dev Functions
def announceRelease(update, context):
  if(checkAdmin(update)):
    chat_id = update.message.chat_id
    allChats = userManagement.allChatids()
    for chat in allChats:
      context.bot.send_message(chat_id=chat, text=readMessages("messages/releaseNotes.txt"), parse_mode=telegram.ParseMode.MARKDOWN)
  else: notAllowed(update, context, chat_id, "announce new release")

def ipFetch(update, context):
  if(checkAdmin(update)):
    chat_id = update.message.chat_id
    ip = get('https://api.ipify.org').text
    context.bot.send_message( chat_id=chat_id, text=ip)
  else: notAllowed(update, context, chat_id, "Fetch the ip")

#def startUpFunctions():
#    Kickerelo.updateDatabase()


##############
updater = Updater(token, use_context=True)
dp = updater.dispatcher

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
#####################
#
#     General User Functions
#
dp.add_handler(CommandHandler('start',start))
dp.add_handler(CommandHandler('help',helpText))
dp.add_handler(CommandHandler('elo',eloInquiry))
dp.add_handler(CommandHandler('elovon',eloInquiryFremd))
dp.add_handler(CommandHandler('eloProgress',eloProgressInquiry))
dp.add_handler(CommandHandler('ranking',getRanking))
dp.add_handler(CommandHandler('stats',statsInquiry))
dp.add_handler(CommandHandler('statsvon',statsInquiryFremd))
dp.add_handler(CommandHandler('lastRound',lastRoundInquiry))
dp.add_handler(CommandHandler('mahlzeit',mahlzeit))
#
#     Admin Functions
#
# dp.add_handler(CommandHandler('upUsers',updateUserDatabase))
dp.add_handler(CommandHandler('newresult',newresult))
dp.add_handler(CommandHandler('editPlayer',editPlayer))
dp.add_handler(CommandHandler('sendUserList',sendUserList))
dp.add_handler(CommandHandler('announceRelease',announceRelease))
dp.add_handler(CommandHandler('ip',ipFetch))


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
