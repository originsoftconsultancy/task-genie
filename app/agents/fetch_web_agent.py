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
from bs4 import BeautifulSoup
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
        'Fetch the contents of a provided web page using the tool `fetch_web_content` for the provided URL'
    ),
)


@fetch_web_agent.tool
def fetch_web_content(ctx: RunContext[str], url: str) -> str:
    """Fallback tool to fetch and return dynamically rendered HTML content of a web page. This tool uses Playwright to fetch the content."""
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
