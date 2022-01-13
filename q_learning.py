from typing import Any, Dict, Iterable, Tuple
import numpy as np


class QLearningAgent:
    _q: Dict[Any, Dict[Any, float]]
    learning_rate: float
    leaerning_rate_scaling_factor: float
    discount: float

    def __init__(self,
                 states: Iterable[Any],
                 actions: Iterable[Any],
                 initial_learning_rate: float,
                 leaerning_rate_scaling_factor: float,
                 discount: float):
        self._q = {s: {a: 1 for a in actions} for s in states}
        self.learning_rate = initial_learning_rate
        self.leaerning_rate_scaling_factor = leaerning_rate_scaling_factor
        self.discount = discount

    def decide(self, state: Any):
        actions = list(self._q[state].keys())
        weights = list(self._q[state].values())
        probabilities = weights / np.sum(weights)
        return np.random.choice(actions, size=1, p=probabilities)[0]

    def update_q(self,
                 state: Any,
                 next_state: Any,
                 action: Any,
                 reward: float,
                 is_done: bool):
        if not is_done:
            q_max_next_state = max(self._q[next_state].values())
        else:
            q_max_next_state = 0

        change = self.learning_rate * (
            reward +
            self.discount * q_max_next_state -
            self._q[state][action])
        self._q[state][action] += change

        self.learning_rate *= self.leaerning_rate_scaling_factor
