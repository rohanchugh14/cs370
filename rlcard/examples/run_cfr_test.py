''' An example of solve Leduc Hold'em with CFR (chance sampling)
'''
import os
import argparse

import rlcard
from rlcard.agents import (
    # CFRAgent,
    RandomAgent,
)
from rlcard.utils import (
    set_seed,
    tournament,
    Logger,
    plot_curve,
)

import matplotlib.pyplot as plt

from cfr_agent import CFRAgent

def train(args):
    # Make environments, CFR only supports Leduc Holdem
    env = rlcard.make(
        'leduc-holdem',
        config={
            'seed': 0,
            'allow_step_back': True,
        }
    )
    eval_env = rlcard.make(
        'leduc-holdem',
        config={
            'seed': 0,
        }
    )

    # Seed numpy, torch, random
    set_seed(args.seed)

    # Initilize CFR Agent
    agent = CFRAgent(
        env,
        os.path.join(
            args.log_dir,
            'cfr_model',
        ),
    )
    # agent.load()  # If we have saved model, we first load the model

    # Evaluate CFR against random
    eval_env.set_agents([
        agent,
        # agent
        RandomAgent(num_actions=env.num_actions),
    ])

    # Start training

    for episode in range(args.num_episodes):
        # gain = agent.train()
        # print(gain)
        agent.train()
        print('\rIteration {}'.format(episode))

    print(agent.total_regrets)

    # get the change in regret from each iteration
    gain = []
    for i in range(1, len(agent.total_regrets)):
        gain.append(agent.total_regrets[i] - agent.total_regrets[i-1])

    # Plot the learning curve
    plt.figure(figsize=(10, 5))
    # plt.plot(agent.total_regrets, label='avg Regret')
    plt.plot(gain, label='gain')
    plt.xlabel('Iteration')
    plt.ylabel('Gain')
    plt.title('Gain per Iteration')
    plt.legend()
    plt.show()

    # Plot the learning curve
    plt.figure(figsize=(10, 5))
    plt.plot(agent.total_regrets, label='Cumulative Regret')
    # plt.plot(gain, label='gain')
    plt.xlabel('Iteration')
    plt.ylabel('Total Regret')
    plt.title('Total Regret per Iteration')
    plt.legend()
    plt.show()

if __name__ == '__main__':
    parser = argparse.ArgumentParser("CFR example in RLCard")
    parser.add_argument(
        '--seed',
        type=int,
        default=42,
    )
    parser.add_argument(
        '--num_episodes',
        type=int,
        default=5000,
    )
    parser.add_argument(
        '--num_eval_games',
        type=int,
        default=100,
    )
    parser.add_argument(
        '--evaluate_every',
        type=int,
        default=5,
    )
    parser.add_argument(
        '--log_dir',
        type=str,
        default='experiments/leduc_holdem_cfr_result/',
    )

    args = parser.parse_args()

    train(args)
    
