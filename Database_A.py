import random
import os
import sqlite3
import csv
import Elo_Algorythm as elo
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib import style
style.use("fivethirtyeight")


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


def create_table(table_name):
    cur.execute("CREATE TABLE IF NOT EXISTS " + table_name + " (match_number INTEGER, elo_value REAL)")
    elo_entry(table_name, 0, 100)
    connection.commit()
    return


def elo_entry(table_name, match_number, elo_value):
    cur.execute("INSERT INTO " + table_name + "(match_number, elo_value) VALUES (?, ?)", (match_number, elo_value))
    connection.commit()
    return


def elo_extract(players):
    elos = []
    for player in players:
        cur.execute("SELECT elo_value FROM " + player + " WHERE match_number = (SELECT max(match_number) FROM " + player + ")")
        read_value = cur.fetchall()
        elos.append(read_value[0][0])
    return elos


def match_entry(match):
    cur.execute("INSERT INTO matches (match_number, player_A1, player_A2, player_B1, player_B2, goals_A, goals_B) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (int(match[0]), match[1], match[2], match[3], match[4], int(match[5]), int(match[6])))
    connection.commit()
    return


def write_matchdata(match):
    match_entry(match)
    for j in range(1, 5):
        try:
            cur.execute("SELECT elo_value FROM " + match[j] + " WHERE match_number = 0")
        except:
            create_table(match[j])
            cur.execute("INSERT INTO players (ID, name) VALUES (?, ?)", (4, match[j]))
    elos_new = evaluate_match(match[1:5], int(match[6]) - int(match[5]))
    for j in range(1,5):
        elo = elos_new[j-1]
        elo_entry(match[j], match[0], elo)


def evaluate_match(players, GD):
    elos = elo_extract(players)
    EAB = elo.prediction(elos)
    SAB = elo.evaluation(GD)
    RAB = [(EAB[0] - SAB[0]), (EAB[1] - SAB[1])]
    elos_new = (elo.distribution(elos[0], elos[1], RAB[0]) + elo.distribution(elos[2], elos[3], RAB[1]))
    return elos_new


def read_playerdata(name):
    cur.execute("SELECT match_number FROM " + name)
    res = cur.fetchall()
    matches = [x[0] for x in res]
    print(matches)
    cur.execute("SELECT elo_value FROM " + name)
    res = cur.fetchall()
    elo = [x[0] for x in res]
    print(elo)
    return matches, elo


def plot_graph(x, y):
    plt.plot(x, y)


def plot_fullgraph(x,y):
    lim = max(x)
    x_full = []
    y_full = []
    y_curr = 100
    for k in range(0, lim+1):
        x_full.append(k)
        if k in x:
            x_curr = x.index(k)
            y_curr = y[x_curr]
        y_full.append(y_curr)
    plt.plot(x_full, y_full)



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




## connect Database



# if os.path.exists("./ELO.db"):
#     os.remove("./ELO.db")

## connect Database

connection = sqlite3.connect("ELO.db")
cur = connection.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS players (ID INTEGER, name TEXT, team Text, status Text)")
cur.execute("CREATE TABLE IF NOT EXISTS matches (match_number INTEGER, player_A1 TEXT, player_A2 TEXT, player_B1 TEXT, "
            "player_B2 TEXT, goals_A INTEGER, goals_B INTEGER)")
connection.commit()
cur.execute("SELECT max(match_number) FROM matches")
last_match = cur.fetchone()[0]
if last_match is None:
    last_match = 0


## Import matchfile

match_file = open("match_history.csv", "r")
reader = csv.reader(match_file, delimiter=";")

for row in reader:
    print(row[0])
    if int(row[0]) > last_match:
        write_matchdata(row)












# matches2plot, elo2plot = read_playerdata("Alia")
# # plot_graph(matches2plot, elo2plot)
# plot_fullgraph(matches2plot, elo2plot)


connection.close()
# match_file.close()
plt.show()
