from argparse import ArgumentParser
from math import inf

from two_player_games.games.dots_and_boxes import (
    DotsAndBoxes, DotsAndBoxesState, Player)

from alphabeta import alphabeta

BAR = "=" * 50


def constrain(min=-inf, max=inf, type=float):
    def wrapped_type(string: str):
        result = type(string)
        if result < min or result > max:
            raise ValueError(f"not in range [{min}, {max}]")
        return result
    return wrapped_type


def dots_and_boxes_evaluate_state(
        state: DotsAndBoxesState,
        max_player: Player):

    if state.current_player is max_player:
        min_player = state.other_player
    else:
        min_player = state.current_player

    scores = state.get_scores()
    return scores[max_player] - scores[min_player]


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("size", type=constrain(2, type=int),
                        help="gameboard size (at least 2)")
    parser.add_argument("depth", type=constrain(1, type=int),
                        help="search depth (at least 1)")
    args = parser.parse_args()

    game = DotsAndBoxes(args.size)

    print(game)
    print(BAR)
    while not game.is_finished():
        value, move = alphabeta(
            state=game.state,
            depth=args.depth,
            evaluate_state=dots_and_boxes_evaluate_state)

        player = game.get_current_player()
        game.make_move(move)

        print(f"{player.char}'s move value: {value}")
        print(BAR)

        print(game)
        print(BAR)

    winner = game.get_winner()
    if winner is None:
        print("Draw")
    else:
        print(f"{winner.char} won")
