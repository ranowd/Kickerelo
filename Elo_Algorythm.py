# Parameters for prediction
# values are guesses
P_1 = 100.0
P_2 = 100.0

# Parameters for evaluation
# Eval(goaldiff = 10) = 1.5
# Eval(goaldiff = 0) = 0.5
# Eval(goaldiff = -10) = -0.5
# d_Eval(goaldiff = 0) = 0.025
P_3 = 10.0
A_0 = 0.5
A_1 = 0.025
A_2 = -86.7361737988404 * 10 ** (-20)
A_3 = 0.00075


# calculate an expectation based on elo values
def prediction(elos):
    # elo values of both teams are added up
    elo_A = elos[0] + elos[1]
    elo_B = elos[2] + elos[3]

    # expectation based on a logistic curve
    expect_A = P_3 * 1 / (1 + P_1 ** ((elo_A - elo_B) / P_2))
    expect_B = P_3 * 1 / (1 + P_1 ** ((elo_B - elo_A) / P_2))
    return expect_A, expect_B


# evaluate the actual outcome of the match
def evaluation(goal_diff):
    # polynomial curve to punish high defeats harder
    eval_A = P_3 * (A_3 * goal_diff ** 3 + A_2 * goal_diff ** 2 + A_1 * goal_diff + A_0)
    eval_B = P_3 * (A_3 * -goal_diff ** 3 + A_2 * -goal_diff ** 2 + A_1 * -goal_diff + A_0)
    return eval_A, eval_B


# distribute the won/lost elo between the teammates
# higher rated players lose more and gain less
def distribution(elo_1, elo_2, elo_all):
    # calculate shares in elo value before the match
    perc_1 = elo_1/(elo_1 + elo_2)
    perc_2 = 1-perc_1

    # distribution when losing
    if elo_all < 1:
        elo_1 = elo_all * perc_1 + elo_1
        elo_2 = elo_all * perc_2 + elo_2
    # distribution when winning
    else:
        elo_1 = elo_all * (1 - perc_1) + elo_1
        elo_2 = elo_all * (1 - perc_2) + elo_2
    return elo_1, elo_2
