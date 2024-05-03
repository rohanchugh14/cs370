from enum import Enum
import openai

class RoundStage(Enum):
    PREFLOP = 0
    FLOP = 1
    TURN = 2
    RIVER = 3
    SHOWDOWN = 4

class GameState:
    def __init__(self):
        self.round_state = RoundStage.PREFLOP

        self.community_cards = []

        self.hole_cards = []
        
        self.dealer_position = 0

        # store each action as {"round": "preflop",  "player": "player1", "action": "call", "amount": 10}
        self.action_history = []

        self.player_classification = {"player2": "Tight-Passive (The Rock)", "player3": "Loose-Passive (Calling Station)"}
    
    def __str__(self) -> str:
        return f"Round State: {self.round_state}, Community Cards: {self.community_cards}, Hole Cards: {self.hole_cards}, Action History: {self.action_history}"

    # def update_action_history(self, action):
    #     self.action_history.append(action)


class HeroState:
    def __init__(self):
        self.hero_round_actions_history = []
        self.hero_strategy_history = []
        self.hero_tactics_history = []

        self.hero_position

class PokerAgent:
    def __init__(self):
        self.game_state = GameState()
        self.client = openai.OpenAI()
    
    def get_gamestate_prompt(self, game_state):
        gamestate_prompt = f"""
                        #Texas Holdem (No-Limit, Cash game) Poker data:

                        Current Round: {self.game_state.round_state}
                        
                        Previous Actions:
                        '''
                        {game_state.action_history}
                        '''

                        Hero Hole Cards:
                        {game_state.hole_cards}

                        Community Cards:
                        {game_state.community_cards}

                        Player Classification:
                        {game_state.player_classification}
                        

                        Heros Players Turn:
                        '''
                        """

        return gamestate_prompt


    def get_gamestate_analysis(self, game_state, actions):
            gamestate_prompt = self.get_gamestate_prompt(game_state)

            response = self.client.chat.completions.create(
                model=  "gpt-4-1106-preview",
                #model=  "gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": f"""
                        You are Hero player. Your player name is denoted as player1. Other players will be denoted as player2, player3, player4, player5, player6.
                        Your objective is to analyze real-time online poker data from a 6-max Online Texas Holdem (No Limit, Cash game) and suggest the next action for the hero.

                        {actions}
                     
                        --------------------------

                        #HARD RULES(follow STRICTLY!):

                        - ACTIONS: strictly make decisions based on #Available Actions.

                        - STRATEGY: 
                        1. Focus on dynamic and unpredictable Exploitative poker strategies, mixed with occational (Game Theory Optimied) GTO plays.

                        - ALL-IN: 
                        1. Allowed Pre-flop with premium hands if we are likely to steal blinds.
                        2. When Hero have been Folding a lot Pre-Flop recently and the opponents are likely to fold. 

                        - RAISING: DO NOT raise on the Turn/River when Heros cards don't connect to the board, especially against tight players.

                        - UNPREDICTABILITY: 
                        1. Always keep opponents guessing by mixing actions between calling, checking, betting and raising, based on the history of Hero actions(if available). 
                        2. If you recently folded, bet or check instead. If you recently raised, check instead. Occationally bet/raise with weak cards to confuse opponents.
                        3. Mix up strategy based on history of strategies to confuse, deceive and exploit opponents.
                        4. Mix up tactics based on history of tactics to confuse, deceive and exploit opponents.
                        5. Vary bet sizing based on history of bet/raising values to confuse, deceive and exploit opponents.

                        --------------------------

                        #GENERAL GUIDELINES(follow depending on the context)
                        
                        - RANGE CONSIDERATION: Be aware of possible ranges of opponents when deciding to bet or raise.

                        - POSITIONAL AWARENESS: Be more aggressive in late positions with strong hands, especially in short-handed situations. Ensure your aggression is calculated and not just based on position.

                        - CHECKING: Occationally Check/Call with strong hands to let other players build the pot and disquise our strong hand.

                        - POT CONTROL: Focus on controlling the pot size to manage risk, especially with marginal hands in late positions(turn, river).

                        - FOLDING: Fold when the odds are against you, especially in response to strong bets from conservative/tight players(that play mostly strong/premium hands).

                        - RAISE AMOUNTS: Adjust your pre-flop raise amounts based on the stakes, action history, number of limpers, your position and any other relevant data. 

                        - BET SIZING: Focus on optimizing bet sizes to maximize value from weaker hands and protect against draws. 

                        - BANKROLL MANAGEMENT: Monitor and manage your stack size, adapting your bet sizing and risk-taking accordingly.

                        - BLUFFING VS VALUE BETTING> Strategically balance bluffing with value betting while considering opponents actions, ranges and tendencies.

                        # Use the following 'strategy'-s:
                        - GTO
                        - Exploit
                        - Mixed
                     
                        # Use the following 'tactic'-s: 
                        - Semi-Bluff
                        - Bluff
                        - Probe Bet
                        - Value Bet
                        - Check-Raise
                        - Exploit
                        - Weak Hand
                        - None

                        OUTPUT JSON FORMAT:
                        {
                            {
                                "strategy": "string",
                                "tactic": "string",
                                "explanation": "Provide short and concise instructions of the strategy and tactics for the next hands.",
                                "action": "string",
                                "amount": "number"
                            }
                        }
                    """},
                    {"role": "user", "content": gamestate_prompt}
                ], 
               
                temperature         = 0.2,
                max_tokens          = 300,
                top_p               = 0.95,
                frequency_penalty   = 0,
                presence_penalty    = 0,
                response_format     = {"type": "json_object"}
            )
            return response