import copy

dist = [
    [0, 2, 5, 1, 100, 100],
    [2, 0, 3, 2, 100, 100],
    [5, 3, 0, 3, 1, 5],
    [1, 2, 3, 0, 100, 100],
    [100, 100, 5, 1, 0, 2],
    [100, 100, 5, 100, 2, 0]
]

newDist = copy.deepcopy(dist)

check = [0, 1, 2, 3, 4, 5, 6]

i = 3
tempDist = newDist[0][i]
nextDist = newDist[i]
for j in range(0, 6):
    if newDist[0][j] > tempDist + nextDist[j]:
        newDist[0][j] = tempDist + nextDist[j]