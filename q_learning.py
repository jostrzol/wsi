import numpy as np
from random import random, choice


class QLearningAgent:
    _q: np.ndarray
    _n_actions: int
    _n_states: int
    discount: float
    learning_rate: float

    def __init__(self,
                 n_states: int,
                 n_actions: int,
                 discount: float,
                 learning_rate: float):
        self._n_states = n_states
        self._n_actions = n_actions
        self._q = np.zeros((n_states, n_actions))
        self.learning_rate = learning_rate
        self.discount = discount

    def decide_epsilon(self, state: int, epsilon: float):
        weights = self._q[state]
        total_weights = weights.sum()

        if random() < epsilon or total_weights == 0:
            return choice(range(len(weights)))
        else:
            return max(range(len(weights)), key=lambda i: weights[i])

    def decide_boltzmann(self, state: int, temperature: float):
        weights = np.exp(self._q[state] / temperature)
        probabilities = weights / weights.sum()

        return np.random.choice(range(self._n_actions), p=probabilities)

    def update_q(self,
                 state: int,
                 next_state: int,
                 action: int,
                 reward: float,
                 is_done: bool):
        # if not is_done:
        #     q_max_next_state = self._q[next_state].max()
        # else:
        #     q_max_next_state = 0
        q_max_next_state = self._q[next_state].max()

        change = self.learning_rate * (
            reward +
            self.discount * q_max_next_state -
            self._q[state][action])
        self._q[state][action] += change

    def get_q(self):
        return self._q
