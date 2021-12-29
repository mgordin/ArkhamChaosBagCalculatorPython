import sqlite3
import time
from itertools import product, islice

# Dumb config
autofail_value = -999
skull_value = -2
tablet_value = -3
cultist_value = -1
squiggle_value = -4

# Stuff


def calculationStep(remainingOptions, previousTotal, probMod, pastFrost, first):
    for i, token in enumerate(remainingOptions, start=0):
        if probMod > 0.0001:
            print(probMod, i, token)
        total = previousTotal + token[0]
        if probMod < 0.000001:
            allResults.append([autofail_value, probMod])
        elif token[1]:
            if not (pastFrost and token[2] == 'Frost'):
                calculationStep(
                    remainingOptions[0:i] + remainingOptions[i+1:-1], total, probMod / (len(remainingOptions)-1), token[2] == 'Frost', False)
            else:
                allResults.append([autofail_value, probMod])
        elif token[0] == autofail_value:
            allResults.append([autofail_value, probMod])
        # Let's try cutting it off after two redraws
        else:
            allResults.append([total, probMod])


def aggregate(results):
    prob = {}
    print("Aggregation - loop")
    for i in range(100, -1010, -1):
        if i % 10 == 0:
            print(i)
        prob[i] = sum([p for v, p in results if v == i])*100

    print(sum(prob.values()))

    print("Aggregation - sum")
    probCumul = {-2: sumStuffUp(prob, 1),
                 -1: sumStuffUp(prob, 0),
                 0: sumStuffUp(prob, -1),
                 1: sumStuffUp(prob, -2),
                 2: sumStuffUp(prob, -3),
                 3: sumStuffUp(prob, -4),
                 4: sumStuffUp(prob, -5),  # but why?
                 5: sumStuffUp(prob, -6),  # no really, why?
                 6: sumStuffDown(prob, -6)
                 }

    return probCumul


def sumStuffUp(prob, target):
    temp = 0
    for k, v in prob.items():
        if k > target:
            temp += v
            #print(k, type(k), v, type(v))
    return temp


def sumStuffDown(prob, target):
    temp = 0
    for k, v in prob.items():
        if k <= target:
            temp += v
            #print(k, type(k), v, type(v))
    return temp


allResults = []

options = [[1, False, 'Star']] + \
    [[1, False, '+1']] + \
    [[0, False, '0']]*2 + \
    [[-1, False, '-1']]*3 + \
    [[-2, False, '-2']]*2 + \
    [[cultist_value, False, 'Cultist']]*2 + \
    [[-3, False, '-3']] + \
    [[tablet_value, False, 'Tablet']] + \
    [[-4, False, '-4']] + \
    [[skull_value, False, 'Skull']]*2 + \
    [[squiggle_value, False, 'Squiggle']] + \
    [[2, True, 'Bless']]*10 + \
    [[-2, True, 'Curse']]*4 + \
    [[-1, True, 'Frost']]*8 + \
    [[autofail_value, False, 'Autofail']]

start_time = time.time()
calculationStep(options, 0, 1/len(options), False, True)
cumulative = aggregate(allResults)
print("This took {} s".format(time.time() - start_time))

# counts, values, redraw
token_options = {
    '+1': [[1], [1], [False]],
    '0': [[2], [0], [False]],
    '-1': [[3], [-1], [False]],
    '-2': [[2], [-2], [False]],
    '-3': [[1], [-3], [False]],
    '-4': [[1], [-4], [False]],
    'Skull': [[2], list(range(0, -6, -1)), [False]],
    'Cultist': [[1, 2], list(range(-2, -4, -1)), [False]],
    'Tablet': [[1, 2], list(range(-3, -6, -1)), [False]],
    'Squiggle': [[0, 1, 2], list(range(-3, -6, -1)), [False]],
    'Bless': [list(range(11)), [2], [True]],
    'Curse': [list(range(5)), [-2], [True]],
    'Frost': [list(range(9)), [-1], [True]],
    'Star': [[1], [1], [False]],
    'Autofail': [[1], [autofail_value], [False]]
}

# Expand each token's options
token_options_expanded = {}
for k, v in token_options.items():
    token_options_expanded[k] = list(
        product(token_options[k][0], token_options[k][1], token_options[k][2], [k]))

# Single iterator of all permutations of options across all tokens
token_options_fully_expanded = product(*token_options_expanded.values())

# Loop through the iterator
for permutation in token_options_fully_expanded:
    # Build the bag in the right format for this permutation
    bag = []
    for token_config in permutation[0]:
        if token_config[0] != 0:
            bag += [[token_config[1], token_config[2],
                     token_config[3]]]*token_config[0]

    # Calculate probabilities for that bag
    allResults = []
    calculationStep(bag, 0, 1/len(bag), False, True)
    cumulative = aggregate(allResults)

    # Save ???  Halp


# ---
# Number of permutations
def nPermutations(token_options):
    count = 1
    for k, v in token_options.items():
        count = count * len(v[0]) * len(v[1]) * len(v[2])
    return count


nPermutations(token_options)

# Iterate through and save
