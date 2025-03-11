from pydantic import BaseModel, Field
from crewai.tools import BaseTool
from typing import Type
import requests
import urllib.parse
import os
from dotenv import load_dotenv
import re
from tools.data_storage import *

load_dotenv()


class SerperSearchToolInput(BaseModel):
    """Input schema for SerperSearchTool."""
    query: str = Field(...,
                       description="Search query for extracting dentist emails from Instagram.")
    num_results: int = Field(
        100, description="Number of search results to retrieve.")


class SerperSearchTool(BaseTool):
    name: str = "Serper Search Tool"
    description: str = "Fetch search results from Serper API for lead generation."
    args_schema: Type[BaseModel] = SerperSearchToolInput
    api_key: str = Field(..., description="API key for Serper API")

    def __init__(self, **data):
        super().__init__(**data)

    def _run(self, query: str, num_results: int = 100, page: int = 1) -> str:
        """Fetch search results from Serper API for lead generation."""
        query = urllib.parse.quote(query, safe='+')
        url = f"https://google.serper.dev/search?q={query}&num={num_results}&page={page}&apiKey={self.api_key}"

        headers = {
            "X-API-KEY": self.api_key
        }

        params = {}

        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            results = response.json()
            return results
        else:
            return f"Error: {response.status_code} - {response.text}"


search_tool = SerperSearchTool(api_key=os.getenv("SERPER_API_KEY"))


def process_leads(leads, profession: str):

    processed_leads = []

    for lead in leads:
        name = lead["title"]
        link = lead["link"]

        email = None

        if lead["snippet"] is not None:
            email_match = re.search(
                r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", lead["snippet"])
            email = email_match.group(0) if email_match else None

        if email is not None:
            processed_leads.append(
                {"name": name, "email": email, "profession": profession, "link": link})

    return processed_leads


def fetch_leads(profession: str):

    sources = os.getenv("SEARCH_SOURCES").split(",")
    size = os.getenv("SEARCH_PAGE_SIZE")
    leads = []

    for website in sources:
        query = f'site:{website} “{profession}” "Email:" OR “@gmail.com” OR “@yahoo.com” OR “@hotmail.com” OR “@outlook.com” OR “@aol.com” OR “@yahoo.com”'
        page = 1
        done = False
        while not done:
            response = search_tool.run(
                query=query,
                num_results=size,
                page=page
            )

            if (len(response['organic']) > 0):
                leads += response['organic']
                page += 1
            else:
                done = True

    return process_leads(leads, profession)


def insert_leads(leads):

    for lead in leads:
        insert_data(
            table_name="leads",
            columns="name, email, profession, link",
            values=(lead["name"], lead["email"],
                    lead["profession"], lead["link"])
        )
