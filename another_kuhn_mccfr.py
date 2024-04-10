import numpy as np

class MonteCarloKuhnCFR:
    def __init__(self):
        self.node_map = {}

    class Node:
        def __init__(self, actions=2):
            self.regret_sum = np.zeros(actions)
            self.strategy_sum = np.zeros(actions)
            self.actions = actions

        def get_strategy(self, realization_weight):
            strategy = np.maximum(self.regret_sum, 0)
            if np.sum(strategy) > 0:
                strategy /= np.sum(strategy)
            else:
                strategy = np.ones(self.actions) / self.actions
            self.strategy_sum += realization_weight * strategy
            return strategy

        def get_average_strategy(self):
            avg_strategy = self.strategy_sum
            if np.sum(avg_strategy) > 0:
                avg_strategy /= np.sum(avg_strategy)
            else:
                avg_strategy = np.ones(self.actions) / self.actions
            return avg_strategy

    def cfr(self, cards, history, p0, p1):
        plays = len(history)
        player = plays % 2
        opponent = 1 - player
        
        # Terminal case
        if plays > 1:
            terminal_pass = history[-1] == 'p'
            double_bet = history[-2:] == "bb"
            is_player_card_higher = cards[player] > cards[opponent]
            if terminal_pass:
                if history == "pp":
                    return 1 if is_player_card_higher else -1
                else:
                    return 1
            elif double_bet:
                return 2 if is_player_card_higher else -2

        info_set = str(cards[player]) + history
        node = self.node_map.get(info_set)
        if node is None:
            node = self.Node()
            self.node_map[info_set] = node

        # Monte Carlo CFR: Sample actions based on the current strategy
        strategy = node.get_strategy(p0 if player == 0 else p1)
        action_probs = np.random.choice([0, 1], p=strategy)
        util = np.zeros(2)
        node_util = 0
        
        for a in [action_probs]:  # Only sample one action for traversal
            next_history = history + ('p' if a == 0 else 'b')
            if player == 0:
                util[a] = -self.cfr(cards, next_history, p0 * strategy[a], p1)
            else:
                util[a] = -self.cfr(cards, next_history, p0, p1 * strategy[a])
            node_util += strategy[a] * util[a]

        # Update regrets for all actions
        for a in range(2):
            regret = util[a] - node_util
            node.regret_sum[a] += (p1 if player == 0 else p0) * regret

        return node_util

    def train(self, iterations):
        cards = [1, 2, 3]
        util = 0
        for _ in range(iterations):
            np.random.shuffle(cards)
            util += self.cfr(cards, "", 1, 1)
        print(f"Average game value (to player 1): {util / iterations}")
        for node_key in self.node_map:
            print(node_key, self.node_map[node_key].get_average_strategy())

if __name__ == "__main__":
    trainer = MonteCarloKuhnCFR()
    trainer.train(100000)
