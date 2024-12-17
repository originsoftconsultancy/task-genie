from dataclasses import dataclass
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from scrapegraphai.graphs import SmartScraperGraph
from scrapegraphai.utils import prettify_exec_info
import json
from dotenv import load_dotenv
import logfire
import os
import uuid
import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

load_dotenv()

logfire.configure()

model = os.getenv("LLM_MODEL")

fetch_web_agent = Agent(
    model,
    deps_type=str,
    result_type=str,
    system_prompt=(
        'Fetch the contents of a provided web page using the tool `fetch_web_content` for the provided URL, please extract url from the user prompt. '
    ),
)


@fetch_web_agent.tool
def fetch_web_content(ctx: RunContext[str], url: str) -> str:
    """Fetch the contents of a provided web page for the provided URL"""
    logfire.info(
        f"Attempting to fetch content from URL: {url} using Playwright")

    try:
        with sync_playwright() as p:
            # Launch the browser in headless mode
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            # Navigate to the URL
            page.goto(url)

            # Wait for the page to fully load
            page.wait_for_load_state("networkidle")

            # Get the rendered HTML
            content = page.content()
            browser.close()

            logfire.info(
                f"Successfully fetched content from URL: {url} using Playwright")

            return content
    except Exception as e:
        logfire.error(f"Error fetching the web page with Playwright: {e}")
        return f"Error fetching the web page: {e}"


async def fetch_web_content_tool(ctx: RunContext[str], prompt: str) -> str:
    """
    This tool is used to delegate the task of fetching web content to the `fetch_web_agent` for the external websites or specific files online.
    This tool gets the content from the `fetch_web_agent` and saves it to a file in the cache directory and returns the file path.
    The other tools and agents will use this file path to read the contents. 
    params:
    - ctx: RunContext[str]: The context of the run
    - prompt: str, prompt to fetch web content, it contain the URL of the website
    """

    response = await fetch_web_agent.run(prompt)
    contents = response._all_messages[3].content

    logfire.info(f"Received data from the fetch_web_agent")

    cache_dir = os.path.join(os.path.dirname(__file__), 'cache')
    os.makedirs(cache_dir, exist_ok=True)

    # Create a unique file name in the cache directory
    file_name = os.path.join(cache_dir, f"{uuid.uuid4()}.html")

    with open(file_name, "w", encoding="utf-8") as file:
        file.write(contents)

    return file_name
