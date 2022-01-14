from typing import List
import gym
from q_learning import QLearningAgent
from matplotlib import pyplot as plt
import numpy as np

EPISODES = 100_000
EPISODE_LOG_INTERVAL = 10_000
PLOT_LOOKBEHIND = 10_000

EPSILON_SCALING_FACTOR = 0.5
EPSILON_MIN = 0.001

MAX_TURNS = 200

if __name__ == "__main__":
    env = gym.make('FrozenLake-v1')

    agent = QLearningAgent(
        env.observation_space.n,
        env.action_space.n,
        discount=0.85,
        learning_rate_initial=0.8,
        epsilon_initial=1,
        # epsilon_scaling_factor=0.99999,
        # epsilon_min=0.001,
        # temperature=0.8
    )

    rewards: List[float] = []
    for i in range(1, EPISODES + 1):
        state = env.reset()
        is_done = False
        reward = 0
        for _ in range(MAX_TURNS):
            # env.render()
            action = agent.decide_epsilon(state)
            next_state, reward, is_done, info = env.step(action)
            # if is_done != 0:
            #     x = next_state % 4
            #     y = next_state // 4
            #     dst_y = 3
            #     dst_x = 3
            #     dist = abs(x - dst_x) + abs(y - dst_y)
            #     reward = 1 / (dist + 1)

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
        agent.epsilon = max(
            agent.epsilon * EPSILON_SCALING_FACTOR,
            EPSILON_MIN
        )

        if i % EPISODE_LOG_INTERVAL == 0:
            to_print = rewards[-EPISODE_LOG_INTERVAL:]
            print(f'EPISODE {i}:')
            print(f'\tMean reward:\t\t\t{np.mean(to_print)}')
            print(f'\tReward standard deviation:\t{np.std(to_print)}')

    env.close()

    x = np.arange(PLOT_LOOKBEHIND, len(rewards))
    y = [np.mean(rewards[i - PLOT_LOOKBEHIND: i])
         for i in range(PLOT_LOOKBEHIND, len(rewards))]
    plt.plot(x, y)
    plt.show()
