import random

def cfr_rock_paper_scissors(num_iterations):
    """
    A simple Counterfactual Regret Minimization (CFR) implementation for Rock-Paper-Scissors game.
    """
    # Strategies for each action over time
    strategy = {"rock": 0, "paper": 0, "scissors": 0}
    strategy_sum = {"rock": 0, "paper": 0, "scissors": 0}
    regret_sum = {"rock": 0, "paper": 0, "scissors": 0}
    action_utilities = {"rock": 0, "paper": 0, "scissors": 0}
    starting_strategy = {"rock": 0.1, "paper": 0.8, "scissors": 0.1}
    
    def get_strategy():
        normalizing_sum = 0
        for action in strategy:
            strategy[action] = regret_sum[action] if regret_sum[action] > 0 else 0
            normalizing_sum += strategy[action]
        for action in strategy:
            if normalizing_sum > 0:
                strategy[action] /= normalizing_sum
            else:
                strategy[action] = starting_strategy[action]
            strategy_sum[action] += strategy[action]
        return strategy

    def get_action(strategy):
        r = random.random()
        cumulative_probability = 0
        for action in strategy:
            cumulative_probability += strategy[action]
            if r < cumulative_probability:
                return action
        return action 

    def train(iterations):
        for _ in range(iterations):
            # Update strategy
            current_strategy = get_strategy()
            
            opponent_action = get_action(current_strategy)
            for action in action_utilities:
                if action == opponent_action:
                    # Tie
                    action_utilities[action] = 0
                elif (action == "rock" and opponent_action == "scissors") or \
                     (action == "paper" and opponent_action == "rock") or \
                     (action == "scissors" and opponent_action == "paper"):
                    # Win
                    action_utilities[action] = 1
                else:
                    # Lose
                    action_utilities[action] = -1
                    
            # Update regret sums
            for action in regret_sum:
                regret_sum[action] += action_utilities[action] - action_utilities[get_action(current_strategy)]

    train(num_iterations)
    
    # Normalize the accumulated strategy to get the average strategy
    average_strategy = {action: strategy_sum[action] / num_iterations for action in strategy_sum}
    print(strategy)
    print(strategy_sum)
    print(regret_sum)
    return average_strategy

avg = cfr_rock_paper_scissors(10000)
print([itm for itm in avg.items()])
