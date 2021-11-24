# by Jakub Ostrzołek

from typing import Generator, Optional, Tuple
from two_player_games.games.dots_and_boxes import (
    DotsAndBoxes, DotsAndBoxesState, Player)
from itertools import cycle

from alphabeta import alphabeta


def dots_and_boxes_evaluate_state(
        state: DotsAndBoxesState,
        max_player: Player):

    if state.current_player is max_player:
        min_player = state.other_player
    else:
        min_player = state.current_player

    scores = state.get_scores()
    return scores[max_player] - scores[min_player]


def play_dots_and_boxes(
    game: DotsAndBoxes, p1_depth: int, p2_depth: int
) -> Generator[
        Tuple[DotsAndBoxesState,
              Optional[Player],
              Optional[int]],
        None, None]:

    depths = cycle([p1_depth, p2_depth])

    yield (game.state, None, None)

    while not game.is_finished():
        moving_player = game.get_current_player()
        value, move = alphabeta(
            state=game.state,
            depth=next(depths),
            evaluate_state=dots_and_boxes_evaluate_state)
        game.make_move(move)

        yield (game.state, moving_player, value)
