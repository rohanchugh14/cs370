from tabulate import tabulate
import matplotlib.pyplot as plt

# we only have 3 ranks in Kuhn Poker
RANKS = ['K', 'Q', 'J']

# our only actions are to bet or pass
# in some cases, b represents call, and p represents fold
ACTIONS = ['b', 'p']

# hardcode terminal actions. this is when a game ends
TERMINAL_ACTION_STRINGS = {
    'pp',
    'bb',
    'bp',
    'pbb',
    'pbp',
}

# infoset actoin strings. this is when a player has to make a decision
INFOSET_ACTION_STRINGS = {
    '',
    'b',
    'p',
    'pb'
}

# stores data for a single infoset object
# an infoset represents a state such as "K", "Kp", or "Kpb"
class InfosetData:
    def __init__(self):
        # set each action to have same probability
        self.actions = {action : InfosetActionData(1 / len(ACTIONS)) for action in ACTIONS}

        self.beliefs: dict[str, float] = {}
        self.expected_utility: float = None

        # prob of reaching this infoset
        self.likelihood: float = None

    @staticmethod
    def printInfoSetDataTable(infoSets):
        # print the various values for the infoSets in a nicely formatted table
        rows=[]
        for infoSetStr in sorted_infoset_strs:
            infoSet = infoSets[infoSetStr]
            row=[infoSetStr,*infoSet.getStrategyTableData(),infoSetStr,*infoSet.getBeliefTableData(),infoSetStr,*infoSet.getUtilityTableData(),f'{infoSet.expected_utility:.2f}',f'{infoSet.likelihood:.2f}',infoSetStr,*infoSet.getGainTableData()]
            rows.append(row)
        
        headers = ["InfoSet","Strat:Bet", "Strat:Pass", "---","Belief:H", "Belief:L", "---","Util:Bet","Util:Pass","ExpectedUtil","Likelihood","---","TotGain:Bet","TotGain:Pass"]

        # in case you don't want to create a venv to install the tabulate package, this code will work without it. 

        print(tabulate(rows, headers=headers,tablefmt="pretty",stralign="left"))


    def getStrategyTableData(self):
        return [f'{self.actions[action].strategy:.2f}' for action in ACTIONS]
    
    def getUtilityTableData(self):
        return [f'{self.actions[action].utility:.2f}' for action in ACTIONS]
    
    def getGainTableData(self):
        return [f'{self.actions[action].cumulative_gain:.2f}' for action in ACTIONS]
    
    def getBeliefTableData(self):
        return [f'{self.beliefs[oppPocket]:.2f}' for oppPocket in self.beliefs.keys()]

class InfosetActionData:
    def __init__(self, initial_strat_value):
        self.strategy = initial_strat_value
        self.utility = None
        self.cumulative_gain = initial_strat_value

# select opponent possibilities (removing the card we have)
def get_opponent_possibilities(card):
    return [rank for rank in RANKS if rank != card]

def get_deciding_player(infoset_str):
    return (len(infoset_str) - 1) % 2

def get_parent_infoset_strs(infoset_str):
    # no parents
    if len(infoset_str) == 1:
        return []
    
    infoset_card = infoset_str[0]

    opp_possibilities = get_opponent_possibilities(infoset_card)

    # stop before the last action, head it with the opponent's card
    return [opp_card + infoset_str[1:-1] for opp_card in opp_possibilities]

# given the current infoset and an action, return the resulting opponent infosets (2 possibilities for kuhn)
# for example: "Kp" and action b will return ["Qpb", "Jpb"]
def get_child_infoset_strs(infoset_str, action):
    
    infoset_card = infoset_str[0]
    
    opp_possibilities = get_opponent_possibilities(infoset_card)
    # get current actions (which is 1:)
    action_str = infoset_str[1:] + action

    return [opp_card + action_str for opp_card in opp_possibilities]

def is_player_1_card_higher(player_1_card, player_2_card):
    if player_1_card == 'K':
        return True
    if player_1_card == 'J':
        return False

    if player_2_card == 'K':
        return False
    if player_2_card == 'J':
        return True

