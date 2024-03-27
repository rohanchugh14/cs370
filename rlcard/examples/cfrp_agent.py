import numpy as np
import collections
import os
import pickle
from rlcard.utils.utils import *

class CFRPAgent():  # Changed class name to reflect CFR+
    ''' Implement CFR+ (chance sampling) algorithm '''

    def __init__(self, env, model_path='./cfrp_model'):  # Changed default model path
        ''' Initialize Agent '''
        self.use_raw = False
        self.env = env
        self.model_path = model_path

        # Policies and regrets remain the same
        self.policy = collections.defaultdict(list)
        self.average_policy = collections.defaultdict(np.array)
        self.regrets = collections.defaultdict(np.array)
        self.iteration = 0

        self.total_regrets = []
        self.cumulative_regrets = 0

    def train(self):
        ''' Do one iteration of CFR+ '''
        self.iteration += 1
        self.cumulative_regrets = 0


        for player_id in range(self.env.num_players):
            self.env.reset()
            probs = np.ones(self.env.num_players)
            self.traverse_tree(probs, player_id)
        self.update_policy()  # No change here, but the methods it calls have been updated

        self.total_regrets.append(self.cumulative_regrets)

    def traverse_tree(self, probs, player_id):
        ''' Traverse the game tree, update the regrets for CFR+ '''
        if self.env.is_over():
            return self.env.get_payoffs()

        current_player = self.env.get_player_id()
        action_utilities = {}
        state_utility = np.zeros(self.env.num_players)
        obs, legal_actions = self.get_state(current_player)
        action_probs = self.action_probs(obs, legal_actions, self.policy)

        for action in legal_actions:
            action_prob = action_probs[action]
            new_probs = probs.copy()
            new_probs[current_player] *= action_prob
            self.env.step(action)
            utility = self.traverse_tree(new_probs, player_id)
            self.env.step_back()
            state_utility += action_prob * utility
            action_utilities[action] = utility

        if current_player == player_id:
            # Compute regret and strategy updates specific to CFR+
            player_prob = probs[current_player]
            counterfactual_prob = (np.prod(probs[:current_player]) * np.prod(probs[current_player + 1:]))
            player_state_utility = state_utility[current_player]

            if obs not in self.regrets:
                self.regrets[obs] = np.zeros(self.env.num_actions)
            if obs not in self.average_policy:
                self.average_policy[obs] = np.zeros(self.env.num_actions)

            for action in legal_actions:
                action_prob = action_probs[action]
                regret = counterfactual_prob * (action_utilities[action][current_player] - player_state_utility)
                self.regrets[obs][action] = max(self.regrets[obs][action] + regret, 0)  # CFR+: Store only positive regrets
                self.average_policy[obs][action] += self.iteration * player_prob * action_prob  # Same as CFR
        return state_utility

    def update_policy(self):
        ''' Update policy based on the current regrets for CFR+ '''
        for obs in self.regrets:
            self.policy[obs] = self.regret_matching(obs)  # Regret matching logic is modified for CFR+

    def regret_matching(self, obs):
        ''' Apply regret matching for CFR+ '''
        regret = self.regrets[obs]
        # For CFR+: Normalize positive regrets only
        positive_regret_sum = sum([r for r in regret if r > 0])

        action_probs = np.zeros(self.env.num_actions)

        if positive_regret_sum > 0:
            self.cumulative_regrets += positive_regret_sum
            for action in range(self.env.num_actions):
                

                action_probs[action] = max(0.0, regret[action]) / positive_regret_sum  # Use positive regrets only

        else:
            for action in range(self.env.num_actions):
                action_probs[action] = 1.0 / self.env.num_actions
        return action_probs

    def action_probs(self, obs, legal_actions, policy):
        ''' Obtain the action probabilities of the current state

        Args:
            obs (str): state_str
            legal_actions (list): List of leagel actions
            player_id (int): The current player
            policy (dict): The used policy

        Returns:
            (tuple) that contains:
                action_probs(numpy.array): The action probabilities
                legal_actions (list): Indices of legal actions
        '''
        if obs not in policy.keys():
            action_probs = np.array([1.0/self.env.num_actions for _ in range(self.env.num_actions)])
            self.policy[obs] = action_probs
        else:
            action_probs = policy[obs]
        action_probs = remove_illegal(action_probs, legal_actions)
        return action_probs

    def eval_step(self, state):
        ''' Given a state, predict action based on average policy

        Args:
            state (numpy.array): State representation

        Returns:
            action (int): Predicted action
            info (dict): A dictionary containing information
        '''
        probs = self.action_probs(state['obs'].tostring(), list(state['legal_actions'].keys()), self.average_policy)
        action = np.random.choice(len(probs), p=probs)

        info = {}
        info['probs'] = {state['raw_legal_actions'][i]: float(probs[list(state['legal_actions'].keys())[i]]) for i in range(len(state['legal_actions']))}

        return action, info

    def get_state(self, player_id):
        ''' Get state_str of the player

        Args:
            player_id (int): The player id

        Returns:
            (tuple) that contains:
                state (str): The state str
                legal_actions (list): Indices of legal actions
        '''
        state = self.env.get_state(player_id)
        return state['obs'].tostring(), list(state['legal_actions'].keys())

    def save(self):
        ''' Save model
        '''
        if not os.path.exists(self.model_path):
            os.makedirs(self.model_path)

        policy_file = open(os.path.join(self.model_path, 'policy.pkl'),'wb')
        pickle.dump(self.policy, policy_file)
        policy_file.close()

        average_policy_file = open(os.path.join(self.model_path, 'average_policy.pkl'),'wb')
        pickle.dump(self.average_policy, average_policy_file)
        average_policy_file.close()

        regrets_file = open(os.path.join(self.model_path, 'regrets.pkl'),'wb')
        pickle.dump(self.regrets, regrets_file)
        regrets_file.close()

        iteration_file = open(os.path.join(self.model_path, 'iteration.pkl'),'wb')
        pickle.dump(self.iteration, iteration_file)
        iteration_file.close()

    def load(self):
        ''' Load model
        '''
        if not os.path.exists(self.model_path):
            return

        policy_file = open(os.path.join(self.model_path, 'policy.pkl'),'rb')
        self.policy = pickle.load(policy_file)
        policy_file.close()

        average_policy_file = open(os.path.join(self.model_path, 'average_policy.pkl'),'rb')
        self.average_policy = pickle.load(average_policy_file)
        average_policy_file.close()

        regrets_file = open(os.path.join(self.model_path, 'regrets.pkl'),'rb')
        self.regrets = pickle.load(regrets_file)
        regrets_file.close()

        iteration_file = open(os.path.join(self.model_path, 'iteration.pkl'),'rb')
        self.iteration = pickle.load(iteration_file)
        iteration_file.close()
