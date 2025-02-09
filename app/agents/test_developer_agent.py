from FlagEmbedding import FlagModel
import uuid
from pydantic_ai.models.ollama import OllamaModel
from pydantic_ai.models.openai import OpenAIModel
from typing import Optional, Union, List
from pydantic import BaseModel, Field, ValidationError
from pydantic_ai import Agent, RunContext, Tool
import ast
import os
import asyncio
import logfire
from dotenv import load_dotenv
import subprocess
import sys
import traceback
from app.utils.code2exec import CodeExecutor
from pydantic_ai_expert import PydanticAIDeps, pydantic_ai_expert

load_dotenv()
# logfire.configure()


class SolutionArchitect(Agent):

    def __init__(self, model, name, system_prompt, deps_type, result_type, tools):

        self.developer = Agent(
            OpenAIModel(model_name=os.getenv("ALI_BABA_MODEL_NAME"),
                        base_url=os.getenv("ALI_BABA_BASE_URL"), api_key=os.getenv("ALI_BABA_API_KEY")),
            name="developer",
            deps_type=str,
            result_type=str,
            system_prompt="""
                You are a genius developer. Your job is to write executable python code for the given prompt.
                Please also add the external libraries that should be in requirements.txt for the code in the requirements section.
                If you need to put values to some variables, you can use environment variables using os.getenv function, list those environment variables at the end so that we can get them from user later while executing the code.
                Keep your output as follows:
                ```python
                   <your code, including imports>
                ```
                ```requirements
                    <your requirements>
                ```
                ```env_vars
                    <your environment variables>
                ```
            """,
            retries=1,
            tools=[Tool(self.get_multiagent_knowledge)]
        )

        super().__init__(model=model, name=name, system_prompt=system_prompt,
                         deps_type=deps_type, result_type=result_type, tools=tools)

    async def get_multiagent_knowledge(self, ctx: RunContext[str], query: str) -> str:
        """
        This function detailed knowledge about creating pydantic_ai agents and tools for the given prompt given in `query`.

        Args:
            query: str, The query is the original prompt

        Returns:
            str: detailed documentation about creating pydantic_ai agents and tools for the given prompt given in `query`.
        """

        result = await pydantic_ai_expert.run(query)

        return result._all_messages[-1].parts[0].content

    async def run(self, query, message_history=[]):

        done = False
        while not done:
            try:

                result = await self.developer.run(query, message_history=message_history)

                message_history = result._all_messages

                code_executor = CodeExecutor()

                return code_executor.execute(
                    result._all_messages[-1].parts[0].content)

            except Exception as e:
                query = f"There is problem with the code. Please try again. \nErrors: {e}"
                print(e)
                done = False


model = OllamaModel(os.getenv("LLM_MODEL"))

agent = SolutionArchitect(
    model,
    name="architect",
    deps_type=str,
    result_type=str,
    system_prompt="",
    tools=[]
)


async def main():

    prompt = ""
    messages = []
    while prompt != "exit":
        prompt = input("User: ")
        result = await agent.run(prompt, message_history=messages)
        print("Architect: \n" + result)

if __name__ == "__main__":
    asyncio.run(main())
