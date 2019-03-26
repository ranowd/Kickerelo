import sqlite3

def dataByName(name):
	connection = sqlite3.connect('usersdb.db')
	cursor=connection.cursor()

	cursor.execute("SELECT * FROM users WHERE name = ?", (name,))
	data = cursor.fetchone()

	connection.close()

	if data is None:
		return -1
	else:
		return data

def dataByPseudo(pseudo):
	connection = sqlite3.connect('usersdb.db')
	cursor=connection.cursor()

	cursor.execute("SELECT * FROM users WHERE pseudo = ?", (pseudo,))
	data = cursor.fetchone()

	connection.close()

	if data is None:
		return -1
	else:
		return data

def dataByUsername(username):
	connection = sqlite3.connect('usersdb.db')
	cursor=connection.cursor()

	cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
	data = cursor.fetchone()

	connection.close()

	if data is None:
		return -1
	else:
		return data
