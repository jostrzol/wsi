# by Jakub Ostrzołek

from argparse import ArgumentParser
from typing import Callable, List, Optional, Tuple
import numpy as np
from math import sin, cos, pi
from dataclasses import dataclass


@dataclass
class Minimum:
    """
    Represents function's minimum.

    Has following attributes:
    :param point:       point at which the function has minimum
    :type point:        Tuple[float, ...]
    :param value:       value of the minimum
    :type value:        float
    :param steps_taken: steps taken to calculate the minimum
    :type steps_taken:  List[Tuple[float, ...]]
    :param iterations:  iterations taken to calculate the minimum
    :type iterations:   int
    :param found:       true if the minimum was found,
                        false if maximum number of iterations was reached
    :type found:        bool
    """
    point: Tuple[float, ...]
    value: float
    steps_taken: List[Tuple[float, ...]]
    iterations: int
    found: bool


def gradient_descend(
        fnc: Callable[..., float],
        grad: Tuple[Callable[[float], float], ...],
        start_pnt: Tuple[float, ...],
        learn_coef: float,
        stop_condition: float,
        max_iterations: Optional[float] = None):
    """
    Calculates function's minimum using gradient descend method.

    Takes following arguments:
    :param fnc:             function for which the minimum is calculated
    :type fnc:              Callable[..., float]
    :param grad             function's gradient, represented by a tuple of
                            partial derivatives of the function in each
                            dimension
    :type grad:             Tuple[Callable[[float], float], ...]
    :param start_pnt:       point at which to start the algorithm
    :type start_pnt:        Tuple[float, ...]
    :param learn_coef:      initial coefficient used to scale the effect of
                            gradient on the calculation of next point:
                                next_pnt = pnt - learn_coef * pnt_grad
    :type learn_coef:       float
    :param stop_condition:  the algorithm stops at a given point when:
                                |grad(pnt)| <= stop_condition AND
                                |next_pnt - pnt| <= stop_condition
                            lower this parameter to get a more precise result
    :type stop_condition:   float
    :param max_iterations:  if specified, the algorithm stops after the given
                            amount of iterations and returns a Minimum object
                            with found = False
    :type max_iterations:   Union[float, None] = None

    Returns a Minimum object, representing the found minimum
    """

    pnt = np.array(start_pnt)
    steps_taken: List[Tuple[float, ...]] = [pnt.tolist()]
    iterations = 0

    while(True):
        if max_iterations is not None and iterations > max_iterations:
            return Minimum(pnt, fnc(*pnt), steps_taken, iterations, False)

        pnt_grad = np.array([grad_x(x) for x, grad_x in zip(pnt, grad)])
        next_pnt = pnt - learn_coef * pnt_grad

        # stop condition
        if (np.linalg.norm(pnt_grad) <= stop_condition and
                np.linalg.norm(next_pnt - pnt) <= stop_condition):
            return Minimum(pnt, fnc(*pnt), steps_taken, iterations, True)

        iterations += 1
        if fnc(*next_pnt) >= fnc(*pnt):
            learn_coef /= 2
        else:
            pnt = next_pnt
            steps_taken.append(pnt.tolist())


def f(x1: float, x2: float):
    return x1**2 + x2**2


f_grad = (lambda x1: 2 * x1,
          lambda x2: 2 * x2)


def g(x: float):
    return x**2 - 10 * cos(2 * pi * x) + 10


g_grad = (lambda x: 2 * x + 20 * pi * sin(2 * pi * x),)


def pnt(string: str, n_coords: int = None):
    result = tuple(float(word) for word in string.split(","))
    if n_coords is not None and len(result) != n_coords:
        raise ValueError(f"Expected {n_coords} coordinates in point, "
                         f"not {len(result)}")
    return result


def format_pnt(pnt: Tuple[float, ...]):
    return f'{", ".join([f"{x:.3f}" for x in pnt])}'


def main():
    parser = ArgumentParser()
    parser.add_argument(
        "learn_coef", metavar="learning-coefficient", type=float,
        help="initial learning coefficient for calculating the minimum")
    parser.add_argument(
        "stop_condition", metavar="stop-condition", type=float,
        help="stop condition for calculating when to stop")
    parser.add_argument(
        "-f", metavar="x1,x2", type=pnt, nargs="+",
        help="starting points for function f in format x1,x2")
    parser.add_argument(
        "-g", metavar="x", type=pnt, nargs="+",
        help="starting points for function g")

    args = parser.parse_args()

    print("Minima:")
    for start_pnt in args.f:
        f_min = gradient_descend(f, f_grad, start_pnt,
                                 args.learn_coef, args.stop_condition)
        print(f'\t{start_pnt}\t= >\tf({format_pnt(f_min.point)}) '
              f'={f_min.value: .3f}')

    for start_pnt in args.g:
        g_min = gradient_descend(g, g_grad, start_pnt,
                                 args.learn_coef, args.stop_condition)
        print(f'\t{start_pnt}\t\t=>\tg({format_pnt(g_min.point)}) '
              f'= {g_min.value:.3f}')


if __name__ == "__main__":
    main()
