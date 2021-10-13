from main import gradient_descend, f, f_grad, g, g_grad
import pytest

F_START_PNTS = [(x, y) for x in range(-10, 11) for y in range(-10, 11)]
G_START_PNTS = [(x,) for x in range(-10, 91)]

LEARN_COEFS = [0.9, 0.5, 0.25, 0.125, 0.0625]
STOP_CONDITION = 0.001


@pytest.mark.parametrize("f_start_pnt", F_START_PNTS)
@pytest.mark.parametrize("learn_coef", LEARN_COEFS)
def test_benchmark_f(f_start_pnt, learn_coef, benchmark):
    benchmark.pedantic(
        target=gradient_descend,
        args=(f, f_grad, f_start_pnt, learn_coef, STOP_CONDITION),
        rounds=1)


@pytest.mark.parametrize("g_start_pnt", G_START_PNTS)
@pytest.mark.parametrize("learn_coef", LEARN_COEFS)
def test_benchmark_g(g_start_pnt, learn_coef, benchmark):
    benchmark.pedantic(
        target=gradient_descend,
        args=(g, g_grad, g_start_pnt, learn_coef, STOP_CONDITION),
        rounds=1)
