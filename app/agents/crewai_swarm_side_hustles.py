import os
from crewai import Agent, Task, Crew, Process, LLM
from langchain.llms.openai import OpenAI
from crewai_tools import ScrapeWebsiteTool
import litellm
from crewai_tools import SerperDevTool
from dotenv import load_dotenv
from fpdf import FPDF

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

# Initialize Search Tool
search_tool = SerperDevTool()

# ---------------------------- AGENTS ----------------------------

# Researcher Agent
researcher = Agent(
    role="AI Business Researcher",
    goal="Identify profitable side hustles using CrewAI.",
    verbose=True,
    memory=True,
    llm=llm,
    backstory=(
        "A highly skilled business researcher, passionate about AI monetization. "
        "You uncover new trends, analyze markets, and provide valuable insights on making money with AI."
    ),
    tools=[search_tool]
)

# Writer Agent (PDF Generator)
writer = Agent(
    role="AI Report Writer",
    goal="Convert research insights into a structured PDF report.",
    verbose=True,
    memory=True,
    llm=llm,
    backstory=(
        "An expert technical writer specializing in business reports. "
        "You take raw research and transform it into clear, actionable insights."
    )
)

# ---------------------------- TASKS ----------------------------

# Research Task
research_task = Task(
    description=(
        "Research high-earning video contents (youtube, instagram, youtube, tiktok) side hustles that use CrewAI. "
        "Analyze how others are making money with CrewAI, focusing on profitability and real-world examples. "
        "Your final output must be a structured summary listing at least 5-7 profitable side hustles, "
        "each with a short description and estimated earning potential."
    ),
    expected_output="A structured summary of CrewAI-based side hustles.",
    tools=[search_tool],
    agent=researcher,
)

# PDF Report Generation Task


def generate_pdf_report(content):
    """Generate a structured PDF report from the research content."""
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)

    pdf.cell(200, 10, "Profitable Side Hustles Using CrewAI", ln=True, align="C")
    pdf.ln(10)  # Line break

    pdf.set_font("Arial", size=12)
    for line in content.split("\n"):
        pdf.multi_cell(0, 10, line)
        pdf.ln(2)

    pdf.output("CrewAI_Side_Hustles_Report.pdf")
    return "PDF report generated successfully: CrewAI_Side_Hustles_Report.pdf"


write_task = Task(
    description=(
        "Take the research summary and create a structured PDF report. "
        "Ensure proper formatting, section headers, and clear descriptions. "
        "The final report should be professional and easy to read."
    ),
    expected_output="A well-formatted PDF report named 'CrewAI_Side_Hustles_Report.pdf'.",
    agent=writer,
    function=generate_pdf_report  # Call the PDF generation function
)

# ---------------------------- CREW SETUP ----------------------------

crew = Crew(
    agents=[researcher, writer],
    tasks=[research_task, write_task],
    process=Process.sequential  # Ensure research runs before writing
)

# ---------------------------- EXECUTION ----------------------------

print("🚀 Starting CrewAI Side Hustle Research...")
result = crew.kickoff()
print(result)
