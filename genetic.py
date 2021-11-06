# by Jakub Ostrzołek

from typing import Callable, List, Tuple, Union
from random import random, sample
from dataclasses import dataclass
import numpy as np

Solution = Tuple[bool, ...]
RatedSolution = Tuple[float, Solution]


@dataclass
class Generation:
    population: List[Solution]
    fitness: List[float]
    best: Solution
    best_fitness: float


def reproduct(
        population: List[Solution],
        fitness: List[float]):

    fitness_reverse = [1/f for f in fitness]
    fitness_reverse_sum = sum(fitness_reverse)
    probabilities = np.array([f/fitness_reverse_sum for f in fitness_reverse])

    # cannot use directly population, because numpy expects a 1-D list
    indices = np.random.choice(
        list(range(len(population))), size=len(population), p=probabilities)

    return [population[i] for i in indices]


def mutate_gene(gene: bool, mutation_prob: float):
    if random() < mutation_prob:
        return not gene
    else:
        return gene


def mutate(
        population: List[Solution],
        mutation_prob: float):
    result = [None] * len(population)
    for i, solution in enumerate(population):
        result[i] = tuple(mutate_gene(gene, mutation_prob)
                          for gene in solution)
    return result


def crossover_two_point(
        population: List[Solution],
        crossover_prob: float):
    init_len = len(population)

    if len(population) % 2 != 0:
        population = population + [population[-1]]

    population = np.array(population)
    pairs_shape = (population.shape[0]//2, 2, population.shape[1])
    pairs = np.array(population).reshape(pairs_shape)

    result = [None] * pairs.size

    for i, (solution1, solution2) in enumerate(pairs):
        solution1 = tuple(solution1)
        solution2 = tuple(solution2)

        if random() < crossover_prob:
            j, k = sorted(sample(range(len(solution1) + 1), 2))
            child1 = solution1[:j] + solution2[j:k] + solution1[k:]
            child2 = solution2[:j] + solution1[j:k] + solution2[k:]
        else:
            child1 = solution1
            child2 = solution2
        result[2*i] = child1
        result[2*i + 1] = child2

    return result[:init_len]


def genetic_algorithm(
        fitness_fnc: Callable[[Solution], float],
        population: List[Solution],
        mutation_prob: float,
        crossover_prob: float,
        iterations: int,
        seek_max: bool = False,
        return_generations: bool = False
) -> Union[RatedSolution, List[Generation]]:

    generations: List[Generation] = []
    optimum = min
    if seek_max:
        optimum = max

    fitness = [fitness_fnc(solution) for solution in population]
    best = optimum(zip(fitness, population))

    for _ in range(iterations):
        generations.append(Generation(population, fitness, best[1], best[0]))

        population = reproduct(population, fitness)
        population = mutate(population, mutation_prob)
        population = crossover_two_point(population, crossover_prob)

        fitness = [fitness_fnc(solution) for solution in population]
        best_candidate = optimum(zip(fitness, population))
        best = optimum(best, best_candidate)

    if return_generations:
        return generations
    else:
        return best
