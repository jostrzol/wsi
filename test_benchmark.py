# by Jakub Ostrzołek

from typing import List
from genetic import Generation, genetic_algorithm
from main import f_encoded, generate_population, point_encode
from pytest import mark

REPEAT = 25

FITNESS_FNC = f_encoded

SIZES = [5, 10, 20, 40, 80]
ITERATIONS = [50, 100, 250, 500, 1000]
MUTATION_PROBS = [0.001, 0.01, 0.025, 0.05, 0.1, 0.25]
CROSSOVER_PROBS = [0, 0.01, 0.05, 0.1, 0.25, 0.5, 0.75]

# in format [<size>, <iterations>, <mutation_prob>, <crossover_prob>]
STD_PARAMS = [20, 500, 0.05, 0.1]

SEPARATE_PARAMS = [[40, 500, 0.03, 0.5]]

ALL_PARAMS = [[s] + STD_PARAMS[1:] for s in SIZES] + \
    [STD_PARAMS[:1] + [i] + STD_PARAMS[2:] for i in ITERATIONS] + \
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
