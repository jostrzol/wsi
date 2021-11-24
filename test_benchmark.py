from dataclasses import dataclass
from typing import List, Optional, Tuple
from pytest import mark
from pytest_benchmark.fixture import BenchmarkFixture
from alphabeta_dots_and_boxes import play_dots_and_boxes
from two_player_games.games.dots_and_boxes import (
    DotsAndBoxes, DotsAndBoxesState)
from two_player_games.games.dots_and_boxes import Player


@dataclass
class BParams:
    size: int
    p1_depth: int
    p2_depths: List[int]


PARAMS = [
    BParams(2, 6, [4, 5, 6, 7, 8]),
    BParams(3, 4, [2, 3, 4, 5, 6]),
    BParams(4, 3, [1, 2, 3, 4]),
    BParams(5, 2, [1, 2, 3]),
]


def unpack_params(params: List[BParams]):
    for bparams in params:
        for p2_depth in bparams.p2_depths:
            yield (bparams.size,
                   bparams.p1_depth,
                   p2_depth)


@mark.parametrize("size,p1_depth,p2_depth", list(unpack_params(PARAMS)))
def test_benchmark(size: int, p1_depth: int, p2_depth: int,
                   benchmark: BenchmarkFixture):
    game = DotsAndBoxes(size)
    result: List[Tuple[
        DotsAndBoxesState,
        Optional[Player],
        Optional[int]]] = benchmark.pedantic(
        lambda *args: list(play_dots_and_boxes(*args)),
        (game, p1_depth, p2_depth))

    scores = [None] * (len(result))
    for i, (state, _, _) in enumerate(result):
        score_dict = state.get_scores()
        scores[i] = (score_dict[game.first_player],
                     score_dict[game.second_player])
    extra = benchmark.extra_info
    extra["p1_char"] = game.first_player.char
    extra["p2_char"] = game.second_player.char
    extra["scores"] = scores
    extra["values"] = [
        (player.char, value) for _, player, value in result[1:]]
