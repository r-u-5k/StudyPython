def find_nearest_city(current_city, unvisited, graph):
    nearest_city = None
    min_distance = float('inf')
    for city in unvisited:
        distance = graph[current_city][city]
        if distance < min_distance:
            min_distance = distance
            nearest_city = city
    return nearest_city


def tsp(graph):
    unvisited = list(graph.keys())
    path = ['A']
    current_city = 'A'

    while len(unvisited) > 1:  # 'A'는 이미 방문했으므로 1개 남을 때까지
        unvisited.remove(current_city)
        next_city = find_nearest_city(current_city, unvisited, graph)
        path.append(next_city)
        current_city = next_city

    path.append('A')
    return path


graph = {
    'A': {'B': 12, 'C': 10, 'D': 19, 'E': 8},
    'B': {'A': 12, 'C': 3, 'D': 7, 'E': 2},
    'C': {'A': 10, 'B': 3, 'D': 6, 'E': 20},
    'D': {'A': 19, 'B': 7, 'C': 6, 'E': 4},
    'E': {'A': 8, 'B': 2, 'C': 20, 'D': 4},
}

shortest_path = tsp(graph)

print(f"최단 경로: {' -> '.join(shortest_path)}")
