import os
from crewai import Agent, Task, Crew, Process, LLM
from langchain.llms.openai import OpenAI

# Set up the Ali Baba Model
llm = LLM(
    model="gemini/gemini-2.0-flash",
    temperature=0.7,
    api_key=os.getenv("GEMINI_API_KEY"),
    max_rpm=2,
)

os.environ['LITELLM_LOG'] = 'DEBUG'
# ------------------------
# Define Debate Agents
# ------------------------

debater1 = Agent(
    role="Debater 1",
    goal="Defend your perspective and respond critically to others' arguments.",
    backstory="You are a strong advocate of your school of thought of Sunni sect in Islam. "
              "You carefully analyze the points made by others and respond with conviction.",
    verbose=True,
    memory=True,
    llm=llm
)

debater2 = Agent(
    role="Debater 2",
    goal="Defend your perspective and respond critically to others' arguments.",
    backstory="You are a committed thinker who is confident that your perspective about Shia Islam is the most accurate. "
              "You respond thoughtfully and challenge opposing claims.",
    verbose=True,
    memory=True,
    llm=llm
)

debater3 = Agent(
    role="Debater 3",
    goal="Defend your perspective and respond critically to others' arguments.",
    backstory="You are deeply knowledgeable about your tradition about Ibadi Islam. "
              "You emphasize why your perspective stands stronger than others.",
    verbose=True,
    memory=True,
    llm=llm
)

debater4 = Agent(
    role="Debater 4",
    goal="Defend your perspective on Ahmadiyya Islamic teachings and respond critically to others' arguments.",
    backstory="You are passionate about your belief system and well-prepared to debate against all objections.",
    verbose=True,
    memory=True,
    llm=llm
)

moderator = Agent(
    role="Moderator",
    goal="Keep the debate structured, ask for responses, and finally give a concluding decision.",
    backstory="You are a neutral and fair debate moderator. "
              "You ensure that each debater has the chance to speak and that the debate remains productive.",
    verbose=True,
    memory=True,
    llm=llm
)

# ------------------------
# Define Debate Tasks
# ------------------------

debate_task = Task(
    description=(
        "Start a structured debate between the four debaters. "
        "Each debater should defend their position, challenge others, and respond to critiques. "
        "Ensure each agent has at least 2 turns to speak."
        "Topic of the debate is: 'Which Islamic sect has the most accurate teachings?'"
    ),
    expected_output=(
        "A transcript of the debate with contributions from all 4 debaters."
    ),
    agent=moderator,  # Moderator orchestrates the discussion
)

conclusion_task = Task(
    description=(
        "After the debate, analyze the discussion carefully and provide a final conclusion. "
        "The conclusion should summarize key arguments and declare which debater made the strongest case."
    ),
    expected_output=(
        "A clear and reasoned final judgment summarizing the debate and identifying the winner."
    ),
    agent=moderator,
)

# ------------------------
# Create Crew
# ------------------------

crew = Crew(
    agents=[debater1, debater2, debater3, debater4, moderator],
    tasks=[debate_task, conclusion_task],
    process=Process.sequential,
)

# ------------------------
# Run Debate
# ------------------------

result = crew.kickoff(inputs={})
print(result)
