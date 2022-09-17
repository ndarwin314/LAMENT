import numpy as np
import bisect

def bin_search(value, array):
    return bisect.bisect_left(array, value)

def cumulative(array, index):
    if index >= array.size:
        return 100
    return f"{round(100*array.cumsum()[index],2)}"

def weapon(wishes=0, guarantee=True, pity=0):
    base = np.zeros((81,))
    p = 0.007
    ramp = 0.06 #temporary
    base[0] = 0
    base[1:63] = p
    base[80] = 1
    for i in range(63, 80):
        base[i] = min(1, p + ramp * (i-62))
    ones = np.ones((81,))
    oneMinus = ones - base
    basePDF = np.zeros((81,))
    for i in range(81):
        basePDF[i] = np.prod(oneMinus[0:i]) * base[i]
    doublePDF = np.convolve(basePDF, basePDF)
    triplePDF = np.convolve(doublePDF, basePDF)
    fullPDF = 23 / 64 * triplePDF
    fullPDF[0:81] += 3/8*basePDF
    fullPDF[0:161] += 17/64*doublePDF
    pityPDF = np.zeros((81-pity,))
    pityPDF[0] = 0
    initialPDF = np.zeros((241-pity,))
    for i in range(1, 81 - pity):
        # would be more efficient to keep track of product O(n^2)->O(n)
        pityPDF[i] = np.prod(oneMinus[pity + 1:i + pity]) * base[i + pity]
    if guarantee:
        initialPDF[0:81-pity] += 1 / 2 * pityPDF
        temp = np.convolve(pityPDF, basePDF)
        initialPDF[0:161 - pity] += 3 / 16 * temp
        temp = np.convolve(temp, basePDF)
        initialPDF += 5 / 16 * temp
    else:
        initialPDF[0:81-pity] += 3 / 8 * pityPDF
        temp = np.convolve(pityPDF, basePDF)
        initialPDF[0:161-pity] += 17 / 64 * temp
        temp = np.convolve(temp, basePDF)
        initialPDF += 23 / 64 * temp
    probabilities = [cumulative(initialPDF, wishes)]
    print(probabilities)
    fullPDF = initialPDF
    for i in range(4):
        fullPDF = np.convolve(fullPDF, triplePDF)
        probabilities.append(cumulative(fullPDF, wishes))
    return probabilities

def character(wishes=0, guarantee=False, pity=0):
    rampRate = 0.06
    P = 0.006
    cons = 6
    probabilities = []
    base = np.zeros((91,))
    base[0] = 0
    base[1:74] = P
    base[90] = 1
    for i in range(74, 90):
        base[i] = P + rampRate * (i - 73)
    ones = np.ones((91,))
    temp = ones - base
    basePDF = np.zeros((91,))
    for i in range(91):
        basePDF[i] = np.prod(temp[0:i]) * base[i]
    doublePDF = np.zeros((181,))
    doublePDF[0:91] += basePDF
    for i in range(1, 90):
        doublePDF[i:i + 91] += basePDF[i] * basePDF
    doublePDF /= 2
    pityPDF = np.zeros((91 - pity,))
    fullPDF = np.zeros((181 - pity - 90 * guarantee,))
    pityPDF[0] = 0
    for i in range(1, 91 - pity):
        pityPDF[i] = np.prod(temp[pity + 1:i + pity]) * base[i + pity]
    fullPDF[0:91 - pity] = pityPDF
    if not guarantee:
        for i in range(1, 90 - pity):
            fullPDF[i:i + 91] += pityPDF[i] * basePDF
        fullPDF /= 2
    probabilities.append(cumulative(fullPDF, wishes))
    # fullPDF = basePDF if guarantee else doublePDF
    for i in range(cons):
        fullPDF = np.convolve(fullPDF, doublePDF)
        probabilities.append(cumulative(fullPDF, wishes))
    return probabilities