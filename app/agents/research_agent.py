import asyncio
from dataclasses import dataclass
import re
from typing import Union
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
import uuid
from urllib.parse import urljoin, urlparse, urlunparse
import hashlib
from pydantic_ai.models.gemini import GeminiModel
import htmlmin

load_dotenv()
logfire.configure()
model = GeminiModel(os.getenv("LLM_MODEL"))  # OllamaModel("qwen2.5:latest")
work_folder = "works/research_agent"


class Link(BaseModel):
    href: str
    text: str


class SearchResponse(BaseModel):
    text_response: str = Field(default_factory=str)
    links: list[Link] = Field(default_factory=list)


research_agent = Agent(
    model,
    name="research_agent",
    deps_type=str,
    result_type=SearchResponse,
    system_prompt=(
        """
        You are a research agent.
        1. Load a web page using the tool `load_page` for the given url.
        2. Construct a query and use the tool `search_text_in_page` to search for the query in the web page.
        3. If nothing is found, use the tool `get_page_links` to get all URLs from the page. Respond back to the user with the list.
        """
    )
)


@research_agent.tool
def load_page(ctx: RunContext[str], url: str) -> str:
    """
    Fetches the web page given by the `url` and returns the contents.

    """

    logfire.info(f"Loading page: {url}")

    page_folder = sanitized_url = re.sub(
        r'[^a-zA-Z0-9]', '_', re.sub(r'^https?://', '', url))
    os.makedirs(f"{work_folder}/{page_folder}", exist_ok=True)
    file_path = f"{work_folder}/{page_folder}/data.html"

    if not os.path.exists(file_path):
        content = ""
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

        # Minify the HTML content
        minified_content = htmlmin.minify(
            content, remove_comments=True, remove_empty_space=True)

        # Save the minified HTML content to a file in the folder
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(minified_content)

    return f"The web contents are loaded and stored in a file as BeautifulSoup data. You can use the page ID as `{page_folder}` to fetch specific details about this web page using the tool `get_page_element_details` for further processing."


@research_agent.tool
def get_page_links(ctx: RunContext[str], id: str) -> list[Link]:
    """
    Fetches all the links from the web page given by the `id`.

    Args:

        - id: str: The unique identifier of the web page.

    Returns:

        - str: The string representation of the links found in the web page.
    """

    file_path = f"{work_folder}/{id}/data.html"

    if not os.path.exists(file_path):
        return "The page is not loaded. Please load the page first."

    with open(file_path, "r", encoding="utf-8") as file:
        soup = BeautifulSoup(file, 'html.parser')

    links = [Link(href=a.get('href'), text=a.get_text(strip=True))
             for a in soup.find_all('a', href=True) if not a.get('href').startswith('../')]

    # [{'href': a.get('href'), 'text': a.get_text(strip=True)}
    # for a in soup.find_all('a', href=True)]

    print("links >> " + str(links))

    # "Pick a few links from the list that may contain the required information and respond back to user. " + str(links)
    return links


@research_agent.tool
def search_text_in_page(ctx: RunContext[str], id: str, query: str) -> bool:
    """
    Searches for the given query in the web page and returns true if found.

    Args:
        - id: str: The unique identifier of the web page.
        - query: str: The text query to search for.

    Returns:
        - bool: It return if the query is found in the page or not.
    """

    logfire.info(f"Searching for text: {query}")

    file_path = f"{work_folder}/{id}/data.html"

    if not os.path.exists(file_path):
        return "The page is not loaded. Please load the page first."

    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    soup = BeautifulSoup(content, 'html.parser')

    links = "\n".join([a.get('href') + " " + a.get_text(strip=True)
                      for a in soup.find_all('a', href=True)])

    # Search for the query in the text content
    text = content + links
    pattern = re.compile(re.escape(query), re.IGNORECASE)
    matches = pattern.finditer(text)

    return bool(matches)


async def main():
    result = None

    query = "Can you find all the categories of the books on https://toscrape.com?"

    while result is None or result.data.text_response == "":

        try:
            result = await research_agent.run(query, message_history=result.all_messages() if result else None)
            if result.data.text_response == "":
                query = "try " + result.data.links[0].href
                print("query >> " + query)
        except Exception as e:
            continue

    print(result)


asyncio.run(main())
