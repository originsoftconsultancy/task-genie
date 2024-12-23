import asyncio
from dataclasses import dataclass
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

from app.agents.fetch_web_agent import fetch_web_content, fetch_web_content_tool

load_dotenv()

logfire.configure()

model = os.getenv("LLM_MODEL")
api_key = os.getenv("GEMINI_API_KEY")

# Configuration for the SmartScraperGraph
graph_config = {
    "llm": {
        "api_key": api_key,
        "model": "gemini-pro",
    },
}


scrapper_agent = Agent(
    model,
    name="scrapper_agent",
    deps_type=str,
    result_type=str,
    system_prompt=(
        'Use the tool `scrap_from_contents` to scrap json data from the web page given by url from the provided prompt. The tool internally fetches the web page contents as well.'
    ),
)


# @scrapper_agent.tool
def scrap_from_contents(ctx: RunContext[str], url: str, prompt: str) -> str:
    """Scraps information as JSON from the file contents given by the url and a prompt"""

    logfire.info(
        f"Attempting to get information using SmartScraperGraph for the prompt: {prompt} and url: {url}")

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

        # see if the result is a dictionary and first element has value "NA"
        if isinstance(result, dict) and (list(result.values())[0] == "NA" or list(result.values())[0] == []):
            logfire.info("Call the tool `extract_detailed_information` with the url: " + url + " prompt: " +
                         prompt + " and the required boolean parameters to extract the detailed information.")
            return "Call the tool `extract_detailed_information` with the url: " + url + " prompt: " + prompt + " and the required boolean parameters to extract the detailed information."
        else:
            return result

    except Exception as e:
        logfire.error(f"SmartScraperGraph failed: {e}")
        # Signal to the agent to try the alternative tool
        return f"SmartScraperGraph failed: {e}"


@scrapper_agent.tool
def extract_detailed_information(ctx: RunContext[str],
                                 url: str,
                                 prompt: str,
                                 b_title: bool,
                                 b_metadata: bool,
                                 b_headings: bool,
                                 b_paragraphs: bool,
                                 b_links: bool,
                                 b_images: bool,
                                 b_unordered_lists: bool,
                                 b_ordered_lists: bool,
                                 b_tables: bool,
                                 b_scripts: bool,
                                 b_styles: bool,
                                 b_iframes: bool,
                                 b_forms: bool,
                                 b_divs: bool,
                                 b_spans: bool,
                                 b_only_text: bool
                                 ) -> str:
    """
        Pick required information from the html based on boolean parameters. The web page url is in the parameter `url`, prompt is in `prompt`, This tool will return a dictionary containing the following information:
        - 
        - Title of the page if b_title parameter is True
        - Metadata tags (name and content) if b_metadata parameter is True
        - Headings (h1 to h6) if b_headings parameter is True
        - Paragraphs if b_paragraphs parameter is True
        - Links (anchor tags) if b_links parameter is True
        - Images if b_images parameter is True
        - Unordered lists if b_unordered_lists parameter is True
        - Ordered lists if b_ordered_lists parameter is True
        - Tables if b_tables parameter is True
        - Scripts if b_scripts parameter is True
        - Styles if b_styles parameter is True
        - Iframes if b_iframes parameter is True
        - Forms if b_forms parameter is True
        - Divs if b_divs parameter is True
        - Spans if b_spans parameter is True
        - Use the b_only_text as True if you want to extract only the text from the html content
    """
    #
    logfire.info("Extracting detailed information from the web page")
    logfire.info("Parameters: " + str(locals()))

    # Read the HTML content from the file

    html_content = fetch_web_content(ctx, url)

    soup = BeautifulSoup(html_content, 'html.parser')

    if b_only_text:
        return soup.get_text(strip=True)

    # Title
    title = soup.title.string if (soup.title and b_title) else None

    # Metadata
    meta_tags = ({meta.get('name', meta.get('property', '')): meta.get('content', '')
                 for meta in soup.find_all('meta')}) if b_metadata else None

    # Headings
    headings = {
        f'h{i}': [h.get_text(strip=True) for h in soup.find_all(f'h{i}')]
        for i in range(1, 7)
    } if b_headings else None

    # Paragraphs
    paragraphs = [p.get_text(strip=True)
                  for p in soup.find_all('p')] if b_paragraphs else None

    # Links
    links = [{
        'text': a.get_text(strip=True),
        'href': a.get('href', '')
    } for a in soup.find_all('a', href=True)] if b_links else None

    # Images
    images = [{
        'alt': img.get('alt', ''),
        'src': img.get('src', ''),
        'title': img.get('title', '')
    } for img in soup.find_all('img')] if b_images else None

    # Lists
    unordered_lists = [[li.get_text(strip=True) for li in ul.find_all('li')]
                       for ul in soup.find_all('ul')] if b_unordered_lists else None
    ordered_lists = [[li.get_text(strip=True) for li in ol.find_all('li')]
                     for ol in soup.find_all('ol')] if b_ordered_lists else None

    # Tables
    tables = []
    if (b_tables):
        for table in soup.find_all('table'):
            rows = []
            for tr in table.find_all('tr'):
                cells = [td.get_text(strip=True)
                         for td in tr.find_all(['th', 'td'])]
                rows.append(cells)
            tables.append(rows)
    else:
        tables = None

    # Scripts
    scripts = [script.get('src', '') or script.get_text(strip=True)
               for script in soup.find_all('script')] if b_scripts else None

    # Styles
    styles = [style.get_text(strip=True)
              for style in soup.find_all('style')] if b_styles else None

    # Iframes
    iframes = [iframe.get('src', '') for iframe in soup.find_all(
        'iframe')] if b_iframes else None

    # Forms
    forms = [{
        'action': form.get('action', ''),
        'method': form.get('method', ''),
        'inputs': [{
            'name': input_tag.get('name', ''),
            'type': input_tag.get('type', 'text'),
            'value': input_tag.get('value', '')
        } for input_tag in form.find_all('input')]
    } for form in soup.find_all('form')] if b_forms else None

    # Divs and Spans
    divs = [div.get_text(strip=True)
            for div in soup.find_all('div')] if b_divs else None
    spans = [span.get_text(strip=True)
             for span in soup.find_all('span')] if b_spans else None

    # Return the extracted information
    json = {
        "title": title,
        "meta_tags": meta_tags,
        "headings": headings,
        "paragraphs": paragraphs,
        "links": links,
        "images": images,
        "unordered_lists": unordered_lists,
        "ordered_lists": ordered_lists,
        "tables": tables,
        "scripts": scripts,
        "styles": styles,
        "iframes": iframes,
        "forms": forms,
        "divs": divs,
        "spans": spans,
    }

    final_json = str(json)
    return final_json
