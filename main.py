from typing import List
import gym
from q_learning import QLearningAgent
import numpy as np

EPISODES = 10000
EPISODE_LOG_INTERVAL = 1000

if __name__ == "__main__":
    env = gym.make('FrozenLake-v1')

    agent = QLearningAgent(
        range(env.observation_space.n),
        range(env.action_space.n),
        initial_learning_rate=1,
        leaerning_rate_scaling_factor=0.95,
        discount=0.5
    )

    rewards: List[float] = []
    for i in range(EPISODES):
        state = env.reset()
        is_done = False
        while not is_done:
            action = agent.decide(state)
            next_state, reward, is_done, info = env.step(action)

            agent.update_q(
                state,
                next_state,
                action,
                reward,
                is_done
            )
            state = next_state

        rewards.append(reward)

        if i % EPISODE_LOG_INTERVAL == 0:
            print(f'EPISODE {i}:')
            print(f'\tMean reward:\t\t\t{np.mean(rewards)}')
            print(f'\tReward standard deviation:\t{np.std(rewards)}')
            rewards = []

    env.close()
