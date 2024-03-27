import numpy as np
import os

from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory



load_dotenv()

# prompt = ChatPromptTemplate.from_messages([
#     ("system", 
#     'You are now a program designed to play a version of Texas Limit Holdem against a single human player. You will be provided the current game state, including what your cards are, as well as revealed community cards.\n\
#     You are denoted as player 0. Cards will be denoted by the first letter of the suit followed by the rank.\n\
#     Based on the following information, respond exactly with only with the 0-based index corresponding with the legal action you choose from the list and a brief explanation separated by a ":". For example: "0:I have a good hand and would like to get more value".'),
#     ("user", "{input}")
# ])
prompt = ChatPromptTemplate.from_messages([
    ("system", 
    'You are now a program designed to play a version of Texas Limit Holdem against a single human player. You will be provided the current game state, including what your cards are, the revealed community cards, and previous actions taken\n\
    You are denoted as player 1.\n\
    Based on the following information, respond exactly with only the legal action you choose from the list and a brief explanation separated by a ":". For example: "raise:I have a good hand and would like to get more value".'),
    MessagesPlaceholder(variable_name="chat_history"),
    ("user", "{input}")
])

# map the capital letter of the suit to the suit name
suit_map = {
    'C': 'Clubs',
    'D': 'Diamonds',
    'H': 'Hearts',
    'S': 'Spades'
}

# map the rank to the rank name
rank_map = {
    '2': 'Two',
    '3': 'Three',
    '4': 'Four',
    '5': 'Five',
    '6': 'Six',
    '7': 'Seven',
    '8': 'Eight',
    '9': 'Nine',
    'T': 'Ten',
    'J': 'Jack',
    'Q': 'Queen',
    'K': 'King',
    'A': 'Ace'
}

def interpret_card(card):
    ''' Interpret the card into a human readable format

    Args:
        card (str): The card to be interpreted

    Returns:
        interpreted_card (str): The human readable format of the card
    '''
    return f"{rank_map[card[1]]} of {suit_map[card[0]]}"

class GptAgent(object):
    ''' A random agent. Random agents is for running toy examples on the card games
    '''

    def __init__(self, num_actions):
        ''' Initilize the random agent

        Args:
            num_actions (int): The size of the ouput action space
        '''
        print("initializing gpt agent")
        self.use_raw = True
        self.num_actions = num_actions

        # langchain setup
        self.llm = ChatOpenAI(openai_api_key=os.getenv("OPENAI_API_KEY"))

        self.chat_memory = ChatMessageHistory()

        self.chain = prompt | self.llm
        self.history_chain = RunnableWithMessageHistory(
            self.chain,
            lambda session_id: self.chat_memory,
            input_messages_key="input",
            history_messages_key="chat_history"
        )

    def step(self, state):
        ''' Predict the action given the curent state in gerenerating training data.

        Args:
            state (dict): An dictionary that represents the current state

        Returns:
            action (int): The action predicted (randomly chosen) by the random agent
        '''

        print("stepping")

        # pass data into gpt
        result = self.gpt_calculate(state)

        # reformat into choice
        action, reasoning = result.split(":")

        print("action", action)
        print("reasoning", reasoning)

        # if action.isdigit() and int(action) >= 0 and int(action) < len(state['legal_actions']):
        if action in state['raw_legal_actions']:
            print("gpt choosing action", action)
            return action
            # print("gpt choosing action,", state['raw_legal_actions'][int(action)])
            # return state['raw_legal_actions'][int(action)]
            # return int(action)
        else:
            print("INVALID ACTION by GPT, choosing random")
            # return np.random.choice(list(state['legal_actions'].keys()))
            return np.random.choice(state['raw_legal_actions'])

    def gpt_calculate(self, state):
        print("state legal actions", state['legal_actions'])
        print("state raw legal actions", state['raw_legal_actions'])
        rstate = state['raw_obs']

        # convert hand into a words
        hand = rstate['hand']
        interpreted_hand = [
            interpret_card(card) for card in hand
        ]

        public_cards = rstate['public_cards']
        interpreted_public_cards = [
            interpret_card(card) for card in public_cards
        ]


        # print("hand=", rstate['hand'])
        # print("public cards=", rstate['public_cards'])
        # print("action record=", state['action_record'])
        # print("legal actions=", state['raw_legal_actions'])
        state_string = f"hand= {interpreted_hand}\n" \
                  f"public cards= {interpreted_public_cards}\n" \
                  f"action record= {state['action_record']}\n" \
                  f"legal actions= {rstate['legal_actions']}"
        
        print("state_string", state_string)

        # result = self.chain.invoke({"input": state_string})
        result = self.history_chain.invoke({"input": state_string}, {"configurable": {"session_id": "unused"}},)
        
        print("result")
        print(result)
        print("-----\n")
        return result.content

    def eval_step(self, state):
        ''' Predict the action given the current state for evaluation.
            Since the random agents are not trained. This function is equivalent to step function

        Args:
            state (dict): An dictionary that represents the current state

        Returns:
            action (int): The action predicted (randomly chosen) by the random agent
            probs (list): The list of action probabilities
        '''
        print("evaluating step")


        # print("state", rstate)



        probs = [0 for _ in range(self.num_actions)]
        for i in state['legal_actions']:
            probs[i] = 1/len(state['legal_actions'])

        info = {}
        info['probs'] = {state['raw_legal_actions'][i]: probs[list(state['legal_actions'].keys())[i]] for i in range(len(state['legal_actions']))}

        return self.step(state), info
