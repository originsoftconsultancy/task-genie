from pydantic_ai import Tool
import logfire
from pydantic_ai import Agent, RunContext
import uuid
from app.agents.fetch_web_agent import fetch_web_agent
from app.agents.scrapper_agent import scrapper_agent
from app.agents.research_agent import research_agent
import os

logfire.configure()


async def research_tool(ctx: RunContext[str], prompt: str) -> str:
    """
    This tool is used to delegate the task to `research_agent` to research the provided user `prompt`
    This tool can download a web page from url and can process the data.
    params:
    - ctx: RunContext[str]: The context of the run
    - prompt: str: The prompt to be used for research
    """

    logfire.info(
        f"Attempting to call the research_agent for research, prompt: " + prompt)

    try:
        response = await research_agent.run(prompt)
        logfire.info(f"Received data from the research_agent")
        return response.data
    except Exception as e:
        logfire.error(f"Error calling the research_agent: {e}")
        return f"Error calling the research_agent: {e}"


async def scrap_from_contents_tool(ctx: RunContext[str], prompt: str) -> dict:
    """
    This tool is used to delegate the task to `scrapper_agent` to fetch and scrap data for the provided user `prompt`. 
    Please notice that this tool can download the webpage contents and then scrap the data from it.
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
