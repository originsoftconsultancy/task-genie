from dataclasses import dataclass
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from scrapegraphai.graphs import SmartScraperGraph
from scrapegraphai.utils import prettify_exec_info
import json
from dotenv import load_dotenv
import logfire
import os
import requests
from playwright.sync_api import sync_playwright

load_dotenv()

logfire.configure()

api_key = os.getenv("GEMINI_API_KEY")
model = os.getenv("LLM_MODEL")

# Configuration for the SmartScraperGraph
graph_config = {
    "llm": {
        "api_key": api_key,
        "model": "gemini-pro",
    },
}

fetch_web_agent = Agent(
    model,
    deps_type=str,
    result_type=str,
    system_prompt=(
        'Use the `fetch_web_content` tool to fetch and return the contents of the web page '
        'based on the URL provided. If unsuccessful (means if the response json contains NA in any key), use the `fetch_web_content_alternative` '
        'tool as a fallback to retrieve the content directly.'
    ),
)


@fetch_web_agent.tool
def fetch_web_content(ctx: RunContext[str], url: str, prompt: str) -> str:
    """Fetch and return the contents of a web page given its URL according to the prompt."""
    logfire.info(
        f"Attempting to fetch content from URL: {url} using SmartScraperGraph")
    try:
        # Create the SmartScraperGraph instance and run it
        smart_scraper_graph = SmartScraperGraph(
            prompt=prompt,
            source=url,
            config=graph_config
        )

        # Execute the scraper and save the results to a JSON file
        result = smart_scraper_graph.run()
        logfire.info(f"SmartScraperGraph result: {result}")
        return result
    except Exception as e:
        logfire.error(f"SmartScraperGraph failed: {e}")
        # Signal to the agent to try the alternative tool
        return f"SmartScraperGraph failed: {e}"


@fetch_web_agent.tool
def fetch_web_content_alternative(ctx: RunContext[str], url: str) -> str:
    """Fallback tool to fetch and return dynamically rendered HTML content of a web page."""
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

            # write contents in an html file
            with open("content.html", "w", encoding="utf-8") as file:
                file.write(content)

            logfire.info(
                f"Successfully fetched content from URL: {url} using Playwright")

            return content
    except Exception as e:
        logfire.error(f"Error fetching the web page with Playwright: {e}")
        return f"Error fetching the web page: {e}"
