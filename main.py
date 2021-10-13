from argparse import ArgumentParser
from typing import Callable, Tuple
import numpy as np
from math import sin, cos, pi


def gradient_descend(
        fnc: Callable[..., float],
        grads: Tuple[Callable[[float], float], ...],
        start_pnt: Tuple[float, ...],
        learn_coef: float,
        stop_condition: float):

    pnt = np.array(start_pnt)

    while(True):
        pnt_grad = np.array([grad(x) for x, grad in zip(pnt, grads)])
        next_pnt = pnt - learn_coef * pnt_grad

        # stop condition
        if (np.linalg.norm(pnt_grad) <= stop_condition and
                np.linalg.norm(next_pnt-pnt) <= stop_condition):
            return next_pnt, fnc(*next_pnt)

        if (fnc(*next_pnt) > fnc(*pnt)):
            learn_coef /= 2
        else:
            pnt = next_pnt


def f(x1: float, x2: float):
    return x1**2 + x2**2


f_grad = (lambda x1: 2*x1,
          lambda x2: 2*x2)


def g(x: float):
    return x**2 - 10 * cos(2*pi*x) + 10


g_grad = (lambda x: 2*x + 20 * pi * sin(2*pi*x),)


def main():
    parser = ArgumentParser("Gradient descend")
    parser.add_argument("x1_s", metavar="f-starting-x1", type=float)
    parser.add_argument("x2_s", metavar="f-starting-x2", type=float)
    parser.add_argument("x_s", metavar="g-starting-x", type=float)
    parser.add_argument("learn_coef",
                        metavar="learning-coefficient", type=float)
    parser.add_argument("stop_condition", metavar="stop-condition", type=float)

    args = parser.parse_args()

    f_result = gradient_descend(f, f_grad, (args.x1_s, args.x2_s),
                                args.learn_coef, args.stop_condition)
    g_result = gradient_descend(g, g_grad, (args.x_s,),
                                args.learn_coef, args.stop_condition)

    print(f"""Minima:
    -f: f({", ".join([f"{x:.4f}" for x in f_result[0]])}) = {f_result[1]:.4f}
    -g: g({", ".join([f"{x:.4f}" for x in g_result[0]])}) = {g_result[1]:.4f}
    """)


if __name__ == "__main__":
    main()
