dist = [
    [0, 100, 100, 100, 100, 100, 100],
    [100, 0, 2, 5, 1, 100, 100],
    [100, 2, 0, 3, 2, 100, 100],
    [100, 5, 3, 0, 3, 1, 5],
    [100, 1, 2, 3, 0, 1, 100],
    [100, 100, 100, 1, 1, 0, 2],
    [100, 100, 100, 5, 100, 2, 0]
]


def dijkstra(dist, start):
    shortest_distances = [100] * 7
    shortest_distances[start] = 0

    visited = [False] * 7

    for _ in range(7):
        min_distance = 100
        min_index = -1
        for i in range(7):
            if not visited[i] and shortest_distances[i] < min_distance:
                min_distance = shortest_distances[i]
                min_index = i

        visited[min_index] = True

        for j in range(7):
            if dist[min_index][j] != 100 and not visited[j]:
                new_distance = shortest_distances[min_index] + dist[min_index][j]
                if new_distance < shortest_distances[j]:
                    shortest_distances[j] = new_distance

    return shortest_distances


for start_node in range(1, 7):
    shortest_distances = dijkstra(dist, start_node)
    print(f"노드 {start_node}에서 각 노드까지의 최단 거리: {shortest_distances[1:]}")
