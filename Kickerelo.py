import random
import os
import sqlite3
import csv
import Elo_Algorythm as elo
import userManagement
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
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

    elos = []
    for player in players:
        try:
            elos.append(getELOs(player).iloc[-1])
        except:elos.append(100.00) # assume that players not in the list are new and have 100.00 ELO
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
    # print(matches)
    cursor.execute("SELECT elo_value FROM " + name)
    res = cursor.fetchall()
    elo = [x[0] for x in res]
    # print(elo)
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
    plt.xlabel('Spielnummer')
    plt.ylabel('ELO')
    plt.savefig("elo_plot.png", bbox_inches='tight', dpi=100)
    plt.clf()

def plotGameGraph(players, numGames):

    # extract players' ELOs and concat them into a df where each column is a player
    dfs = []
    for each in players:
        dfs.append(getELOs(each).tail(numGames).reset_index(drop=True))
    df = pd.concat(dfs, axis=1)
    df.columns = players
    for player in df.columns:
        shifts = pd.isna(df[player]).sum()
        if shifts > 0: df[player] = df[player].shift(periods=shifts)
    #df = df.fillna(method='ffill')

    # plot the last numGames games into a line plot
    df.plot(kind='line',y=df.columns)
    plt.title('die letzten {} Spiele'.format(numGames), alpha=0.6)
    plt.legend(ncol = 2, frameon = False, loc = 'upper center', bbox_to_anchor=(0.5, 0))
    plt.tick_params(top=False, bottom=False, left=False, right=False, labelleft=True, labelbottom=False)
    plt.yticks(alpha=0.4)
    plt.grid(axis = 'x')

    plt.savefig("elo_plot.png", bbox_inches='tight', dpi=100)
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
        # print(row[0])
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

def rankingFormat(ranking, elomaster = False, highlight = [], showLegends = False, showBeginners = False):
    # add the data needed to create the ranking text
    df = pd.DataFrame(ranking)
    df.columns = ["ELO", "player"]
    df[['nick', 'role', 'status']] = df['player'].apply(lambda x: pd.Series(userManagement.dataByName(x)[2:5]))
    df = df.merge((getGameCounts()>15).rename('quali'), left_on= 'player', right_index= True, how = 'left')
    df['nick'] = df['nick'].apply(lambda x: x[:4] if 'anon' in x else x)
    df['identity'] = df['nick']

    # active formatting depending on the function parameters
    if(elomaster == True): df['identity'] = df['player']
    if (showLegends == False): df = df[df['status'] != 'legend']
    if (showBeginners == False): df = df[df['quali'] == True]

    # create and output the formatted ranking text
    df.reset_index(drop = True, inplace = True)
    df['text'] = df.apply(lambda x: "{}: {} - {:.2f}".format((x.name + 1), x.identity, x.ELO), axis = 1)
    mask = df['player'].isin(highlight) # create a mask for users that shall be highlighted
    df.loc[mask, 'text'] = "<b>" + df.loc[mask, 'text'] + "</b>" # html Highlighting
    df['text'] += '\n' # linebreaks at the end of each ranking entry
    outputStr = "<b>Ranking:</b> \n" + "".join(df['text'].to_list())

    return outputStr

def getGames(playerName):
    # connect to the database
    connection = sqlite3.connect('ELO.db')
    cursor=connection.cursor()

    # fetch all matches as dataframe
    df = pd.read_sql_query("SELECT * FROM matches", connection).drop(["match_number"], axis=1)

    # filter matches of a specific player
    df = df[(df.drop(['goals_A', 'goals_B'], axis = 1) == playerName).any(axis = 1)]

    # Rearrange the the columns, so that the filtered player is always "player A1"
    df.loc[df['player_A2'] == playerName, ['player_A1', 'player_A2']] = df.loc[df['player_A2'] == playerName, ['player_A2', 'player_A1']].values
    df.loc[df['player_B2'] == playerName, ['player_B1', 'player_B2']] = df.loc[df['player_B2'] == playerName, ['player_B2', 'player_B1']].values
    df.loc[df['player_B1'] == playerName, ['player_A1', 'player_A2', 'player_B1', 'player_B2', 'goals_A', 'goals_B']] = df.loc[df['player_B1'] == playerName, ['player_B1', 'player_B2', 'player_A1', 'player_A2', 'goals_B', 'goals_A']].values

    connection.close()

    return df

def getGameCounts():
    # connect to the database
    connection = sqlite3.connect('ELO.db')
    cursor=connection.cursor()

    # fetch all matches as dataframe
    df = pd.read_sql_query("SELECT * FROM matches", connection).drop(["match_number"], axis=1)

    connection.close()

    # put all player occurences into one column
    allPlays =  df['player_A1'].append(df['player_A2']).append(df['player_B1']).append(df['player_B2'])

    counts = allPlays.value_counts()

    return counts

