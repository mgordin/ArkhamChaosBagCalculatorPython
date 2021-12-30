import sqlite3
from sqlite3 import Error
import time
from itertools import product, islice
import json

# Dumb config
autofail_value = -999
skull_value = 0
tablet_value = -3
cultist_value = -2
squiggle_value = -4

db_file = 'testdb.db'

variable_tokens = ['Skull', 'Cultist', 'Tablet', 'Squiggle']

# Stuff


def calculationStep(remainingOptions, previousTotal, probMod, pastFrost, first):
    for i, token in enumerate(remainingOptions, start=0):
        if probMod > 0.0001:
            print(probMod, i, token)
        total = previousTotal + token[0]
        # Cut it off after three-ish redraws
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
        else:
            allResults.append([total, probMod])


def aggregate(results):
    prob = {}
    print("Aggregation - loop")
    for i in list(range(21, -25, -1)) + [-999]:
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


""" allResults = []

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
    [[squiggle_value, False, 'Squiggle']]*2 + \
    [[-1, True, 'Frost']]*3 + \
    [[autofail_value, False, 'Autofail']]

start_time = time.time()
calculationStep(options, 0, 1/len(options), False, True)
cumulative = aggregate(allResults)
print("This took {} s".format(time.time() - start_time)) """

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

# Connect to database
conn = None
try:
    conn = sqlite3.connect(db_file)
    print(sqlite3.version)
except Error as e:
    print(e)

# Create table if needed
create_table_sql = """ CREATE TABLE IF NOT EXISTS probabilities (
    p1_count integer NOT NULL,
    n0_count integer NOT NULL,
    m1_count integer NOT NULL,
    m2_count integer NOT NULL,
    m3_count integer NOT NULL,
    m4_count integer NOT NULL,
    skull_count integer NOT NULL,
    skull_value integer NOT NULL,
    skull_redraw boolean NOT NULL,
    cultist_count integer NOT NULL,
    cultist_value integer NOT NULL,
    cultist_redraw boolean NOT NULL,
    tablet_count integer NOT NULL,
    tablet_value integer NOT NULL,
    tablet_redraw boolean NOT NULL,
    squiggle_count integer NOT NULL,
    squiggle_value integer NOT NULL,
    squiggle_redraw boolean NOT NULL,
    bless_count integer NOT NULL,
    curse_count integer NOT NULL,
    frost_count integer NOT NULL,
    star_count integer NOT NULL,
    autofail_count integer NOT NULL,
    token_probabilities text NOT NULL
); """
try:
    cursor = conn.cursor()
    cursor.execute(create_table_sql)
except Error as e:
    print(e)

# Saving SQL
save_sql = '''INSERT INTO probabilities(p1_count,n0_count,m1_count,m2_count,m3_count,m4_count,skull_count,cultist_count,tablet_count,squiggle_count,bless_count,curse_count,frost_count,star_count,autofail_count,skull_value,cultist_value,tablet_value,squiggle_value,skull_redraw,cultist_redraw,tablet_redraw,squiggle_redraw,token_probabilities)
              VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) 
'''

# Loop through the iterator
c = 0
for permutation in token_options_fully_expanded:
    if c > 0:
        break
    # Build the bag in the right format for this permutation
    bag = []
    print(permutation)
    for token_config in permutation:
        if token_config[0] != 0:
            bag += [[token_config[1], token_config[2],
                     token_config[3]]]*token_config[0]

    # Calculate probabilities for that bag
    allResults = []
    calculationStep(bag, 0, 1/len(bag), False, True)
    cumulative = aggregate(allResults)

    # Save
    save_values = [x[0] for x in permutation] + \
        [x[1] for x in permutation if x[3] in variable_tokens] + \
        [x[2] for x in permutation if x[3]
            in variable_tokens] + [json.dumps(cumulative)]
    cursor.execute(save_sql, save_values)
    conn.commit()
    c += 1

# Close db connection
conn.close()

# ---
# Number of permutations


def nPermutations(token_options):
    count = 1
    for k, v in token_options.items():
        count = count * len(v[0]) * len(v[1]) * len(v[2])
    return count


nPermutations(token_options)

# Iterate through and save
