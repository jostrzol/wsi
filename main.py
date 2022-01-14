from typing import List, Tuple
import gym
from q_learning import QLearningAgent
from matplotlib import pyplot as plt
import numpy as np

DISCOUNT = 0.95
LEARNING_RATE = 0.05

STRATEGY = 'epsilon'
STRATEGIES = ['epsilon', 'boltzmann']

EXPLORATION_INITIAL = 1
EXPLORATION_LAMBDA = 0.0005
EXPLORATION_MIN = 0.001

REWARD = 'NORMAL'
REWARDS = ['NORMAL', 'GRADUAL', 'FALL_LOSS', 'GRADUAL_WITH_FALL_LOSS']

EPISODES = 15_000
EPISODE_LOG_INTERVAL = 1_000
PLOT_LOOKBEHIND = 1_000

MAX_TURNS = 200


def to_dirs(q: np.ndarray):
    DIR_MAP = {0: '<', 1: 'v', 2: '>', 3: '^'}
    return np.array([DIR_MAP[max(range(len(row)), key=lambda i: row[i])] if not (
        row == 0).all() else ' ' for row in q]).reshape((4, 4))


def exp_map(value: float, initial_value: float,
            lower_bound: float, coefficient: float):
    return (lower_bound +
            (initial_value - lower_bound) * np.exp(-coefficient * value))


def reward_gradual(next_state: int, dst: Tuple[int, int]):
    x = next_state % 4
    y = next_state // 4
    dst_x, dst_y = dst
    dist = abs(x - dst_x) + abs(y - dst_y)
    return 1 / (dist + 1)


def reward_fall_loss(normal_reward: float, is_done: bool):
    if normal_reward == 0 and is_done == True:
        # fell into a hole
        return -1
    return normal_reward


def reward_gradual_with_fall_loss(next_state: int, dst: Tuple[int, int],
                                  normal_reward: float, is_done: bool):
    if normal_reward == 0 and is_done == True:
        # fell into a hole
        return -1
    x = next_state % 4
    y = next_state // 4
    dst_x, dst_y = dst
    dist = abs(x - dst_x) + abs(y - dst_y)
    return 1 / (dist + 1)


if __name__ == "__main__":
    if STRATEGY not in STRATEGIES:
        raise ValueError(f"STRATEGY must belong to [{', '.join(STRATEGIES)}]")
    if REWARD not in REWARDS:
        raise ValueError(f"REWARD must belong to [{', '.join(REWARDS)}]")

    env = gym.make('FrozenLake-v1')

    agent = QLearningAgent(
        env.observation_space.n,
        env.action_space.n,
        discount=DISCOUNT,
        learning_rate=LEARNING_RATE,
    )
    exploration = EXPLORATION_INITIAL

    rewards: List[float] = []
    try:
        for i in range(EPISODES):
            exploration = exp_map(
                i,
                EXPLORATION_INITIAL,
                EXPLORATION_MIN,
                EXPLORATION_LAMBDA)

            state = env.reset()
            is_done = False
            reward = 0
            for _ in range(MAX_TURNS):
                if STRATEGY == 'epsilon':
                    action = agent.decide_epsilon(state, exploration)
                elif STRATEGY == 'boltzmann':
                    action = agent.decide_boltzmann(state, exploration)

                next_state, reward, is_done, info = env.step(action)

                if REWARD == 'NORMAL':
                    pass
                elif REWARD == 'GRADUAL':
                    reward = reward_gradual(next_state, (3, 3))
                elif REWARD == 'GRADUAL_WITH_FALL_LOSS':
                    reward = reward_gradual_with_fall_loss(
                        next_state, (3, 3), reward, is_done)

                agent.update_q(
                    state,
                    next_state,
                    action,
                    reward,
                    is_done
                )
                state = next_state
                if is_done:
                    break

            rewards.append(reward)

            if (i + 1) % EPISODE_LOG_INTERVAL == 0:
                to_print = rewards[-EPISODE_LOG_INTERVAL:]
                print(f'EPISODE {i + 1}:')
                print(f'\tMean reward:\t\t\t{np.mean(to_print)}')
                print(f'\tReward standard deviation:\t{np.std(to_print)}')
                print(f'\tBest move map:')
                print('\t\t' + str(to_dirs(agent.get_q())).replace("\n", "\n\t\t"))
    except KeyboardInterrupt:
        pass

    env.close()

    x = np.arange(PLOT_LOOKBEHIND, len(rewards))
    y = [np.mean(rewards[i - PLOT_LOOKBEHIND: i])
         for i in range(PLOT_LOOKBEHIND, len(rewards))]
    plt.plot(x, y)
    plt.show()
