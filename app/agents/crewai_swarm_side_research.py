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


# ---------------------------- SETUP SELENIUM ----------------------------
def scrape_acquire_listings():
    """Scrapes Acquire.com listings with dynamic scrolling."""
    print("🚀 Scraping Acquire.com listings...")

    # Set up Selenium WebDriver
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run in headless mode
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=Service(
        ChromeDriverManager().install()), options=options)
    driver.get("https://app.acquire.com/all-listing")

    # Scroll to load more listings
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)  # Allow time to load
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    # Get page source and close driver
    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    # Extract listings
    listings = []
    for listing in soup.select(".listing-item"):  # Adjust selector as needed
        title = listing.select_one(
            ".listing-title").text.strip() if listing.select_one(".listing-title") else "N/A"
        price = listing.select_one(
            ".listing-price").text.strip() if listing.select_one(".listing-price") else "N/A"
        category = listing.select_one(
            ".listing-category").text.strip() if listing.select_one(".listing-category") else "N/A"

        listings.append({"title": title, "price": price, "category": category})

    print(f"✅ Scraped {len(listings)} listings.")
    return listings

# ---------------------------- AGENTS ----------------------------


# Scraper Agent
scraper_agent = Agent(
    role="Web Scraper",
    goal="Extract all business listings from Acquire.com.",
    verbose=True,
    memory=True,
    llm=llm,
    backstory="An expert in web scraping, skilled at extracting data from complex websites.",
    function=scrape_acquire_listings
)

# Business Analyst Agent


def analyze_listings(listings):
    """Analyzes the scraped business listings to identify trends and opportunities."""
    print("📊 Analyzing business data...")

    category_counts = {}
    for listing in listings:
        category = listing["category"]
        if category in category_counts:
            category_counts[category] += 1
        else:
            category_counts[category] = 1

    # Identify top categories
    top_categories = sorted(category_counts.items(),
                            key=lambda x: x[1], reverse=True)[:5]

    insights = f"📈 **Business Trends & Opportunities**\n\n"
    insights += "### **Top Business Categories:**\n"
    for cat, count in top_categories:
        insights += f"- {cat}: {count} listings\n"

    insights += "\n### **Opportunities:**\n"
    insights += "1. Identify high-demand, low-competition categories.\n"
    insights += "2. Look for successful businesses and find ways to improve them.\n"
    insights += "3. Explore trends based on pricing and market gaps.\n"

    print("✅ Analysis complete.")
    return insights


analyst_agent = Agent(
    role="Business Analyst",
    goal="Analyze business categories, statistics, and trends from Acquire.com data.",
    verbose=True,
    memory=True,
    llm=llm,
    backstory="A seasoned business analyst with expertise in market research and identifying profitable opportunities.",
    function=analyze_listings
)

# ---------------------------- TASKS ----------------------------

# Scraping Task
scraping_task = Task(
    description="Scrape all listings from Acquire.com, including categories, pricing, and trends.",
    expected_output="A structured list of all business listings with relevant details.",
    agent=scraper_agent
)

# Analysis Task
analysis_task = Task(
    description="Analyze the scraped business data to determine trends, top categories, and profitable opportunities.",
    expected_output="A business insights summary with trends and recommended opportunities.",
    agent=analyst_agent
)

# ---------------------------- PDF REPORT GENERATION ----------------------------


def generate_pdf_report(analysis_content):
    """Generate a structured PDF report with analysis results."""
    print("📝 Generating PDF Report...")

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)

    pdf.cell(200, 10, "Business Analysis Report - Acquire.com",
             ln=True, align="C")
    pdf.ln(10)  # Line break

    pdf.set_font("Arial", size=12)
    for line in analysis_content.split("\n"):
        pdf.multi_cell(0, 10, line)
        pdf.ln(2)

    pdf.output("Acquire_Business_Report.pdf")
    print("✅ PDF report generated: Acquire_Business_Report.pdf")
    return "PDF report generated successfully: Acquire_Business_Report.pdf"


# Report Writer Agent
writer_agent = Agent(
    role="Report Writer",
    goal="Convert business insights into a structured PDF report.",
    verbose=True,
    memory=True,
    llm=llm,
    backstory="An expert technical writer who creates structured business reports.",
    function=generate_pdf_report
)

# PDF Task
pdf_task = Task(
    description="Create a PDF report summarizing business trends and opportunities.",
    expected_output="A well-structured PDF report named 'Acquire_Business_Report.pdf'.",
    agent=writer_agent
)

# ---------------------------- CREW SETUP ----------------------------

crew = Crew(
    agents=[scraper_agent, analyst_agent, writer_agent],
    tasks=[scraping_task, analysis_task, pdf_task],
    process=Process.sequential
)

# ---------------------------- EXECUTION ----------------------------

print("🚀 Starting Acquire.com Business Research...")
result = crew.kickoff()
print(result)
