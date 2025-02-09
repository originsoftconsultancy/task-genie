import os
from crewai import Agent, Task, Crew, Process, LLM
from langchain.llms.openai import OpenAI
from crewai_tools import ScrapeWebsiteTool
import litellm

# Set up the Ali Baba Model
llm = LLM(
    model="gemini/gemini-1.5-pro-latest",
    temperature=0.7,
    api_key=os.getenv("GEMINI_API_KEY"),
    max_rpm=2,
)

os.environ['LITELLM_LOG'] = 'DEBUG'

scrape_tool = ScrapeWebsiteTool()

# Web Scraper Agent
scraper_agent = Agent(
    role="Web Scraper",
    goal="Extract information about Digital Workers from the website.",
    backstory="You are an expert web scraper who efficiently extracts structured data from web pages.",
    tools=[scrape_tool],
    llm=llm,  # Using Ali Baba model
    verbose=True
)

# Comparison Analyst Agent
analyst_agent = Agent(
    role="AI Comparison Analyst",
    goal="Compare different Digital Workers and analyze their strengths, weaknesses, and best use cases.",
    backstory="You specialize in analyzing AI-powered agents, identifying trends, and evaluating their efficiency in various industries.",
    llm=llm,  # Using Ali Baba model
    verbose=True
)

# Business Strategist Agent
strategist_agent = Agent(
    role="AI Business Strategist",
    goal="Recommend a new AI agent that fills a market gap and has strong business potential.",
    backstory="You are an expert in AI-driven business models, identifying profitable opportunities in the digital workforce industry.",
    llm=llm,  # Using Ali Baba model
    verbose=True
)

# Task 1: Scrape the website
scrape_task = Task(
    description=(
        "Scrape the website https://aiagentsdirectory.com/landscape. "
        "Extract information about various Digital Workers, including their names, descriptions, and features. "
        "Provide a structured dataset containing this information."
    ),
    expected_output="A structured list of Digital Workers with key details.",
    tools=[scrape_tool],
    agent=scraper_agent
)

# Task 2: Compare Digital Workers
compare_task = Task(
    description=(
        "Analyze the extracted Digital Workers data. "
        "Compare them based on capabilities, industries they serve, and their business impact. "
        "Highlight key trends, strengths, and weaknesses."
    ),
    expected_output="A detailed comparison report of different Digital Workers.",
    agent=analyst_agent
)

# Task 3: Suggest a new AI agent idea
strategy_task = Task(
    description=(
        "Based on the comparison, identify gaps in the market for Digital Workers. "
        "Suggest a new AI agent that could be developed to solve an unmet need. "
        "Provide a business justification for why this new agent would be valuable."
    ),
    expected_output="A new AI agent idea with a business strategy and potential market impact.",
    agent=strategist_agent
)

# Assemble Crew
crew = Crew(
    agents=[scraper_agent, analyst_agent, strategist_agent],
    tasks=[scrape_task, compare_task, strategy_task],
    process=Process.sequential
)

# Kickoff execution
result = crew.kickoff()
print(result)
