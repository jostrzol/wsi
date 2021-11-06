# by Jakub Ostrzołek

from typing import List
from genetic import Generation, genetic_algorithm
from main import f_encoded, generate_population, point_encode
from pytest import mark

REPEAT = 25

FITNESS_FNC = f_encoded

# in format [<size>, <iterations>, <mutation_prob>, <crossover_prob>]
STD_PARAMS = [20, 500, 0.05, 0.1]

# for each size * iterations = 10000
SIZES_ITERATIONS = [
    (5, 2000),
    (10, 1000),
    (15, 667),
    # (20, 500),    already in STD_PARAMS
    (40, 250),
    (80, 125),
    (125, 80),
]
MUTATION_PROBS = [
    0.001,
    0.01,
    0.025,
    # 0.05,         already in STD_PARAMS
    0.1,
    0.25,
]
CROSSOVER_PROBS = [
    0,
    0.01,
    0.05,
    # 0.1,          already in STD_PARAMS
    0.25,
    0.5,
    0.75
]

SEPARATE_PARAMS = [[15, 667, 0.1, 0.05]]

ALL_PARAMS = [STD_PARAMS] + \
    [[s, i] + STD_PARAMS[2:] for s, i in SIZES_ITERATIONS] + \
    [STD_PARAMS[:2] + [mp] + STD_PARAMS[3:] for mp in MUTATION_PROBS] + \
    [STD_PARAMS[:3] + [cp] for cp in CROSSOVER_PROBS] + \
    SEPARATE_PARAMS


@mark.repeat(REPEAT)
@mark.parametrize("size,iterations,mutation_prob,crossover_prob",
                  ALL_PARAMS)
def test_benchmark(size, iterations, mutation_prob,
                   crossover_prob, benchmark):
    population = [point_encode(solution)
                  for solution in generate_population(size)]

    generations: List[Generation] = benchmark.pedantic(
        target=genetic_algorithm,
        args=[FITNESS_FNC,
              population,
              mutation_prob,
              crossover_prob,
              iterations],
        kwargs={"return_generations": True})

    benchmark.extra_info["generations"] = [
        g.fitness for g in generations]
    benchmark.extra_info["result"] = generations[-1].best_fitness
