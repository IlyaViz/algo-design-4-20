import numpy as np
import time
import random
from networkx import Graph
from constants import (
    CITY_COUNT,
    PHEROMONE,
    DISTANCE,
    ALPHA,
    BETA,
    P,
    M_COUNT,
    E_COUNT,
    INIT_PHEROMONE,
    CYCLE_COUNT
)


class TSP:
    def __init__(self, graph: Graph) -> None:
        self._graph = graph
        self.cycles_log = []

    def solve(self):
        best_distance = float('inf')
        best_path = []

        self._apply_init_pheromone()

        for iteration in range(CYCLE_COUNT):
            print(f"{iteration/CYCLE_COUNT*100}%")

            self._cycle()

            best_ants = self._get_best_ants(E_COUNT)

            for best_ant in best_ants:
                self._apply_elite_ant(best_ant)

            best_ant = best_ants[0]

            if self._ant_current_distances[best_ant] < best_distance:
                best_distance = self._ant_current_distances[best_ant]
                best_path = self._ant_visited_vertices[best_ant]

            self.cycles_log.append((iteration, best_distance))

        return best_distance, best_path 
    
    def _cycle(self):
        self._reset_ant_variables()

        for iteration in range(CITY_COUNT):
            for ant in self._ants:
                current_vertex = self._ant_positions[ant]

                if iteration == CITY_COUNT - 1:
                    next_vertex = self._get_next_vertex(ant, self._ant_positions[ant], True)
                else:
                    next_vertex = self._get_next_vertex(ant, self._ant_positions[ant], False)

                self._ant_current_distances[ant] += self._graph[current_vertex][next_vertex][DISTANCE]
                self._ant_positions[ant] = next_vertex
                self._ant_visited_vertices[ant].append(next_vertex)
                
                self._graph[current_vertex][next_vertex][PHEROMONE] += self._l_min / self._ant_current_distances[ant]

            self._evaporate()

    def _get_best_ants(self, count: int) -> list[int]:
        ant_distances = list(self._ant_current_distances.items())
        
        best_ant_distances = sorted(ant_distances, key = lambda ant_distance: ant_distance[1])[:count]

        return [best_ant_distance[0] for best_ant_distance in best_ant_distances]
    
    def _apply_elite_ant(self, ant: int):
        path = self._ant_visited_vertices[ant]
        current_distance = 0

        for index in range(len(path)-1):
            current_distance += self._graph[path[index]][path[index+1]][DISTANCE]

            self._graph[path[index]][path[index+1]][PHEROMONE] += self._l_min / current_distance

    def _apply_init_pheromone(self) -> None:
        for first, second, data in self._graph.edges(data=True):
            data[PHEROMONE] = INIT_PHEROMONE

    def _apply_extra_pheromone(self) -> None:
        for first, second, data in self._graph.edges(data=True):
            data[PHEROMONE] += INIT_PHEROMONE

    def _evaporate(self) -> None:
        for first, second, data in self._graph.edges(data=True):
            data[PHEROMONE] *= (1-P)

    def _reset_ant_variables(self) -> None:
        self._ants = [ant for ant in range(M_COUNT)]

        vertices = list(self._graph.nodes)
        shuffled_vertices = random.sample(vertices, len(vertices))
        self._ant_positions = {ant: shuffled_vertices[index] for index, ant in enumerate(self._ants)}

        self._ant_visited_vertices = {ant: [self._ant_positions[ant]] for ant in self._ants}
        self._ant_current_distances = {ant: 0 for ant in self._ants}

        self._l_min = self._get_greedy_value()

    def _get_next_vertex(self, ant: int, current_vertex: str, allow_start_vertex: bool) -> str:
        allowed_neighbours = []

        for neighbour in self._graph[current_vertex]:
            if neighbour not in self._ant_visited_vertices[ant] or allow_start_vertex and neighbour == self._ant_visited_vertices[ant][0]:
                allowed_neighbours.append(neighbour)
    
        probabilities = [self._get_edge_chance(current_vertex, neighbour, allowed_neighbours) for neighbour in allowed_neighbours]
        
        return np.random.choice(allowed_neighbours, p=probabilities)

    def _get_edge_chance(self, current_vertex: str, next_vertex: str, allowed_neighbours: list[str]) -> float:
        numerator = self._get_edge_value(self._graph[current_vertex][next_vertex])
        denominator = 0

        for neighbour in allowed_neighbours:
            denominator += self._get_edge_value(self._graph[current_vertex][neighbour])

        if denominator == 0:
            self._apply_extra_pheromone()
            
            return self._get_edge_chance(current_vertex, next_vertex, allowed_neighbours)

        return numerator / denominator
    
    def _get_edge_value(self, edge: dict) -> float:
        pheromone = edge[PHEROMONE]
        distance = edge[DISTANCE]
        
        return pheromone**ALPHA*(1/distance)**BETA
    
    def _get_greedy_value(self) -> int:
        total_distance = 0
        vertices = list(self._graph.nodes)
        current_vertex = vertices[0]
        visited = [current_vertex]

        for _ in range(CITY_COUNT):
            next_vertex = None
            min_distance = float('inf')

            for neighbor in self._graph[current_vertex]:
                if neighbor not in visited:
                    distance = self._graph[current_vertex][neighbor][DISTANCE]

                    if distance < min_distance:
                        min_distance = distance
                        next_vertex = neighbor

            if next_vertex is None:
                break

            total_distance += min_distance
            current_vertex = next_vertex

            visited.append(current_vertex)

        total_distance += self._graph[current_vertex][vertices[0]][DISTANCE]

        return total_distance
