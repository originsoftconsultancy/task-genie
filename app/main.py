
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import json
from app.agents.orchestrator_agent import *
import asyncio
import logfire

logfire.configure()


async def main():

    query = ""

    while (query != "bye"):
        query = input("User: ")
        if query != "bye":
            result = await task_genie.run(query)
            content = result.data if hasattr(result, 'data') else str(result)
            print("Agent: " + content)

asyncio.run(main())
