import random
import os
import sqlite3
import csv
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib import style
style.use("fivethirtyeight")

P_1 = 100.0
P_2 = 100.0
P_3 = 10.0
A_0 = 0.5
A_1 = 0.025
A_2 = -86.7361737988404 * 10 ** (-20)
A_3 = 0.00075


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


def write_matchdata(match):
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
    EAB = match_prediction(elos[0]+elos[1], elos[2]+elos[3])
    SAB = result_evaluation(GD)
    RAB = [P_3 * (EAB[0] - SAB[0]), P_3 * (EAB[1] - SAB[1])]
    elos_new = (elo_distribution(elos[0], elos[1], RAB[0]) + elo_distribution(elos[2], elos[3], RAB[1]))
    return elos_new


def match_prediction(elo_A, elo_B):
    expect_A = 1 / (1 + P_1 ** ((elo_A - elo_B) / P_2))
    expect_B = 1 / (1 + P_1 ** ((elo_B - elo_A) / P_2))
    return expect_A, expect_B


def result_evaluation(goal_diff):
    eval_A = A_3 * goal_diff ** 3 + A_2 * goal_diff ** 2 + A_1 * goal_diff + A_0
    eval_B = A_3 * -goal_diff ** 3 + A_2 * -goal_diff ** 2 + A_1 * -goal_diff + A_0
    return eval_A, eval_B


def elo_distribution(elo_1, elo_2, elo_all):
    perc_1 = elo_1/(elo_1 + elo_2)
    perc_2 = 1-perc_1
    if elo_all < 1:
        elo_1 = elo_all * perc_1 + elo_1
        elo_2 = elo_all * perc_2 + elo_2
    else:
        elo_1 = elo_all * (1 - perc_1) + elo_1
        elo_2 = elo_all * (1 - perc_2) + elo_2
    return elo_1, elo_2


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



if os.path.exists("./matchhistorie.csv"):
    print("hamwa")
else:
    Names = ["Alia", "Hilma", "Debbra", "Austin", "Carola", "Verlene", "Matthew", "Maureen", "Dwana", "Kristal",
             "Khadijah", "Laura",
             "Annalisa", "Fransisca", "Youlanda", "Nolan", "Garnett", "Malcolm", "Ching", "Mandie", "Jillian",
             # "Destiny", "Stacey",
             # "Jamison", "Lance", "Gina", "Valerie", "Christiane", "Chieko", "Elane", "Nickie", "Glayds", "Doria",
             # "Mozell", "Shae",
             # "Jayme", "Syble", "Julieann", "Zetta", "Belkis", "Louvenia", "Madalene", "Nikia", "Clifton", "Randa",
             "Jacob", "Madaline",
             "Billye", "Rosalva", "Jacquetta"]
    file_object = open("matchhistorie.csv", "w")
    for i in range(500):
         write_a_match_to_file(i+1)
    file_object.close()

# if os.path.exists("./ELO.db"):
#     os.remove("./ELO.db")

connection = sqlite3.connect("ELO.db")
cur = connection.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS players (ID INTEGER, name TEXT)")
connection.commit()

match_file = open("matchhistorie.csv", "r")
reader = csv.reader(match_file, delimiter=";")

# for row in reader:
#     write_matchdata(row)

# matches2plot, elo2plot = read_playerdata("Alia")
# plot_graph(matches2plot, elo2plot)
# plot_fullgraph(matches2plot, elo2plot)


connection.close()
match_file.close()
plt.show()
