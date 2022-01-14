from typing import Any, Dict, Iterable

import numpy as np
from random import random


class QLearningAgent:
    _q: np.ndarray
    _n_actions: int
    _n_states: int
    discount: float

    learning_rate: float
    # learning_rate_scaling_factor: float
    # learning_rate_min: float

    epsilon: float
    # epsilon_scaling_factor: float
    # epsilon_min: float

    temperature: float

    def __init__(self,
                 n_states: int,
                 n_actions: int,
                 discount: float,
                 learning_rate_initial: float,
                 #  learning_rate_scaling_factor: float = 1,
                 #  learning_rate_min: float = 0,
                 epsilon_initial: float = 1,
                 #  epsilon_scaling_factor: float = 0.99999,
                 #  epsilon_min: float = 0.001,
                 temperature: float = 0.5):
        self._n_states = n_states
        self._n_actions = n_actions
        self._q = np.zeros((n_states, n_actions))
        self.learning_rate = learning_rate_initial
        # self.leaerning_rate_scaling_factor = learning_rate_scaling_factor
        # self.learning_rate_min = learning_rate_min
        self.discount = discount
        self.epsilon = epsilon_initial
        # self.epsilon_scaling_factor = epsilon_scaling_factor
        # self.epsilon_min = epsilon_min
        self.temperature = temperature

    def decide_epsilon(self, state: int):
        weights = self._q[state]
        total_weights = weights.sum()

        if random() < self.epsilon or total_weights == 0:
            probabilities = None
        else:
            probabilities = weights / total_weights

        # self.epsilon *= self.epsilon_scaling_factor
        # self.epsilon_min = max(self.epsilon_min,
        #                        self.epsilon)

        return np.random.choice(
            range(self._n_actions), size=1, p=probabilities)[0]

    def decide_boltzmann(self, state: int):
        weights = np.exp(self._q[state] / self.temperature)
        probabilities = weights / weights.sum()

        return np.random.choice(
            range(self._n_actions), size=1, p=probabilities)[0]

    def update_q(self,
                 state: int,
                 next_state: int,
                 action: Any,
                 reward: float,
                 is_done: bool):
        if not is_done:
            q_max_next_state = self._q[next_state].max()
        else:
            q_max_next_state = 0

        change = self.learning_rate * (
            reward +
            self.discount * q_max_next_state -
            self._q[state][action])
        self._q[state][action] += change

        # self.learning_rate *= self.leaerning_rate_scaling_factor
        # self.learning_rate_min = max(self.learning_rate_min,
        #                              self.learning_rate)
