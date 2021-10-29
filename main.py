# by Jakub Ostrzołek

from argparse import ArgumentParser
from typing import Any, Callable, Dict, List, Tuple
from math import sin
from genetic import genetic_algorithm
from random import randint, seed
import sys


gettrace = getattr(sys, 'gettrace', None)
if gettrace is not None and gettrace():
    seed("test")

COORD_MIN = -16
COORD_MAX = 15

Point = Tuple[int, ...]
Bits = Tuple[bool, ...]


def parseRestrict(string: str, name: str = None,
                  type: Callable[[str], Any] = int,
                  min=float("-inf"), max=float("+inf")):
    result = type(string)
    if result < min or result > max:
        if name:
            raise ValueError("{name} must be in range [{min};{max}]")
        raise ValueError("Must be in range [{min};{max}]")
    return result


def probability(s): return parseRestrict(s, "Probability", float, 0, 1)
def iterations(s): return parseRestrict(s, "Iterations", int, 0)
def size(s): return parseRestrict(s, "Size", int, 0)


def pointFromStr(string: str,
                 dimension=4,
                 type: Callable[[str], Any] = int,
                 min=-16,
                 max=15) -> Point:
    result = tuple(parseRestrict(word, "Coordinate", type, min, max)
                   for word in string.split(","))
    if dimension is not None and len(result) != dimension:
        raise ValueError(f"Expected {dimension} coordinates in point, "
                         f"not {len(result)}")
    return result


def f(x: Tuple[int, int, int, int]):
    x1, x2, x3, x4 = x
    return (x1 + 2*x2 - 7)**2 + (2*x1+x2-5)**2 + sin(sin(sin(1.5 * x3))) + \
        (x3 - 1)**2 * (1+sin(sin(1.5 * x4))) + (x4-1)**2 * (1+sin(sin(x4)))


class Grey:
    _max_bits = 1
    _from_int_table: List[Bits] = [(False,), (True,)]
    _to_int_table: Dict[Bits, int] = {(False,): 0, (True,): 1}

    @classmethod
    def _extendTables(cls):
        extension = []
        for grey in cls._from_int_table[::-1]:
            new = (True,) + (False,) * (cls._max_bits - len(grey)) + grey
            extension.append(new)
        cls._from_int_table.extend(extension)
        for grey, x in zip(extension, range(len(extension), 2*len(extension))):
            cls._to_int_table[grey] = x
        cls._max_bits += 1

    @classmethod
    def from_int(cls, x: int, min_bits=5):
        while x >= len(cls._from_int_table):
            cls._extendTables()
        grey = cls._from_int_table[x]
        return (False,) * max(min_bits - len(grey), 0) + grey

    @classmethod
    def to_int(cls, grey: Bits):
        # gt rid of leading zeros
        try:
            grey = grey[grey.index(1):]
        except ValueError:
            grey = (False,)

        while len(grey) > cls._max_bits:
            cls._extendTables()
        return cls._to_int_table[grey]


def point_encode(point: Point) -> Bits:
    encoded = []
    for coord in point:
        encoded.extend(Grey.from_int(coord - COORD_MIN))
    return tuple(encoded)


def point_decode(encoded: Bits, bits=5) -> Point:
    point = []
    prev_i = 0
    for i in range(bits, len(encoded) + 1, bits):
        point.append(Grey.to_int(encoded[prev_i:i]) + COORD_MIN)
        prev_i = i
    return tuple(point)


def main():
    parser = ArgumentParser()
    pop_group = parser.add_mutually_exclusive_group()
    pop_group.add_argument("-p", "--population", type=pointFromStr,
                           nargs="+", help="Starting population of points")
    pop_group.add_argument("-s", "--size", type=size, default=20,
                           help="Population size")
    parser.add_argument(
        "mutation_prob", metavar="mutation_probability", type=probability,
        help="Probability that a given gene "
        "will negate during the mutation phase")
    parser.add_argument(
        "crossover_prob", metavar="crossover_probability", type=probability,
        help="Probability that a given pair of adjacent "
        "point will crossover during the crossover phase")
    parser.add_argument(
        "-i", "--iterations", metavar="crossover_probability", type=iterations,
        default=500, help="Probability that a given pair of adjacent "
        "point will crossover during the crossover phase")

    args = parser.parse_args()

    if not args.population:
        args.population = [tuple(randint(COORD_MIN, COORD_MAX)
                                 for _ in range(4)) for _ in range(args.size)]
        print(f"Starting population: {args.population}")

    population = [point_encode(point) for point in args.population]

    best_fitness, best_solution = genetic_algorithm(
        lambda x: f(point_decode(x)), population, args.mutation_prob,
        args.crossover_prob, args.iterations)

    print(f"Best solution: {point_decode(best_solution)}")
    print(f"Best fitness: {best_fitness}")


if __name__ == "__main__":
    main()
