import streamlit as st
from poker_agent import PokerAgent, GameState, RoundStage


def __main__():
    st.title("Poker Agent")

    if "game_state" not in st.session_state:
        st.session_state.game_state = GameState()
    
    if "current_game_stage" not in st.session_state:
        st.session_state.current_game_stage = RoundStage.PREFLOP
    
    if "poker_agent" not in st.session_state:
        st.session_state.poker_agent = PokerAgent()
    
    if "logs" not in st.session_state:
        st.session_state.logs = []

    st.subheader("Game State")

    st.button("Refresh Game State")


    with st.expander("Expand"):
        st.write("Actions")
        st.write(st.session_state.game_state.action_history)

        st.write("Hero Cards")
        st.write(st.session_state.game_state.hole_cards)

        st.write("Community Cards")
        st.write(st.session_state.game_state.community_cards)

    st.subheader("Round Stage")
    round_stage = st.selectbox("Round Stage", [stage.name for stage in RoundStage])
    st.session_state.current_game_stage = round_stage

    hero_cards = st.text_input("Hero Cards. Ex: AhKs")
    st.session_state.game_state.hole_cards = hero_cards

    community_cards = st.text_input("Community Cards. Ex: 2h3h4h5h6h")
    st.session_state.game_state.community_cards = community_cards

    st.subheader("Possible Actions")
    actions = ["Check", "Fold", "Call", "Raise"]
    action_bools = [st.checkbox(action) for action in actions]

    possible_actions = [action for action, action_bool in zip(actions, action_bools) if action_bool]

    if st.session_state.logs:
        for log in st.session_state.logs[::-1]:
            with st.chat_message("assistant"):
                st.write(log)
                
    if st.button("Get Agent Response"):
        with st.spinner("Getting Agent Response..."):
            print("Game State")
            print(st.session_state.game_state)

            response = st.session_state.poker_agent.get_gamestate_analysis(st.session_state.game_state, actions = possible_actions)
            print(response.choices[0].message.content)
            with st.chat_message("assistant"):
                st.write(response.choices[0].message.content)
                st.session_state.logs.append(response.choices[0].message.content)
    


    with st.sidebar:
        st.subheader("Submit Action")

        player = st.text_input("Player")
        action = st.selectbox("Action", ["Check", "Fold", "Call", "Raise"])
        amount = st.number_input("Amount", value=0)

        if st.button("Submit"):
            st.session_state.game_state.action_history.append({
                "round": round_stage,
                "player": player,
                "action": action,
                "amount": amount
            })


if __name__ == "__main__":
    __main__()