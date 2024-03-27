''' An example of solve Leduc Hold'em with CFR (chance sampling)
'''
import os
import argparse
import time

import torch

import rlcard
from rlcard.agents import (
    CFRAgent,
    RandomAgent,
    DQNAgent
)
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
    cfr_agent = CFRAgent(
        env,
        os.path.join(
            args.log_dir,
            'cfr_model',
        ),
    )
    cfr_agent.load()  # If we have saved model, we first load the model

    if args.load_checkpoint_path != "":
        dqn_agent = DQNAgent.from_checkpoint(checkpoint=torch.load(args.load_checkpoint_path))
    else:
        print("COULDN'T FIND DQN AGENT PATH")

    # Evaluate CFR against random
    eval_env.set_agents([
        cfr_agent,
        cfr_agent,
        # dqn_agent,
        # RandomAgent(num_actions=env.num_actions),
    ])

    # Start training
    with Logger(args.log_dir) as logger:
        for episode in range(args.num_episodes):
            reward = tournament(
                eval_env,
                args.num_eval_games
            )[0]
            logger.log_performance(
                    episode,
                    reward
            )
        # total_reward = 0
        # for episode in range(args.num_episodes):
        #     agent.train()
        #     print('\rIteration {}'.format(episode), end='')
        #     # Evaluate the performance. Play with Random agents.
        #     if episode % args.evaluate_every == 0:
        #         agent.save() # Save model
        #         reward = tournament(
        #                 eval_env,
        #                 args.num_eval_games
        #             )[0]
        #         logger.log_performance(
        #             episode,
        #             reward
        #         )
        #     total_reward += reward
        
        # print('\nAverage reward against random agent: ', total_reward/args.num_episodes)

        # Get the paths
        # csv_path, fig_path = logger.csv_path, logger.fig_path
    # Plot the learning curve
    # plot_curve(csv_path, fig_path, 'cfr')

if __name__ == '__main__':
    parser = argparse.ArgumentParser("CFR example in RLCard")
    parser.add_argument(
        '--seed',
        type=int,
        default=1234,
    )
    parser.add_argument(
        '--num_episodes',
        type=int,
        default=100,
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
        default='experiments/leduc_holdem_cfr_result/',
    )
    parser.add_argument(
        '--load_checkpoint_path',
        type=str,
        default='experiments/leduc_holdem_dqn_result/checkpoint_dqn.pt',
    )

    args = parser.parse_args()

    start_time = time.time()

    train(args)

    end_time = time.time()

    print("training cfr took: ", end_time - start_time, " seconds.")
    