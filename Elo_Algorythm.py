# Parameters
P_1 = 100.0
P_2 = 100.0
P_3 = 10.0

# polynom coefficients
A_0 = 0.5
A_1 = 0.025
A_2 = -86.7361737988404 * 10 ** (-20)
A_3 = 0.00075


def prediction(elos):
    elo_A = elos[0] + elos[1]
    elo_B = elos[2] + elos[3]
    expect_A = P_3 * 1 / (1 + P_1 ** ((elo_A - elo_B) / P_2))
    expect_B = P_3 * 1 / (1 + P_1 ** ((elo_B - elo_A) / P_2))
    return expect_A, expect_B


def evaluation(goal_diff):
    eval_A = P_3 * (A_3 * goal_diff ** 3 + A_2 * goal_diff ** 2 + A_1 * goal_diff + A_0)
    eval_B = P_3 * (A_3 * -goal_diff ** 3 + A_2 * -goal_diff ** 2 + A_1 * -goal_diff + A_0)
    return eval_A, eval_B


def distribution(elo_1, elo_2, elo_all):
    perc_1 = elo_1/(elo_1 + elo_2)
    perc_2 = 1-perc_1
    if elo_all < 1:
        elo_1 = elo_all * perc_1 + elo_1
        elo_2 = elo_all * perc_2 + elo_2
    else:
        elo_1 = elo_all * (1 - perc_1) + elo_1
        elo_2 = elo_all * (1 - perc_2) + elo_2
    return elo_1, elo_2
