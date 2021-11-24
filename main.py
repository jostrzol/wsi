# by Jakub Ostrzołek

from argparse import ArgumentParser
from math import inf
from alphabeta_dots_and_boxes import play_dots_and_boxes

from two_player_games.games.dots_and_boxes import (
    DotsAndBoxes, DotsAndBoxesState)


BAR = "=" * 50


def constrain(min=-inf, max=inf, type=float):
    def wrapped_type(string: str):
        result = type(string)
        if result < min or result > max:
            raise ValueError(f"not in range [{min}, {max}]")
        return result
    return wrapped_type


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("size", type=constrain(2, type=int),
                        help="gameboard size (at least 2)")
    parser.add_argument("depth", type=constrain(1, type=int),
                        help="search depth for player 1 (>= 1)")
    parser.add_argument("depth2", type=constrain(1, type=int),
                        help="search depth for player 2 (>= 1)")

    args = parser.parse_args()

    if not hasattr(args, "depth2"):
        args.depth2 = args.depth

    state: DotsAndBoxesState = None
    for state, moving_player, value in play_dots_and_boxes(
            DotsAndBoxes(args.size), args.depth, args.depth2):

        if moving_player is not None:
            print(f"{moving_player.char}'s move value: {value}")
            print(BAR)

        print(state)
        print(BAR)

        prev_state = state

    winner = state.get_winner()
    if winner is None:
        print("Draw")
    else:
        print(f"{winner.char} won")
