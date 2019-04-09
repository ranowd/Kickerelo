import random
import os
import sqlite3
import csv
import Elo_Algorythm as elo
import userManagement
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib import style
style.use("fivethirtyeight")


# generate random matches
def write_a_match_to_file(match_number):
    file_object.write(str(match_number) + ";")
    players = []
    player  = ""
    while len(players)<4:
        player = random.choice(Names)
        if player in players:
            player = ""
        else:
            players.append(player)
    for player_count in range(4):
        file_object.write(players[player_count]+";")
    file_object.write("10;")
    file_object.write(str(random.randint(0, 9)) + ";" + "\n")
    return


# Create a table in the Database with the name of the player
# contains number of match played and Elo value after the match
def create_table(cursor, connection, table_name):
    cursor.execute("CREATE TABLE IF NOT EXISTS " + table_name + " (match_number INTEGER, elo_value REAL)")
    # First entry is start value (100) at match 0
    elo_entry(cursor, table_name, 0, 100)
    connection.commit()
    return


# Enter the updated Elo after a match into the table with the players name
def elo_entry(cursor, table_name, match_number, elo_value):
    cursor.execute("INSERT INTO " + table_name + "(match_number, elo_value) VALUES (?, ?)", (match_number, elo_value))
    #connection.commit()
    return


# Get the current Elo of a list of player from their respective table
def elo_extract(players):
    connection = sqlite3.connect("ELO.db")
    cur = connection.cursor()
    elos = []
    for player in players:
        cur.execute("SELECT elo_value FROM " + player + " WHERE match_number = (SELECT max(match_number) FROM " + player + ")")
        read_value = cur.fetchall()
        elos.append(read_value[0][0])
    return elos