def getELOs(playerName):
    # connect to the database
    connection = sqlite3.connect('ELO.db')
    cursor=connection.cursor()

    # fetch elo entries for a specific player
    df = pd.read_sql_query("SELECT match_number, elo_value FROM " + playerName, connection).set_index("match_number", drop=True)['elo_value']

    connection.close()

    return df

def getStats(playerName):

    # fetch all matches and elo entries as dataframes
    df = getGames(playerName)
    df_elo = getELOs(playerName)

    #### Berechnung der stats

    #Elo stats
    maxElo = df_elo.max()
    minElo = df_elo.min()
    meanElo = df_elo.mean()
    medianElo = df_elo.median()

    #Games stats
    gamesPlayed = df.count()[0]
    wingman = df['player_A2'].value_counts().idxmax()
    nemesis = df['player_B1'].append(df['player_B2']).value_counts().idxmax()
    gewinnChance = ((df['goals_A']==10).sum()/(df['goals_A']==10).count())*100
    toreGesch = df["goals_A"].sum()
    toreKass = df["goals_B"].sum()
    torDifferenz = toreGesch-toreKass
    opfer = 2 * (df['goals_B']== 0).sum()

    #Calc consecutive wins
    df_wins = df.copy()
    df_wins['subgroup'] = (df_wins['goals_A'] != df_wins['goals_A'].shift(1)).cumsum()
    df_wins = df_wins[df_wins['goals_A']== 10]
    consWins = df_wins['subgroup'].value_counts().max()

    #Define the toreGesch/toreKass ratio
    geschKass = toreGesch/toreKass
    if geschKass > 1:
        geschKassA = round(geschKass, 1)
        geschKassB = 1
    else:
        geschKassA = 1
        geschKassB = round(1/geschKass, 1)

    #Define the Zielband
    nowElo = df_elo.iloc[-1]
    grenze = 70
    zielBand = 0
    if nowElo < grenze:
        pass
    else:
        while(True):
            if (int(nowElo) in range(grenze, grenze+10)):
                zielBand += 1
                break
            else:
                zielBand += 1
                grenze+=10
    # Pack everything into a dictionary
    statsDict = {   "gamesPlayed": gamesPlayed,
                    "maxElo": maxElo,
                    "minElo": minElo,
                    "meanElo": meanElo,
                    "medianElo": medianElo,
                    "toreGesch": toreGesch,
                    "toreKass": toreKass,
                    "torDifferenz": torDifferenz,
                    "geschKassA": geschKassA,
                    "geschKassB": geschKassB,
                    "zielBand": zielBand,
                    "gewinnChance": gewinnChance,
                    "wingman": wingman,
                    "nemesis": nemesis,
                    "opfer": opfer,
                    "consWins": consWins}

    ### Weitere Ideen
    # Längste Siegesserie
    return statsDict

def formatStats(stats, mode):
    if(mode == "private"):
        text =  """```
------Spielstatistik------
Spiele insgesamt: {}
Wingman: {}
Nemesis: {}
Tore geschossen: {}
Geschossen vs Kassiert: {} zu {}
Längste Siegesserie: {}
Zerstörte Gegner: {}
Gewinnchance: {:.2f}%\n
------ELO------
ZB: ELO-{}
Max: {:.2f}
Min: {:.2f}
Durchschnitt: {:.2f}
Median: {:.2f}
```""".format(*[stats.get(i)for i in ["gamesPlayed", "wingman", "nemesis", "toreGesch", "geschKassA", "geschKassB", "consWins", "opfer", "gewinnChance", "zielBand","maxElo", "minElo", "meanElo", "medianElo"]])
    elif(mode == "fremd"):
        text =  """```
------Spielstatistik------
Wingman: {}
Nemesis: {}
Geschossen vs Kassiert: {} zu {}
Längste Siegesserie: {}
Zerstörte Gegner: {}
Gewinnchance: {:.2f}%\n
------ELO------
ZB: ELO-{}
Max: {:.2f}
Min: {:.2f}
Durchschnitt: {:.2f}
Median: {:.2f}
```""".format(*[stats.get(i)for i in ["wingman", "nemesis", "geschKassA", "geschKassB", "consWins", "opfer", "gewinnChance", "zielBand","maxElo", "minElo", "meanElo", "medianElo"]])
    else: text = "Error"
    return text
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

def getLastGame():
    with open('match_history.csv', 'r') as f:
        gameString = list(csv.reader(f))[-1]
        return gameString

def addResultLine(csvRow):
   with open('match_history.csv','a') as f:
       f.write(csvRow)
       f.close()
