from FlagEmbedding import FlagModel
import uuid
from pydantic_ai.models.ollama import OllamaModel
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
from pydantic_ai_expert import PydanticAIDeps, pydantic_ai_expert
import re

load_dotenv()
logfire.configure()


class SolutionArchitect(Agent):

    def __init__(self, model, name, system_prompt, deps_type, result_type, tools):

        # model_settings={"temperature": 0.0}

        self.developer = Agent(
            OllamaModel(os.getenv("REASONING_MODEL")),
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
            """
        )

        super().__init__(model=model, name=name, system_prompt=system_prompt,
                         deps_type=deps_type, result_type=result_type, tools=tools)

    async def run(self, query, message_history=[]):

        result = await self.developer.run(query, message_history=message_history)

        code, requirements, env_vars = self._extract_function_and_requirements(
            result._all_messages[-1].parts[0].content)

        print(code)
        print(requirements)
        print(env_vars)

    def _extract_function_and_requirements(self, text):

        # Regex patterns for Python code and requirements
        code_pattern = r"```python(.*?)```"
        requirements_pattern = r"```requirements(.*?)```"
        env_vars_pattern = r"```env_vars(.*?)```"

        # Extract the first occurrence of each
        code = re.search(code_pattern, text, re.DOTALL)
        requirements = re.search(requirements_pattern, text, re.DOTALL)
        env_vars = re.search(env_vars_pattern, text, re.DOTALL)

        # Get the matched strings or set as empty if not found
        code = code.group(1).strip() if code else ""
        requirements = requirements.group(1).strip() if requirements else ""
        env_vars = env_vars.group(1).strip() if env_vars else ""

        return code, requirements, env_vars


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
        await agent.run(prompt, message_history=messages)

if __name__ == "__main__":
    asyncio.run(main())
