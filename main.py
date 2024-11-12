from colorama import Fore, Style
from generator import generate_country_graph
from algorithm import TSP
from constants import (
    CITY_COUNT,
    MIN_DISTANCE,
    MAX_DISTANCE,
    DISTANCE
)


if __name__ == "__main__":
    graph = generate_country_graph(CITY_COUNT, MIN_DISTANCE, MAX_DISTANCE)
    task = TSP(graph)
    result = task.solve()

    path = result[1]
    distance = result[0]

    for edge in graph.edges(data=True):
        print(f"{edge[0]} to {edge[1]} ({edge[2][DISTANCE]})")
                
    print(Fore.GREEN, f"{path[0]} (Start)")

    for index in range(len(path)-1):
        print(Fore.GREEN, f"{path[index]} to {path[index+1]} ({graph[path[index]][path[index+1]][DISTANCE]})")

    print(distance)

    print(Style.RESET_ALL)