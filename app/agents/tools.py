import logfire
from pydantic_ai import Agent, RunContext
import uuid
from app.agents.fetch_web_agent import fetch_web_agent
from app.agents.scrapper_agent import scrapper_agent
import os

logfire.configure()


async def scrap_from_contents_tool(ctx: RunContext[str], prompt: str) -> dict:
    """
    This tool is used to delegate the task to `scrapper_agent` to scrap data for the provided user `prompt`. 

    params:
    - ctx: RunContext[str]: The context of the run
    - file_path: str: The path to the local file that contains the html contents
    - prompt: str: The prompt to be used for scrapping
    """
    logfire.info(
        f"Attempting to call the scrapper_agent for scrapping the contents as JSON, prompt: " + prompt)

    try:
        response = await scrapper_agent.run(prompt)
        logfire.info(f"Received data from the scrapper_agent")
        return response.data
    except Exception as e:
        logfire.error(f"Error calling the scrapper_agent: {e}")
        return f"Error calling the scrapper_agent: {e}"
