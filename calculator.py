# Dumb config
autofail_value = -999

# Stuff
allResults = []


def calculationStep(remainingOptions, previousTotal, probMod, pastFrost):
    for i, token in enumerate(remainingOptions, start=0):
        total = previousTotal + token[0]
        if token[1]:
            if not (pastFrost and token[2] == 'Frost'):
                calculationStep(
                    remainingOptions[0:i] + remainingOptions[i+1:-1], total, probMod / (len(remainingOptions)-1), token[2] == 'Frost')
            else:
                allResults.append([autofail_value, probMod])
        elif token[0] == autofail_value:
            allResults.append([autofail_value, probMod])
        else:
            allResults.append([total, probMod])


def aggregate(results):
    prob = {}
    for i in range(100, -1010, -1):
        prob[i] = sum([p for v, p in results if v == i])*100

    print(sum(prob.values()))

    probBounded = {-2: sum({v for k, v in prob.items() if k > 1}),
                   -1: prob[1],
                   0: prob[0],
                   1: prob[-1],
                   2: prob[-2],
                   3: prob[-3],
                   4: prob[-4],
                   5: prob[-5],
                   6: sum({v for k, v in prob.items() if k < -5})}

    probCumul = {-2: probBounded[-2],
                 -1: sum({v for k, v in probBounded.items() if k < 0}),
                 0: sum({v for k, v in probBounded.items() if k < 1}),
                 1: sum({v for k, v in probBounded.items() if k < 2}),
                 2: sum({v for k, v in probBounded.items() if k < 3}),
                 3: sum({v for k, v in probBounded.items() if k < 4}),
                 4: sum({v for k, v in probBounded.items() if k < 5}),
                 5: sum({v for k, v in probBounded.items() if k < 6})
                 }

    return probCumul


options = [[1, False, 'Star']] + \
    [[1, False, '+1']] + \
    [[0, False, '0']]*2 + \
    [[-1, False, '-1']]*2 + \
    [[-2, False, '-2']]*2 + \
    [[-2, False, 'Cultist']]*2 + \
    [[-3, False, '-3']] + \
    [[-3, False, 'Skull']]*2 + \
    [[-3, False, 'Tablet']] + \
    [[-4, False, '-4']] + \
    [[-4, False, 'Squiggle']] + \
    [[2, True, 'Bless']] * 2 + \
    [[autofail_value, False, 'Autofail']]


calculationStep(options, 0, 1/len(options), False)
aggregate(allResults)
