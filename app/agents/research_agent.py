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
from pydantic_ai.models.ollama import OllamaModel

load_dotenv()
logfire.configure()
model = os.getenv("LLM_MODEL")  # OllamaModel("qwen2.5:latest")
work_folder = "works/research_agent"

research_agent = Agent(
    model,
    name="research_agent",
    deps_type=str,
    result_type=str,
    system_prompt=(
        """
        You are a research agent. 
        Your primary role is to plan and execute research tasks efficiently. Follow these steps:

        1. Break down the main research objective into smaller, manageable sub-tasks, task: {"task": "description of task", "status": "pending"}.
        2. Use the `store_tasks` tool to store the sub-tasks. Ensure each task is clearly defined and actionable.
        3. Use the `get_next_pending_task` tool to retrieve the next pending sub-task in the sequence.
        4. Use the `perform_task` tool to execute the retrieved sub-task and mark it as completed.

        Continue this process until all sub-tasks are completed and the research is successfully accomplished. 
        Always aim to complete tasks systematically and provide concise, clear results for each step.
        Do not run tasks in parallel as they may depend on each other.
        """
    )
)


@research_agent.tool
def store_tasks(ctx: RunContext[str], tasks: str) -> str:
    """
    Stores the tasks in JSON format with a 'pending' flag.
    """
    logfire.info(f"Storing tasks: {tasks}")

    # convert json from string into dict
    json_tasks = json.loads(tasks)

    with open(f"{work_folder}/tasks.json", "w") as f:
        json.dump(json_tasks, f, indent=4)

    logfire.info(f"Tasks stored successfully.")
    return "Tasks created and stored."


@research_agent.tool
def get_next_pending_task(ctx: RunContext[str]) -> str:
    """
    Gets the next pending task from the list of tasks.
    """
    logfire.info(f"Fetching the next pending task...")

    with open(f"{work_folder}/tasks.json", "r") as f:
        tasks = json.load(f)

    for task in tasks:
        if task["status"] == "pending":
            logfire.info(f"Next pending task found: {task['task']}")
            return task["task"]

    logfire.info("No pending tasks found.")
    return "No pending tasks found."


@research_agent.tool
def perform_task(ctx: RunContext[str], task: str) -> str:
    """
    Performs the given task and marks it as completed.
    """
    logfire.info(f"Performing task: {task}")

    with open(f"{work_folder}/tasks.json", "r") as f:
        tasks = json.load(f)

    for t in tasks:
        if t["task"] == task:
            t["status"] = "completed"
            break

    with open(f"{work_folder}/tasks.json", "w") as f:
        json.dump(tasks, f, indent=4)

    logfire.info(f"Task completed: {task}")
    return f"Task completed: {task}"


@research_agent.tool
def load_page(ctx: RunContext[str], url: str) -> str:
    """
    Fetches the web page given by the `url` and returns the contents.

    """

    logfire.info(f"Loading page: {url}")
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

    return content


async def main():

    query = "If I ask you to research on topic like services provided by the company from their complete website https://www.dataicraft.com, can you create tasks and accomplish them ?"
    result = await research_agent.run(query)
    print(result)

asyncio.run(main())