# returns the tuple (player_1_utility, player_2_utility) for the terminal node
# this is easy to hardcode for a small gmaes
def calculate_utility_at_terminal_node(player_1_card, player_2_card, action_string):
    # both players check, the one with the higher card wins 1
    if action_string == 'pp':
        if is_player_1_card_higher(player_1_card, player_2_card):
            return (1, -1)
        else:
            return (-1, 1)
    # player 1 folds, player 2 wins the original bet (ante)
    if action_string == 'pbp':
        return (-1, 1)
    # player 2 folds
    if action_string == 'bp':
        return (1, -1)
    # both bet, reward is 2 for the winner
    if action_string == 'bb' or action_string == 'pbb':
        if is_player_1_card_higher(player_1_card, player_2_card):
            return (2, -2)
        else:
            return (-2, 2)
    

def initialize_infosets():
    # generate all possible infosets
    for action_str in INFOSET_ACTION_STRINGS:
        for rank in RANKS:
            infoset_str = rank + action_str
            infosets[infoset_str] = InfosetData()
            sorted_infoset_strs.append(infoset_str)
    pass

def update_beliefs():
    # go through all infosets
    for infoset_str in sorted_infoset_strs:
        infoset = infosets[infoset_str]

        # for the initial infosets (K, Q, J), the opp has a 1/2 chance of having each card we didn't draw
        if len(infoset_str) == 1:
            opp_possibilities = get_opponent_possibilities(infoset_str[0])

            # set each belief to 1/2
            for opp_card in opp_possibilities:
                infoset.beliefs[opp_card] = 1 / len(opp_possibilities)
        
        # in other cases, we want to look at the parents of this infoset
        # the parents of an infoset are the opponent infosets that led to this one
        else:
            parent_infoset_strs = get_parent_infoset_strs(infoset_str)
            
            # check the last action
            last_action = infoset_str[-1]

            total = 0

            '''
            EXAMPLE:
                We have seen the opponent pass 100% of the time with Q, and 50% of the time with J.
                If the opponent passes, we know they have a Q with probability 2 / 3, and a J with probability 1 / 3.
            '''
            # get the total
            for parent_infoset_str in parent_infoset_strs:
                parent_infoset = infosets[parent_infoset_str]
                # total += parent_infoset.likelihood * parent_infoset.actions[last_action]
                total += parent_infoset.actions[last_action].strategy

            # update the beliefs
            for parent_infoset_str in parent_infoset_strs:
                parent_infoset = infosets[parent_infoset_str]
                
                opp_card = parent_infoset_str[0]
                infoset.beliefs[opp_card] = parent_infoset.actions[last_action].strategy / total

def update_utilities_for_infoset_str(infoset_str):
    # check which players POV we are in (based on turn)
    deciding_player = get_deciding_player(infoset_str)

    infoset = infosets[infoset_str]
    beliefs = infoset.beliefs

    # calculate utility for each action
    for action in ACTIONS:
        action_str = infoset_str[1:] + action
        child_infoset_strs = get_child_infoset_strs(infoset_str, action)

        util_from_infosets, util_from_terminal_nodes = 0, 0

        for child_infoset_str in child_infoset_strs:
            # child_infoset = infosets[child_infoset_str[0]]
            opp_card = child_infoset_str[0]
            
            # based on the beliefs what is the probability of getting to this point
            infoset_probability = beliefs[opp_card]

            # store in a list. we will reverse depending on the deciding player
            player_cards = [infoset_str[0], opp_card]

            if deciding_player == 1:
                player_cards = list(reversed(player_cards))
            
            # if this is a terminal action, calculate the utils as such
            if action_str in TERMINAL_ACTION_STRINGS:
                # this calculates the utility based on which player has the higher card
                utils = calculate_utility_at_terminal_node(*player_cards, action_str)

                # multiply by the probability of reaching this terminal node by the util to get expected util
                util_from_terminal_nodes += infoset_probability * utils[deciding_player]

            else:
                # if this is not a terminal action, we want to look at the expected utility of the child infoset
                child_infoset = infosets[child_infoset_str]
                
                for opp_action in ACTIONS:
                    opp_action_probability = child_infoset.actions[opp_action].strategy
                    destination_infoset_str = infoset_str + action + opp_action
                    destination_action_str = destination_infoset_str[1:]

                    if destination_action_str in TERMINAL_ACTION_STRINGS:
                        utils = calculate_utility_at_terminal_node(*player_cards, destination_action_str)

                        # to get the expected utility, we multiply the probability of reaching this infoset by the probability 
                        # of this opponent action by the utility of the terminal node
                        util_from_infosets += infoset_probability * opp_action_probability * utils[deciding_player]
                    
                    else:
                        # we already have the expected utility
                        destination_infoset = infosets[destination_infoset_str]
                        util_from_infosets += infoset_probability * opp_action_probability * destination_infoset.expected_utility
            
        infoset.actions[action].utility = util_from_infosets + util_from_terminal_nodes
    
    # calculate the expected utility
    infoset.expected_utility = 0
    for action in ACTIONS:
        action_data = infoset.actions[action]
        infoset.expected_utility += action_data.strategy * action_data.utility

