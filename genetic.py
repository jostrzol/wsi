# by Jakub Ostrzołek

from typing import Callable, List, Tuple, Union
from random import choice, random, sample
from dataclasses import dataclass

Solution = Tuple[bool, ...]
RatedSolution = Tuple[float, Solution]


@dataclass
class Generation:
    population: List[Solution]
    fitness: List[float]
    best: Solution
    best_fitness: float


def reproduct_tournment(
        population: List[Solution],
        fitness: List[float],
        optimum: Callable = min):
    result = [None] * len(population)
    graded_solutions = list(zip(fitness, population))

    for i in range(len(population)):
        first = choice(graded_solutions)
        second = choice(graded_solutions)
        result[i] = (optimum(first, second)[1])
    return result


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
    result = list(population)
    for i, (solution1, solution2) in enumerate(zip(result[:-1], result[1:])):
        if random() < crossover_prob:
            j, k = sorted(sample(range(len(solution1) + 1), 2))
            child1 = solution1[:j] + solution2[j:k] + solution1[k:]
            child2 = solution2[:j] + solution1[j:k] + solution2[k:]
            result[i] = child1
            result[i + 1] = child2
    return result


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

        population = reproduct_tournment(population, fitness)
        population = mutate(population, mutation_prob)
        population = crossover_two_point(population, crossover_prob)

        fitness = [fitness_fnc(solution) for solution in population]
        best_candidate = optimum(zip(fitness, population))
        best = optimum(best, best_candidate)

    if return_generations:
        return generations
    else:
        return best
