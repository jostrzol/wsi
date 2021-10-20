# by Jakub Ostrzołek

from main import gradient_descend, f, f_grad, g, g_grad, Minimum
import pytest
import numpy as np

MAX_ITERATIONS = 1000

F_START_PNTS = [(0, 0), (10, 10), (-10, -30), (10, 100), (1000, 1000)]
G_START_PNTS = [(x,)for x in [-1.7, -1, 0, 1, 1.2, 1.5, 1.8, 2, 10, 100]]

LEARN_COEFS = [0.06, 0.1, 0.5, 0.8, 1, 1.2]
STOP_CONDITION = 0.001


@pytest.mark.parametrize("fnc,gradient,fnc_name,start_pnt",
                         [(f, f_grad, "f", s_pnt) for s_pnt in F_START_PNTS] +
                         [(g, g_grad, "g", s_pnt) for s_pnt in G_START_PNTS])
@pytest.mark.parametrize("learn_coef", LEARN_COEFS)
def test_benchmark(fnc, gradient, fnc_name, start_pnt, learn_coef, benchmark):
    benchmark.extra_info["function"] = fnc_name
    min: Minimum = benchmark.pedantic(
        target=gradient_descend,
        args=(fnc, gradient, start_pnt, learn_coef,
              STOP_CONDITION, MAX_ITERATIONS),
        rounds=1)
    benchmark.extra_info["steps_taken"] = min.steps_taken
    benchmark.extra_info["iterations"] = min.iterations
    benchmark.extra_info["found"] = min.found
    benchmark.extra_info["random"] = False
    assert min.found
    pnt_grad = [grad_x(x) for x, grad_x in zip(min.point, gradient)]
    assert np.linalg.norm(pnt_grad) <= STOP_CONDITION
