import os
from crewai import LLM, Agent, Task, Crew
from langchain_community.tools.google_trends import GoogleTrendsQueryRun
from langchain_community.utilities.google_trends import GoogleTrendsAPIWrapper
from langchain.tools import Tool
from langchain_community.utilities import SerpAPIWrapper


os.environ["SERPAPI_API_KEY"] = "3cb6b8eabfba4c284b11dfe3e2e694d61c2de09a"

# Initialize LLM
llm = LLM(model="ollama/qwen2.5:latest", base_url="http://localhost:11434")

# Set up Google Trends API wrapper
trends_api = GoogleTrendsAPIWrapper()

# Set up SerpAPI for Google Search
google_search = SerpAPIWrapper()

# --------------- Define Tools ---------------

# Fetch trending men's t-shirt prints from Google Trends


def fetch_tshirt_trends():
    tool = GoogleTrendsQueryRun(api_wrapper=trends_api)
    query = "men's t-shirt prints trends"
    return tool.run(query)


fetch_trends_tool = Tool(
    name="Google Trends T-Shirt Prints Analyzer",
    func=fetch_tshirt_trends,
    description="Fetches the latest t-shirt print trends from Google Trends."
)

# Search for expert opinions and market trends


# Initialize SerpAPI
google_search = SerpAPIWrapper()

# Define a function to fetch Google Search results using SerpAPI


def fetch_market_insights():
    query = "best-selling t-shirt prints for men in 2024"
    return google_search.run(query)


# Define the search tool for CrewAI
fetch_search_tool = Tool(
    name="Google Search Market Insights",
    func=fetch_market_insights,
    description="Searches Google for market trends and consumer preferences in men's t-shirt prints."
)

# --------------- Define Agents ---------------

# 1. Trends Researcher - Fetches print trends
researcher = Agent(
    role="Trends Researcher",
    goal="Identify the latest men's t-shirt print trends using Google Trends and Google Search.",
    backstory="A fashion industry expert specializing in trend analysis and consumer behavior.",
    tools=[fetch_trends_tool, fetch_search_tool],
    llm=llm,
    verbose=True
)

# 2. Consumer Analyst - Understands buyer preferences
consumer_analyst = Agent(
    role="Consumer Analyst",
    goal="Analyze consumer preferences for t-shirt prints, including color, graphics, and typography.",
    backstory="A consumer behavior specialist with expertise in apparel market research.",
    llm=llm,
    verbose=True
)

# 3. Forecasting Expert - Predicts upcoming trends
forecaster = Agent(
    role="Trend Forecaster",
    goal="Predict the top 5 t-shirt print designs that will dominate the market in the next 6 months.",
    backstory="A data scientist specializing in fashion forecasting.",
    llm=llm,
    verbose=True
)

# 4. Business Strategist - Creates a final report
strategist = Agent(
    role="Business Strategist",
    goal="Compile insights into a detailed report with actionable recommendations for a t-shirt printing business.",
    backstory="A business consultant helping startups make data-driven decisions.",
    llm=llm,
    verbose=True
)

# --------------- Define Tasks ---------------

# Task 1: Fetch Print Trends
fetch_trends_task = Task(
    description="Retrieve the latest data on trending men's t-shirt prints from Google Trends and Google Search.",
    agent=researcher,
    expected_output="A list of the most popular and rising t-shirt prints, patterns, and designs."
)

# Task 2: Analyze Consumer Preferences
analyze_preferences_task = Task(
    description="Examine the consumer demand for various t-shirt prints, including colors, designs, and typography.",
    agent=consumer_analyst,
    context=[fetch_trends_task],
    expected_output="A report detailing consumer preferences for different t-shirt print styles."
)

# Task 3: Forecast Future Trends
forecast_trends_task = Task(
    description="Predict the top 5 t-shirt print designs that will dominate in the next 6 months.",
    agent=forecaster,
    context=[fetch_trends_task, analyze_preferences_task],
    expected_output="A future trend analysis highlighting the top 5 upcoming t-shirt print styles."
)

# Task 4: Generate Business Report
generate_report_task = Task(
    description="Compile the research findings into a structured business strategy report for a new t-shirt printing business.",
    agent=strategist,
    context=[forecast_trends_task],
    expected_output="A comprehensive business report with insights and recommendations on t-shirt print trends."
)

# --------------- Assemble CrewAI System ---------------

crew = Crew(
    agents=[researcher, consumer_analyst, forecaster, strategist],
    tasks=[fetch_trends_task, analyze_preferences_task,
           forecast_trends_task, generate_report_task],
    verbose=True
)

# --------------- Run the Crew ---------------
if __name__ == "__main__":
    result = crew.kickoff()
    print("\n--- Final T-Shirt Print Trends Business Report ---\n")
    print(result)
