from cohere import Tool
import requests
import os
import time
import json
from crewai import Agent, Task, Crew, Process, LLM
from langchain.llms.openai import OpenAI
from crewai_tools import ScrapeWebsiteTool
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import litellm
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type
import urllib.parse

load_dotenv()

# Set up the Ali Baba Model
llm = LLM(model="ollama/qwen2.5:latest", base_url="http://localhost:11434")

os.environ["SERPER_API_KEY"] = "3cb6b8eabfba4c284b11dfe3e2e694d61c2de09a"
os.environ['LITELLM_LOG'] = 'DEBUG'


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
        # Implement the search logic here
        # url encode the query
        query = urllib.parse.quote(query, safe='+')
        url = f"https://google.serper.dev/search?q={query}&num={num_results}&page={page}&apiKey={self.api_key}"

        headers = {
            "X-API-KEY": self.api_key
        }

        params = {
        }

        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            results = response.json()
            return results
        else:
            return f"Error: {response.status_code} - {response.text}"


search_tool = SerperSearchTool(api_key=os.getenv("SERPER_API_KEY"))

### --- AGENTS --- ###

# Search Agent: Uses SERPAPI to get results
search_agent = Agent(
    role="Search Specialist",
    goal="Find relevant pages from {website} containing emails related to {profession}",
    backstory="An expert in searching the web and retrieving relevant data from Google.",
    verbose=True,
    memory=True,
    llm=llm,
    tools=[search_tool]
)

# Data Extraction Agent: Extracts name, business, email, and links
extraction_agent = Agent(
    role="Data Extraction Specialist",
    goal="Extract name, business, email, and links from search results",
    backstory="A meticulous analyst who ensures no relevant information is lost.",
    verbose=True,
    llm=llm,
    memory=True
)

# JSON Writer Agent: Saves extracted data into a JSON file
json_writer_agent = Agent(
    role="JSON Data Writer",
    goal="Save extracted data into an organized JSON file",
    backstory="A detail-oriented data recorder who ensures proper documentation.",
    verbose=True,
    llm=llm,
    memory=True
)

### --- TASKS --- ###

# Task 1: Perform Google search using SERPAPI
search_task = Task(
    description=(
        "Use Google search to find pages on {website} containing emails related to {profession}. "
        "Query should be: site:{website} “{profession}” “@gmail.com” OR “@yahoo.com” OR “@hotmail.com” "
        "OR “@outlook.com” OR “@aol.com” OR “@yahoo.com”. "
        "Retrieve multiple pages (each containing 100 results)."
    ),
    expected_output="A list of search result pages containing potential leads.",
    tools=[search_tool],
    agent=search_agent
)

# Task 2: Extract relevant data from search results
extraction_task = Task(
    description=(
        "Extract key details from search results: name, business, email, and link. "
        "Ensure accuracy and completeness in data extraction."
    ),
    expected_output="A structured list of extracted contacts with name, business, email, and links.",
    agent=extraction_agent
)

# Task 3: Save extracted data into a JSON file


def save_to_json(data):
    # Ensure 'data' is a list and contains only structured contact details
    cleaned_string = data.raw.strip('```json\n').strip('```')
    new_data = json.loads(cleaned_string)

    output_file = "extracted_contacts.json"

    # Check if the file exists
    if os.path.exists(output_file):
        # Read the existing data
        with open(output_file, "r", encoding="utf-8") as json_file:
            existing_data = json.load(json_file)
    else:
        existing_data = []

    # Append the new data to the existing data
    if isinstance(existing_data, list):
        existing_data.extend(new_data)
    else:
        existing_data = new_data

    # Write the updated data back to the file
    with open(output_file, "w", encoding="utf-8") as json_file:
        json.dump(existing_data, json_file, indent=4)

    return f"Data appended successfully in {output_file}"


json_writer_task = Task(
    description=(
        "Take extracted data and save it into a JSON file named 'extracted_contacts.json'. "
        "Ensure the file is properly formatted with fields for Name, Business, Email, and Link."
    ),
    expected_output="A JSON file containing structured contact details.",
    agent=json_writer_agent,
    callback=save_to_json
)

### --- CREW FORMATION --- ###
crew = Crew(
    agents=[search_agent, extraction_agent, json_writer_agent],
    tasks=[search_task, extraction_task, json_writer_task],
    process=Process.sequential
)

# Start execution
if __name__ == "__main__":
    profession = input("Enter profession: ")
    website = input("Enter website (e.g., linkedin.com): ")

    # query = f'site:{website} “{profession}” “@gmail.com” OR “@yahoo.com” OR “@hotmail.com” OR “@outlook.com” OR “@aol.com” OR “@yahoo.com”'
    # response = search_tool.run(
    #    query=query,
    #    num_results=100
    # )

    # print(response)
    result = crew.kickoff(
        inputs={"profession": profession, "website": website})
    print(result)
