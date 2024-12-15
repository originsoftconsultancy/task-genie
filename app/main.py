
from app.agents.fetch_web_agent import *
import asyncio
import logfire

logfire.configure()


async def main():

    query = ""

    while (query != "bye"):
        query = input("User: ")
        if query != "bye":
            result = await fetch_web_agent.run(query, deps=None)
            content = result.data if hasattr(result, 'data') else str(result)
            print("Agent: " + content)

asyncio.run(main())
