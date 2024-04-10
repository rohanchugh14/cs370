import numpy as np

class KuhnCFR:
    def __init__(self):
        # Initialize empty dictionaries for regrets and strategy
        self.node_map = {}  # Maps state to Node

    class Node:
        def __init__(self):
            self.info_set = ""
            self.regret_sum = np.zeros(2)  # Assuming two actions: pass(0) and bet(1)
            self.strategy = np.zeros(2)
            self.strategy_sum = np.zeros(2)

        def get_strategy(self, realization_weight):
            """Calculate strategy for a node given the current regrets."""
            normalizing_sum = 0
            for a in range(2):  # Iterate over actions
                self.strategy[a] = max(self.regret_sum[a], 0)
                normalizing_sum += self.strategy[a]
            for a in range(2):
                if normalizing_sum > 0:
                    self.strategy[a] /= normalizing_sum
                else:
                    self.strategy[a] = 1.0 / 2  # If no regrets, use uniform random strategy
            self.strategy_sum += realization_weight * self.strategy
            return self.strategy

        def get_average_strategy(self):
            """Average strategy over all training iterations."""
            avg_strategy = np.zeros(2)
            normalizing_sum = sum(self.strategy_sum)
            for a in range(2):
                if normalizing_sum > 0:
                    avg_strategy[a] = self.strategy_sum[a] / normalizing_sum
                else:
                    avg_strategy[a] = 1.0 / 2
            return avg_strategy

    def cfr(self, cards, history, p0, p1):
        plays = len(history)
        player = plays % 2
        opponent = 1 - player

        # Terminal Case: Resolve the outcome of the game
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
        node = self.node_map.get(info_set, None)
        if node is None:
            node = self.Node()
            node.info_set = info_set
            self.node_map[info_set] = node

        # For each action, recursively call cfr with additional history and probability
        strategy = node.get_strategy(p0 if player == 0 else p1)
        util = np.zeros(2)
        node_util = 0
        for a in range(2):
            next_history = history + ('p' if a == 0 else 'b')
            if player == 0:
                util[a] = -self.cfr(cards, next_history, p0 * strategy[a], p1)
            else:
                util[a] = -self.cfr(cards, next_history, p0, p1 * strategy[a])
            node_util += strategy[a] * util[a]

        # Update regrets
        for a in range(2):
            regret = util[a] - node_util
            node.regret_sum[a] += (p1 if player == 0 else p0) * regret

        return node_util

    def train(self, iterations):
        cards = [1, 2, 3]  # Kuhn Poker cards
        util = 0
        for _ in range(iterations):
            np.random.shuffle(cards)
            util += self.cfr(cards, "", 1, 1)
        print(f"Average game value (to player 1): {util / iterations}")
        for node_key in sorted(self.node_map):
            print(node_key, self.node_map[node_key].get_average_strategy())

if __name__ == "__main__":
    trainer = KuhnCFR()
    trainer.train(10000)
