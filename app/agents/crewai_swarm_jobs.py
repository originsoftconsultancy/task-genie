import os
from crewai import Agent, Task, Crew, Process, LLM
from langchain.llms.openai import OpenAI
from crewai_tools import ScrapeWebsiteTool
import litellm
from crewai_tools import SerperDevTool
from dotenv import load_dotenv

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

# Web search tool for job searching
search_tool = SerperDevTool()

# --- Agents ---
# Job Researcher Agent
job_researcher = Agent(
    role="Job Researcher",
    goal="Find remote job opportunities for game graphics and animation students.",
    backstory=(
        "You are an expert job researcher specializing in remote work. "
        "You find opportunities on job boards, freelancing sites, and company career pages."
    ),
    llm=llm,
    verbose=True,
    tools=[search_tool]
)

# Resume Optimizer Agent
resume_optimizer = Agent(
    role="Resume Optimizer",
    goal="Optimize resumes for remote job applications in game graphics and animation.",
    backstory=(
        "You are an experienced career coach who helps candidates tailor their resumes "
        "to match job descriptions effectively."
    ),
    llm=llm,
    verbose=True
)

# Job Application Advisor Agent
job_application_advisor = Agent(
    role="Job Application Advisor",
    goal="Help candidates craft compelling cover letters for job applications.",
    backstory=(
        "You are a hiring specialist with years of experience in writing persuasive cover letters "
        "to help candidates stand out."
    ),
    llm=llm,
    verbose=True
)

# --- Tasks ---
# Task 1: Research jobs
research_jobs_task = Task(
    description=(
        "Search online job boards and freelancing platforms for remote job opportunities "
        "in game graphics and animation suitable for students."
        "Focus on companies hiring remotely and collect details like job title, requirements, and application links."
    ),
    expected_output="A list of 5-10 relevant remote job openings with descriptions and application links.",
    tools=[search_tool],
    agent=job_researcher
)

# Task 2: Resume Optimization
optimize_resume_task = Task(
    description=(
        "Analyze the job listings and provide suggestions to optimize a resume for these positions."
        "Highlight key skills and experiences that should be included based on job descriptions."
    ),
    expected_output="A set of resume improvement suggestions tailored for remote jobs in game graphics and animation.",
    agent=resume_optimizer
)

# Task 3: Cover Letter Generation
generate_cover_letter_task = Task(
    description=(
        "Create a personalized cover letter template based on the job descriptions found. "
        "Ensure it highlights relevant skills in game graphics and animation."
    ),
    expected_output="A professional, personalized cover letter template that can be used for multiple applications.",
    agent=job_application_advisor
)

# --- Crew Setup ---
job_search_crew = Crew(
    agents=[job_researcher, resume_optimizer, job_application_advisor],
    tasks=[research_jobs_task, optimize_resume_task, generate_cover_letter_task],
    process=Process.sequential  # Tasks run in order
)

# --- Execute the Workflow ---
result = job_search_crew.kickoff()
print(result)
