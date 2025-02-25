import os
from crewai import Agent, Task, Crew, Process, LLM
from langchain.llms.openai import OpenAI
from crewai_tools import ScrapeWebsiteTool
import litellm
from crewai_tools import SerperDevTool
from dotenv import load_dotenv
from fpdf import FPDF
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

load_dotenv()

# Set up the Ali Baba Model
llm = LLM(
    model="gemini/gemini-1.5-pro-latest",
    temperature=0.7,
    api_key=os.getenv("GEMINI_API_KEY"),
    max_rpm=1,
)

os.environ["SERPER_API_KEY"] = "3cb6b8eabfba4c284b11dfe3e2e694d61c2de09a"
os.environ['LITELLM_LOG'] = 'DEBUG'

# Search tool for online research
search_tool = SerperDevTool()

# 1. Industry Researcher Agent
industry_researcher = Agent(
    role="Industry Researcher",
    goal="Find promising industries and niches for an AI-agent-as-a-service business.",
    verbose=True,
    memory=True,
    llm=llm,
    backstory=(
        "An experienced market researcher with deep insights into emerging trends, "
        "you specialize in identifying promising industries for AI-driven solutions."
    ),
    tools=[search_tool]
)

# 2. Problem Analyst Agent
problem_analyst = Agent(
    role="Problem Analyst",
    goal="Identify key problems and challenges in each promising industry and niche.",
    verbose=True,
    memory=True,
    llm=llm,
    backstory=(
        "A business strategist who understands the biggest challenges within industries. "
        "You analyze pain points and uncover gaps where AI solutions can be implemented."
    ),
    tools=[search_tool]
)

# 3. Report Writer Agent
report_writer = Agent(
    role="Report Writer",
    goal="Compile the research into a well-structured report with insights.",
    verbose=True,
    memory=True,
    llm=llm,
    backstory=(
        "A skilled business analyst and writer who turns raw data into actionable insights. "
        "Your reports are clear, insightful, and strategic."
    )
)

# Task 1: Research industries and niches
industry_research_task = Task(
    description=(
        "Identify at least 10 industries and niches where an AI-agent-as-a-service business could be viable. "
        "Consider emerging markets, growth trends, and AI adoption potential."
    ),
    expected_output="A list of at least 10 industries with descriptions.",
    tools=[search_tool],
    agent=industry_researcher,
)

# Task 2: Analyze problems in each niche
problem_analysis_task = Task(
    description=(
        "For each identified industry, analyze the top 3 key pain points or challenges. "
        "Focus on problems that AI agents can realistically solve."
    ),
    expected_output="A list of key pain points for each industry.",
    tools=[search_tool],
    agent=problem_analyst,
)

# Task 3: Generate a final report
report_writing_task = Task(
    description=(
        "Compile a well-structured report with industries, their key challenges, "
        "and why an AI-agent solution is a viable business opportunity."
    ),
    expected_output="A comprehensive business opportunity report in Markdown format.",
    agent=report_writer,
    output_file="business_opportunity_report.md"
)

# Form the Crew
crew = Crew(
    agents=[industry_researcher, problem_analyst, report_writer],
    tasks=[industry_research_task, problem_analysis_task, report_writing_task],
    process=Process.sequential
)

# Execute
result = crew.kickoff()
print(result)