# Enter a match into the match history table
def match_entry(cursor, match):
    cursor.execute("INSERT INTO matches (match_number, player_A1, player_A2, player_B1, player_B2, goals_A, goals_B) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (int(match[0]), match[1], match[2], match[3], match[4], int(match[5]), int(match[6])))
    #connection.commit()
    return


# Evaluate match and enter data into tables
def write_matchdata(cursor,connection, match):
    # enter match into match history
    match_entry(cursor, match)
    # check if tables for all players exist, if not create them
    for j in range(1, 5):
        try:
            cursor.execute("SELECT elo_value FROM " + match[j] + " WHERE match_number = 0")
        except:
            # create players table
            create_table(cursor, connection, match[j])
            # insert player into table of players
            cursor.execute("INSERT INTO players (ID, name) VALUES (?, ?)", (4, match[j]))

    # calculate new elo values from match data
    elos_new = evaluate_match(match[1:5], int(match[6]) - int(match[5]))

    # enter new elo values into players table
    for j in range(1, 5):
        # elo = elos_new[j-1]
        # elo_entry(match[j], match[0], elo)
        elo_entry(cursor, match[j], match[0], elos_new[j-1])

    connection.commit()

# calculate new elos from matchdata
def evaluate_match(players, goal_difference):
    elos = elo_extract(players)
    expectations = elo.prediction(elos)
    performances = elo.evaluation(goal_difference)
    ratings = [(expectations[0] - performances[0]), (expectations[1] - performances[1])]
    elos_new = (elo.distribution(elos[0], elos[1], ratings[0]) + elo.distribution(elos[2], elos[3], ratings[1]))
    return elos_new


def read_playerdata(name, cursor):
    cursor.execute("SELECT match_number FROM " + name)
    res = cursor.fetchall()
    matches = [x[0] for x in res]
    print(matches)
    cursor.execute("SELECT elo_value FROM " + name)
    res = cursor.fetchall()
    elo = [x[0] for x in res]
    print(elo)
    return matches, elo


def plot_graph(x, y):
    plt.plot(x, y)


def plot_fullgraph(x, y):
    lim = max(x)
    x_full = []
    y_full = []
    y_curr = 100
    for k in range(min(x), lim+1):
        x_full.append(k)
        if k in x:
            x_curr = x.index(k)
            y_curr = y[x_curr]
        y_full.append(y_curr)
    plt.plot(x_full, y_full)
    plt.savefig("elo_plot.png", dpi=100)
    plt.clf()

def plotGameGraph(x, y):
    lim = max(x)
    x_full = [[], [], [], []]
    y_full = [[], [], [], []]
    y_curr = 100
    for i in range(4):
        for k in range(0, lim+1):
            x_full.append(k)
            if k in x:
                x_curr = x.index(k)
                y_curr = y[x_curr]
            y_full.append(y_curr)
    plt.plot(x_full, y_full)
    plt.savefig("elo_plot.png", dpi=100)
    plt.clf()

# import matches from match_history.csv
def import_match_history(cursor, connection):
    # Get number of last match in database
    cursor.execute("SELECT max(match_number) FROM matches")
    last_match = cursor.fetchone()[0]
    if last_match is None:
        last_match = 0

    # open file
    match_file = open("match_history.csv", "r")
    reader = csv.reader(match_file, delimiter=";")

    # analyze all matches that are new
    for row in reader:
        print(row[0])
        if int(row[0]) > last_match:
            write_matchdata(cursor, connection, row)

    match_file.close()
    connection.commit()

def generate_player_list():
    connection = sqlite3.connect("ELO.db")
    cur = connection.cursor()
    cur.execute("SELECT name FROM " + "players")
    res = cur.fetchall()
    players = [x[0] for x in res]
    return players

def ranking():
    players = generate_player_list()
    elos = elo_extract(players)
    elosPlayers = zip(elos, players)
    ranking = sorted(elosPlayers)
    ranking.reverse()
    return ranking

def rankingFormat(ranking, elomaster = False, highlight = [], legends = 0):
    i = 1
    identity = 2
    if(elomaster == True): identity = 1
    outputStr = "Ranking:\n"
    for item in ranking:
        player = userManagement.dataByName(item[1])
        if((legends == 0) and (player[4] == "legend")):
            continue
        if(player[1] in highlight):
            outputStr += "{}: {} - {:.2f}\n".format(i, player[identity], item[0]) #todo actual highlighting
        else:
            outputStr += "{}: {} - {:.2f}\n".format(i, player[identity], item[0])
        i += 1
    return outputStr
# if os.path.exists("./matchhistorie.csv"):
#     print("hamwa")
# else:
#     Names = ["Alia", "Hilma", "Debbra", "Austin", "Carola", "Verlene", "Matthew", "Maureen", "Dwana", "Kristal",
#              "Khadijah", "Laura",
#              "Annalisa", "Fransisca", "Youlanda", "Nolan", "Garnett", "Malcolm", "Ching", "Mandie", "Jillian",
#              # "Destiny", "Stacey",
#              # "Jamison", "Lance", "Gina", "Valerie", "Christiane", "Chieko", "Elane", "Nickie", "Glayds", "Doria",
#              # "Mozell", "Shae",
#              # "Jayme", "Syble", "Julieann", "Zetta", "Belkis", "Louvenia", "Madalene", "Nikia", "Clifton", "Randa",
#              "Jacob", "Madaline",
#              "Billye", "Rosalva", "Jacquetta"]
#     file_object = open("matchhistorie.csv", "w")
#     for i in range(500):
#          write_a_match_to_file(i+1)
#     file_object.close()



# if os.path.exists("./ELO.db"):
#     os.remove("./ELO.db")

## connect Database


########## MAIN ###################
def updateDatabase():
    connection = sqlite3.connect("ELO.db")
    cur = connection.cursor()

    # create a table with all player names and their Data
    cur.execute("CREATE TABLE IF NOT EXISTS players (ID INTEGER, name TEXT, team Text, status Text)")
    # create a table witch contains the match history
    cur.execute("CREATE TABLE IF NOT EXISTS matches (match_number INTEGER, player_A1 TEXT, player_A2 TEXT, player_B1 TEXT, "
                "player_B2 TEXT, goals_A INTEGER, goals_B INTEGER)")
    connection.commit()

    # import match history
    import_match_history(cur, connection)
    connection.commit()

    return cur

def accessDatabase():
    connection = sqlite3.connect("ELO.db")
    cur = connection.cursor()
    return cur


    #matches2plot, elo2plot = read_playerdata("Rano_M")
    #plot_graph(matches2plot, elo2plot)
    #plot_fullgraph(matches2plot, elo2plot)

   # connection.close()
# match_file.close()
#plt.show()
#plt.savefig("test_plot.png", dpi=100)

def getLastGame():
    with open('match_history.csv', 'r') as f:
        gameString = list(csv.reader(f))[-1]
        return gameString

def addResultLine(csvRow):
   with open('match_history.csv','a') as f:
       f.write(csvRow)
       f.close()
