import sqlite3
import Kickerelo
import csv
import os
import csv2sqlite

def dataByName(name):
	# connect to the database
	connection = sqlite3.connect('usersdb.db')
	cursor=connection.cursor()
	# search for user by name
	cursor.execute("SELECT * FROM users WHERE name = ?", (name,))
	data = cursor.fetchone()
	connection.close()
	# return user data
	if data is None:
		return -1
	else:
		return data

def dataByPseudo(pseudo):
	# connect to the database
	connection = sqlite3.connect('usersdb.db')
	cursor=connection.cursor()
	# search for user by pseudo
	cursor.execute("SELECT * FROM users WHERE pseudo = ?", (pseudo,))
	data = cursor.fetchone()
	connection.close()
	# return user data
	if data is None:
		return -1
	else:
		return data

def dataByUsername(username):
	# connect to the database
	connection = sqlite3.connect('usersdb.db')
	cursor=connection.cursor()
	# search for user by pseudo
	cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
	data = cursor.fetchone()
	connection.close()
	# return user data
	if data is None:
		return -1
	else:
		return data

def allChatids():
	# connect to the database
	connection = sqlite3.connect('usersdb.db')
	cursor=connection.cursor()
	# get all chat_ids
	cursor.execute("SELECT chatid FROM users WHERE chatid != ?", ("",))
	data = cursor.fetchall()
	data = [i[0] for i in data]
	connection.close()
	# return a list with all chat_ids
	if data is None:
		return -1
	else:
		return data

def csvAddNewPlayer(username, name, pseudo, role, status, team):
	newPlayerData = '"{}","{}","{}","{}","{}","{}",""\n'.format(username, name, pseudo, role, status, team)
	with open('userlist.csv','a') as f:
		f.write(newPlayerData)
		f.close()

def csvUpdatePlayerDb():
	try:
		os.remove("usersdb.db")
	except:pass
	csv2sqlite.convert("userlist.csv", "usersdb.db", "users")

def autoAddNewPlayers():
	csvUpdatePlayerDb()
	playersFromGames = Kickerelo.generate_player_list()
	for player in playersFromGames:
		if(dataByName(player) == -1):
			with open('userlist.csv') as f:
				rowCount = sum(1 for row in f) # count how many players already exist
			csvAddNewPlayer("", player, "anon"+str(rowCount), "player", "aktiv", "Probezeit")

def editSpecificPlayer(name, inputList):
	with open('userlist.csv') as inf:
		reader = csv.reader(inf.readlines())
	with open('userlist.csv', 'w') as outf:
		found = 0 # a flag stating if the user was found in the list
		writer = csv.writer(outf, quoting = csv.QUOTE_ALL)
		fltrInputList = inputList.copy()
		for line in reader:
			if line[1] == name:
				for i in range(len(fltrInputList)):
					if(fltrInputList[i] == "-1"):
						fltrInputList[i] = line[i]
				writer.writerow([fltrInputList[0], line[1], fltrInputList[2], fltrInputList[3], fltrInputList[4], fltrInputList[5], fltrInputList[6]])
				found = 1
				break
			else:
				writer.writerow(line)
		writer.writerows(reader)
		return found

def createUserListFile():
	text = "options = ['player',"
	players = Kickerelo.generate_player_list()
	players.sort()
	for name in players:
		player = dataByName(name)
		if(player[4] == "aktiv"):
			text += "'{}',".format(name)
	text = text[:-1]
	text += "]"
	with open('players.py', 'w') as f:
		f.write(text)
		f.close()
