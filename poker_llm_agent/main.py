from dotenv import load_dotenv
import os
import pandas as pd
# from llama_index.tools import QueryEngineTool, ToolMetadata
# from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.tools.query_engine import QueryEngineTool
from llama_index.core.tools.types import ToolMetadata
from llama_index.core.tools.query_plan import QueryPlanTool

from llama_index.core import get_response_synthesizer

from llama_index.core.agent import ReActAgent
from llama_index.llms.openai import OpenAI
from pdf_engine import poker_engine
from preflop_engine import preflop_engine
from postflop_engine import postflop_engine
from hand_engine import hand_engine


load_dotenv()

# print("hello world")

# tools
# hand matcher
# preflop strategy
# postflop strategy
# bet calculator

# tool based planning
# final decision making engine

tools = [
    # QueryEngineTool(
    #     query_engine=poker_engine,
    #     metadata=ToolMetadata(
    #         name="poker_strategy",
    #         description="this gives detailed information about poker strategy",
    #     ),
    # ),
    QueryEngineTool(
        query_engine=preflop_engine,
        metadata=ToolMetadata(
            name="preflop_strategy",
            description="this provides a strategy about how to play the game preflop",
        ),
    ),
    QueryEngineTool(
        query_engine=hand_engine,
        metadata=ToolMetadata(
            name="hand_guide",
            description="Provide this tool with your hole cards and community cards to determine the best hand that can be made",
        ),
    ),
    QueryEngineTool(
        query_engine=postflop_engine,
        metadata=ToolMetadata(
            name="postflop_strategy",
            description="this provides a strategy about how to play the game postflop",
        ),
    ),
]

# print(hand_engine.get_prompts())

context = """Purpose: You are an agent designed to be a professional poker player. You will be given information about 
            your hole cards, as well as the public game state including community cards. Start by evaluating what hand you have, and then use the tools to determine the strategy. Be sure to take your opponents actions into account as well.
            Return your answer as the valid move you choose to make in order to maximize the amount of money you earn. """
# context = """Purpose: The primary role of this agent is to assist users by providing accurate 
#             information about how to play poker in a way that best allows them to win against their opponents. """

response_synthesizer = get_response_synthesizer()
query_plan_tool = QueryPlanTool.from_defaults(query_engine_tools=tools, response_synthesizer=response_synthesizer)

tools.append(query_plan_tool)

llm = OpenAI(model="gpt-3.5-turbo-0613")
agent = ReActAgent.from_tools(tools, llm=llm, verbose=True, context=context)

# agent = ReActAgent.from_tools([query_plan_tool], llm=llm, verbose=True, context=context)

while (prompt := input("Enter a prompt (q to quit): ")) != "q":
    result = agent.query(prompt)
    print(result)
