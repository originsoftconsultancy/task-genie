from pydantic_ai import Agent, RunContext, Tool
from dotenv import load_dotenv
import os
import logfire

import app.agents._tools

# Load environment variables
load_dotenv()
logfire.configure()

# LLM Model
model = os.getenv("LLM_MODEL")

# Orchestrator Task-Genie Agent
task_genie = Agent(
    name="task_genie",
    model=model,
    system_prompt=(
        "You are an orchestrator agent. Your job is to analyze user input and route it to the appropriate agent. "
        "Your job is to get the overall task done using the provided tools and agents. "
        "You should summarize what you have done with all the tools and agents and return a string response. "
    ),
    deps_type=str,
    result_type=str,
    tools=[
        agents._tools.research_tool
    ]
)
