import pandas as pd
from itertools import permutations

distances = pd.DataFrame({
    'A': [0, 12, 10, 19, 8],
    'B': [12, 0, 3, 7, 2],
    'C': [10, 3, 0, 6, 20],
    'D': [19, 7, 6, 0, 4],
    'E': [8, 2, 20, 4, 0]
}, index=['A', 'B', 'C', 'D', 'E'])

all_routes = [['A'] + list(p) + ['A'] for p in permutations(['B', 'C', 'D', 'E'])]


def calculate_total_distance(route):
    total_distance = 0
    for i in range(len(route) - 1):
        start_city = route[i]
        end_city = route[i + 1]
        distance = distances.loc[start_city, end_city]
        total_distance += distance
    return total_distance


shortest_route = min(all_routes, key=calculate_total_distance)
shortest_distance = calculate_total_distance(shortest_route)

print(f"최단 경로: {' -> '.join(shortest_route)}")
print(f"최단 거리: {shortest_distance}")
