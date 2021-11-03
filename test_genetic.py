import genetic
from genetic import (crossover_two_point, mutate,
                     mutate_gene, reproduct_tournment)


def test_crossover_two_points(monkeypatch):
    population = [
        (1, 2, 3, 4, 5, 6),
        ("a", "b", "c", "d", "e", "f"),
    ]
    monkeypatch.setattr(genetic, "random", lambda: 0.2)
    monkeypatch.setattr(genetic, "sample", lambda *a: (2, 4))
    result = crossover_two_point(population, 0.3)
    assert len(result) == len(population)
    assert result[0] == (1, 2, "c", "d", 5, 6)
    assert result[1] == ("a", "b", 3, 4, "e", "f")


def test_mutate_gene(monkeypatch):
    assert mutate_gene(True, 0) is True
    assert mutate_gene(True, 1) is False
    randoms = [0.1, 0.2, 0.3, 0.2, 0.9, 0.4]
    i = iter(randoms)
    monkeypatch.setattr(genetic, "random", lambda: next(i))
    assert mutate_gene(True, 0.25) is False
    assert mutate_gene(True, 0.25) is False
    assert mutate_gene(True, 0.25) is True
    assert mutate_gene(True, 0.25) is False
    assert mutate_gene(True, 0.25) is True
    assert mutate_gene(True, 0.25) is True


def test_mutate(monkeypatch):
    population = [
        (True,) * 6
    ]
    randoms = [0.1, 0.2, 0.3, 0.2, 0.9, 0.4]
    i = iter(randoms)
    monkeypatch.setattr(genetic, "random", lambda: next(i))
    result = mutate(population, 0.25)
    assert len(result) == len(population)
    assert result[0] == (False, False, True, False, True, True)


def test_reproduct_tournment(monkeypatch):
    population = [0, 1, 2, 3, 4, 5]
    fitness = [4, 2, 1, 7, 7, 8]

    random_indexes = [
        0, 1,   # wins 1
        4, 5,   # wins 4
        3, 4,   # wins 3
        1, 5,   # wins 1
        4, 2,   # wins 2
        2, 2,   # wins 2
    ]
    i = iter(random_indexes)
    monkeypatch.setattr(genetic, "choice", lambda pop: pop[next(i)])

    result = reproduct_tournment(population, fitness)

    assert len(result) == len(population)
    assert result[0] == 1
    assert result[1] == 4
    assert result[2] == 3
    assert result[3] == 1
    assert result[4] == 2
    assert result[5] == 2
