graph = [
    [0, 4, 0, 0, 0, 0, 0, 8, 0],
    [4, 0, 8, 0, 0, 0, 0, 11, 0],
    [0, 8, 0, 7, 0, 4, 0, 0, 2],
    [0, 0, 7, 0, 9, 14, 0, 0, 0],
    [0, 0, 0, 9, 0, 10, 0, 0, 0],
    [0, 0, 4, 14, 10, 0, 2, 0, 0],
    [0, 0, 0, 0, 0, 2, 0, 1, 6],
    [8, 11, 0, 0, 0, 0, 1, 0, 7],
    [0, 0, 2, 0, 0, 0, 6, 7, 0]
]


def dijkstra(graph):
    start = 0
    end = 4
    n = len(graph)
    distances = [float('inf')] * n
    distances[start] = 0
    visited = [False] * n
    parent = [-1] * n

    for _ in range(n):
        min_distance = float('inf')
        min_index = -1
        for i in range(n):
            if not visited[i] and distances[i] < min_distance:
                min_distance = distances[i]
                min_index = i

        if min_index == -1 or min_index == end:
            break

        visited[min_index] = True

        for j in range(n):
            if graph[min_index][j] != 0 and not visited[j]:
                new_distance = distances[min_index] + graph[min_index][j]
                if new_distance < distances[j]:
                    distances[j] = new_distance
                    parent[j] = min_index

    path = []
    current = end
    while current != -1:
        path.append(current)
        current = parent[current]
    path.reverse()

    return distances[end], path


shortest_distance, shortest_path = dijkstra(graph)

path = ""
for node in shortest_path:
    if path:
        path += " -> "
    path += str(node)

print(f"노드 0에서 노드 4로 가는 최단 경로: {path}")
print(f"노드 0에서 노드 4로 가는 최단 거리: {shortest_distance}")
