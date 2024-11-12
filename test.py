from matplotlib import pyplot as plt
from generator import generate_country_graph
from algorithm import TSP
from constants import (
    CITY_COUNT,
    MIN_DISTANCE,
    MAX_DISTANCE
)


if __name__ == "__main__":
    graph = generate_country_graph(CITY_COUNT, MIN_DISTANCE, MAX_DISTANCE)
    
    tsp = TSP(graph)
    
    result = tsp.solve()

    iterations = [step[0] for step in tsp.cycles_log]
    min_distance = [step[1] for step in tsp.cycles_log]

    plt.plot(iterations, min_distance)

    plt.xlabel("Iterations")
    plt.ylabel("Min distance")

    plt.show()