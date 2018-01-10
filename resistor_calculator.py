from __future__ import division

from collections import namedtuple
from itertools import product
import time
from math import sqrt

Combination = namedtuple("Combination", ["score", "b1", "b2", "bc"])
VCCl = 2.1
VCCu = 3.75
ADCu = 1.8


def get_combination_score(b1, b2, bc, ideal1, ideal2):
    return pair_score(
        resistor_score(b1, bc, ideal1),
        resistor_score(bc, b2, ideal2)
    )


def resistor_score(r1, r2, ideal):
    pair_value = paralel_resistor_value(r1, r2)

    try:
        score = 1/abs(ideal - pair_value)
    except ZeroDivisionError:
        score = float("Inf")

    return score


def pair_score(score1, score2):
    try:
        return 1/(1/score1 + 1/score2)
    except ZeroDivisionError:
        return 0


def paralel_resistor_value(r1, r2):
    try:
        return r1*r2/(r1+r2)
    except ZeroDivisionError:
        return float("inf")


def ideal_burden(max_current, number_of_turns, safety_factor=1.0):
    return number_of_turns * VCCl * ADCu / (max_current * sqrt(2) * safety_factor * (VCCl + VCCu))


def calculate_beta(r1, r2, number_of_turns):
    return number_of_turns / paralel_resistor_value(r1, r2)


if __name__ == "__main__":
    resistors = [1, 1.2, 1.5, 1.8, 2, 2.4, 3, 3.3, 3.6, 3.9, 4.3, 4.7, 5.1, 5.6, 6.2, 6.8, 7.5, 8.2, 9.1, 10, 12, 15, 18, 20, 24, 27, 30, 33, 36, 39, 43, 47, 51, 56, 62, 68, 75, 82, 91, 100, 120, 150, 180, 200, 220, 240, 270, 300, 330, 360, 390, 430, 470, 510, 560, 620, 680, 750, 820, 910, 1000, 1500, 1800, 2000, 2200, 2400, 2700, 3000, 3300, 3600, 3900, 4300, 4700, 5100, 5600, 6200, 6800, 7200, 7500, 8200, 9100, 10000, 12000, 15000, 18000, 20000, 22000, 24000, 27000, 30000, 33000, 36000, 39000, 43000, 47000, 51000, 56000, 62000, 68000, 75000, 82000, 91000, 100000, 120000, 150000, 180000, 200000, 220000, 240000, 270000, 300000, 330000, 360000, 390000, 430000, 450000, 510000, 560000, 620000, 680000, 750000, 820000, 910000, 1000000, 1500000, 2000000, 3000000, float("inf")]

    max_rated_input_current = 100
    max_rated_output_current = 0.05
    max_practical_input_current_1 = 30
    max_practical_input_current_2 = 50
    safety_factor = 1.5

    # max_rated_input_current = float(input("Please type the maximum rated input current in A: "))
    # max_rated_output_current = float(input("Please type the maximum rated output current in mA: "))/1000
    # max_practical_input_current_1 = float(input("Please type the maximum current to be sensed 1 in A: "))
    # max_practical_input_current_2 = float(input("Please type the maximum current to be sensed 1 in A: "))
    # safety_factor = float(input("Please type the value of the safety factor: "))

    print("")

    number_of_turns = max_rated_input_current / max_rated_output_current
    
    combinations_to_save = 50
    good_combinations = []

    highest_score = float("Inf")
    lower_score = 0

    ideal_burden_1 = ideal_burden(max_practical_input_current_1, number_of_turns, safety_factor)
    ideal_burden_2 = ideal_burden(max_practical_input_current_2, number_of_turns, safety_factor)

    print("Ideal burdens -> r1: {:6.3f}  r2: {:6.3f}".format(ideal_burden_1, ideal_burden_2))

    start = time.time()
    for b1, b2, bc in product(resistors, resistors, resistors):
        score = get_combination_score(b1, b2, bc, ideal_burden_1, ideal_burden_2)

        if score < lower_score:
            continue

        good_combinations.append(Combination(
            score=score,
            b1=b1,
            b2=b2,
            bc=bc
        ))
        good_combinations = sorted(good_combinations, key=lambda item: item.score, reverse=True)

        if len(good_combinations) > combinations_to_save:
            good_combinations.pop()

        lower_score = good_combinations[-1].score

    best = good_combinations[0]
    print("Your best option is:")
    print("    b1: {}".format(best.b1))
    print("    b2: {}".format(best.b2))
    print("    bc: {}".format(best.bc))

    print("Your calculated betas are:")
    print("    beta 1: {}".format(calculate_beta(best.b1, best.bc, number_of_turns)))
    print("    beta 2: {}".format(calculate_beta(best.b2, best.bc, number_of_turns)))

    print("\n--- Full report: ---")

    for item in good_combinations:
        print("Score: {:6.3f}, b1: {:7g}, b2: {:7g}, b3: {:7g}, r1: {:.3f}, ({:5.2f}), r2: {:.3f} ({:5.2f}), beta1: {:.5f}, beta2: {:.5f}".format(
            item.score,
            item.b1,
            item.b2,
            item.bc,
            paralel_resistor_value(item.b1, item.bc),
            ideal_burden_1 - paralel_resistor_value(item.b1, item.bc),
            paralel_resistor_value(item.b2, item.bc),
            ideal_burden_2 - paralel_resistor_value(item.b2, item.bc),
            calculate_beta(item.b1, item.bc, number_of_turns),
            calculate_beta(item.bc, item.b2, number_of_turns)
        ))

        # print(item)

    elapsed = time.time() - start