# calculate the probability of reaching each infoset
def calculate_infoset_likelihoods():
    for infoset_str in sorted_infoset_strs:
        infoset = infosets[infoset_str]

        # reset it each time
        infoset.likelihood = 0
        opp_possibilities = get_opponent_possibilities(infoset_str[0])

        # first card drawn is only determined by chance and uniform
        if len(infoset_str) == 1:
            infoset.likelihood = 1 / len(RANKS)
        # "second tier" infosets
        # the likelihood of these is based on the likelihood of pathing from the parent sets added together
        # if we have a Qb, it can be reached by a parent of K or J (but not Q because no reuse)
        elif len(infoset_str) == 2:
            for opp_card in opp_possibilities:
                opp_infoset = infosets[opp_card + infoset_str[1:-1]]

                # likelihood is strat / ways to reach this TODO: check this
                infoset.likelihood += opp_infoset.actions[infoset_str[-1]].strategy / (len(RANKS) * len(opp_possibilities))
        
        # "third tier" and beyond
        # we want to check two levels up because that was our last card. we want to do it from the POV of the same player
        else:
            for opp_card in opp_possibilities:
                opp_infoset = infosets[opp_card + infoset_str[1:-1]]

                infoset_skip = infosets[infoset_str[:-2]]
                parent_likelihood = infoset_skip.likelihood / len(opp_possibilities)
                infoset.likelihood += parent_likelihood * opp_infoset.actions[infoset_str[-1]].strategy

# calculate the gains for each infoset
def calculate_gains():
    total_gain = 0

    for infoset_str in sorted_infoset_strs:
        infoset = infosets[infoset_str]

        for action in ACTIONS:
            util_for_action = infoset.actions[action].utility
            # cap gain at 0
            gain = max(0, util_for_action - infoset.expected_utility)
            total_gain += gain
            
            # multiply gain by likelihood
            infoset.actions[action].cumulative_gain += gain * infoset.likelihood
    return total_gain

def update_strategy():
    for infoset_str in sorted_infoset_strs:
        infoset = infosets[infoset_str]

        # get gains for each action
        gains = [infoset.actions[action].cumulative_gain for action in ACTIONS]

        total_gains = sum(gains)

        for action in ACTIONS:
            gain = infoset.actions[action].cumulative_gain

            # adjust it by proportion of total gains
            infoset.actions[action].strategy = gain / total_gains

infosets: dict[str, InfosetData] = {}

# sort this based on length. this allows us to traverse from the "top" of the or from the "bottom"
sorted_infoset_strs: list[str] = []

if __name__ == "__main__":
    initialize_infosets()

    iterations = 300000

    total_gains = []

    # only plot the gain from every xth iteration (in order to lessen the amount of data that needs to be plotted)
    numGainsToPlot=100 
    gainGrpSize = iterations//numGainsToPlot 
    if gainGrpSize==0:
       gainGrpSize=1

    for i in range(iterations):
        update_beliefs()

        # update our utilities in reverse order to simulate a bottom up traversal
        for infoset_str in reversed(sorted_infoset_strs):
            update_utilities_for_infoset_str(infoset_str)
        
        calculate_infoset_likelihoods()

        total_gain = calculate_gains()

        if i%gainGrpSize==0: # every 10 or 100 or x rounds, save off the gain so we can plot it afterwards and visually see convergence
            total_gains.append(total_gain)
            print(f'TOT_GAIN {total_gain: .3f}')     

        update_strategy()

    InfosetData.printInfoSetDataTable(infosets)


    print(f'Plotting {len(total_gains)} totGains')
    # Generate random x, y coordinates
    x = [x*gainGrpSize for x in range(len(total_gains))]
    y = total_gains

    # Create scatter plot
    plt.scatter(x, y)

    # Set title and labels
    plt.title('Total Gain per iteration')
    plt.xlabel(f'Iteration # ')
    plt.ylabel('Total Gain In Round')

    # Display the plot
    plt.show()

