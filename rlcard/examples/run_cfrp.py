''' An example of solve Leduc Hold'em with CFR (chance sampling)
'''
import os
import argparse

import rlcard
from rlcard.agents import (
    RandomAgent,
)

import time

from cfr_agent import CFRAgent
from cfrp_agent import CFRPAgent

from rlcard.utils import (
    set_seed,
    tournament,
    Logger,
    plot_curve,
)

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
    agent = CFRPAgent(
        env,
        os.path.join(
            args.log_dir,
            'cfrp_model',
        ),
    )
    agent.load()  # If we have saved model, we first load the model

    # Evaluate CFR against random
    eval_env.set_agents([
        agent,
        RandomAgent(num_actions=env.num_actions),
    ])

    # Start training
    with Logger(args.log_dir) as logger:
        total_reward = 0
        for episode in range(args.num_episodes):
            agent.train()
            print('\rIteration {}'.format(episode), end='')
            # Evaluate the performance. Play with Random agents.
            if episode % args.evaluate_every == 0:
                agent.save() # Save model
                reward = tournament(
                        eval_env,
                        args.num_eval_games
                    )[0]
                logger.log_performance(
                    episode,
                    reward
                )
            total_reward += reward
        print("Average reward: ", total_reward / args.num_episodes)
        # Get the paths
        csv_path, fig_path = logger.csv_path, logger.fig_path
    # Plot the learning curve
    plot_curve(csv_path, fig_path, 'cfrp')

if __name__ == '__main__':
    parser = argparse.ArgumentParser("CFRP example in RLCard")
    parser.add_argument(
        '--seed',
        type=int,
        default=1234,
    )
    parser.add_argument(
        '--num_episodes',
        type=int,
        default=5000,
    )
    parser.add_argument(
        '--num_eval_games',
        type=int,
        default=2000,
    )
    parser.add_argument(
        '--evaluate_every',
        type=int,
        default=100,
    )
    parser.add_argument(
        '--log_dir',
        type=str,
        default='experiments/leduc_holdem_cfrp_result/',
    )

    args = parser.parse_args()

    start_time = time.time()

    train(args)

    end_time = time.time()

    print("training cfrp took: ", end_time - start_time, " seconds.")
    