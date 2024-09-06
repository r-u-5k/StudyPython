def dijkstra(dist):
    shortest_distances = [100, 100, 100, 100, 100, 100]
    shortest_distances[0] = 0

    visited = [False, False, False, False, False, False]

    for _ in range(6):
        min_distance = 100
        min_index = -1
        for i in range(6):
            if not visited[i] and shortest_distances[i] < min_distance:
                min_distance = shortest_distances[i]
                min_index = i

        visited[min_index] = True

        for j in range(6):
            if dist[min_index][j] != 100 and not visited[j]:
                new_distance = shortest_distances[min_index] + dist[min_index][j]
                if new_distance < shortest_distances[j]:
                    shortest_distances[j] = new_distance

    return shortest_distances


dist = [
    [0, 2, 5, 1, 100, 100],
    [2, 0, 3, 2, 100, 100],
    [5, 3, 0, 3, 1, 5],
    [1, 2, 3, 0, 1, 100],
    [100, 100, 1, 1, 0, 2],
    [100, 100, 5, 100, 2, 0]
]

shortest_distances = dijkstra(dist)

print(f"각 노드까지의 최단 거리: {shortest_distances}")
