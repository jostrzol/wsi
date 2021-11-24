from typing import Callable, Tuple
from math import inf

from two_player_games.state import State
from two_player_games.player import Player
from two_player_games.move import Move


EvaluatedMove = Tuple[float, Move]


def alphabeta(
    state: State, depth: int,
    evaluate_state: Callable[[State, Player], float],
    max_player: Player = None,
    alpha: EvaluatedMove = (-inf, None),
    beta: EvaluatedMove = (inf, None)
) -> EvaluatedMove:
    """
    Returns tuple [value, move] of the best move for the current player,
    using minimax algorithm with alpha - beta pruning
    """
    if max_player is None:
        max_player = state.get_current_player()

    if state.is_finished() or depth < 1:
        return (evaluate_state(state, max_player), None)

    if state.get_current_player() is max_player:
        # max's move
        for move in state.get_moves():
            # evaluate move
            value = alphabeta(
                state=state.make_move(move),
                depth=depth - 1,
                evaluate_state=evaluate_state,
                max_player=max_player,
                alpha=alpha,
                beta=beta)[0]
            # update alpha
            if value > alpha[0]:
                alpha = (value, move)
            # min won't consider the current
            # node in his previous move,
            # as he has a better option
            if alpha[0] >= beta[0]:
                return beta
        # return max's best choice
        return alpha
    else:
        # min's move
        for move in state.get_moves():
            # evaluate move
            value = alphabeta(
                state=state.make_move(move),
                depth=depth - 1,
                evaluate_state=evaluate_state,
                max_player=max_player,
                alpha=alpha,
                beta=beta)[0]
            # update beta
            if value < beta[0]:
                beta = (value, move)
            # max won't consider the current
            # node in his previous move,
            # as he has a better option
            if alpha[0] >= beta[0]:
                return alpha
        # return min's best choice
        return beta
