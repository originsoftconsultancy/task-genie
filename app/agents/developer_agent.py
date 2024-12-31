import sendgrid
from sendgrid.helpers.mail import Mail, To
from sendgrid import SendGridAPIClient
from pydantic_ai.models.ollama import OllamaModel
from typing import Optional, Union, List
import openai
from pydantic import BaseModel, Field, ValidationError, validator
from pydantic_ai import Agent, RunContext
from playwright.sync_api import sync_playwright
import ast
import os
import asyncio
from pydantic_ai import Tool
import logfire
from dotenv import load_dotenv
from pydantic.dataclasses import dataclass
import subprocess
import sys
import traceback

load_dotenv()
logfire.configure()


class Developer(Agent):

    def __init__(self, model, name, system_prompt, deps_type, result_type, tools):

        self.assistant = Agent(
            OllamaModel(os.getenv("LLM_MODEL")),
            name="assistant",
            deps_type=str,
            result_type=str,
            system_prompt="",
            tools=[]
        )

        system_prompt = f"""
            If you need any tools to fulfill the user prompt, use the function `generate_custom_tools` with the provided user prompt in `query`. 
            Call the function `generate_custom_tools` once for the whole user prompt as it will internally subdivide the prompt. 
            The function will generate a tool code for the given user prompt. Check for tools in the `tools` list then and use it to fulfill the user prompt.
        """ + "\n" + system_prompt
        tools = tools + [Tool(self.generate_custom_tools)]
        super().__init__(model=model, name=name, system_prompt=system_prompt,
                         deps_type=deps_type, result_type=result_type, tools=tools)

    async def run(self, query, message_history=[]):

        done = False
        tasks = await self._divide_in_tasks(query)

        while not done:
            try:
                response = await super().run(tasks, message_history=message_history)
                return response
            except Exception as e:
                if os.getenv("DEBUG", "False").lower() == "true":
                    print("Error in running the agent: " + str(e))
                    print("Trying again")
                await asyncio.sleep(3)
                continue

    async def generate_custom_tools(self, ctx: RunContext[str], query: str) -> bool:
        """
        This function generates a tool code for the given user prompt given in `query`.

        Args:
            query: str, The query is the original prompt from the user

        Returns:
            str: Message showing if tool is generated or not.
        """

        tools_query = f"""
            Give me  (short and one liner) prompts (one on each line) that you will send you LLM to generate tools (python code) for you if the user prompt is the following.
            Give only one prompt for each tool you want to generate. For each operation generate different tool.

            For example if the user prompt is

            ```
            Can you tell me what is 2+2*2?
            ```

            the response should be

            ```
            Please generate a tool to add two numbers.
            Please generate a tool to multiply two numbers.
            ```

            User Prompt:
            ```
            {query}
            ```
        """

        response = await self.assistant.run(tools_query)
        content = response._all_messages[-1].parts[0].content.replace(
            "```python\n", "").replace("\n```", "")

        prompt_list = content.split("\n")

        # Remove empty items from prompt_list
        prompt_list = [prompt for prompt in prompt_list if prompt.strip()]
        functions = []

        for prompt in prompt_list:
            status, function_name = await self.register_tool(prompt + " (do not add any logging or print statements).")
            if status:
                functions.append(function_name)

        return "Following tools have been generated and registered, please use them in order to fulfill user prompt: " + (", ".join(functions))

    import os

    async def register_tool(self, query: str, file: str = None):
        """
        This function queries the model to generate a tool code and registers it or saves it to a file.

        Args:
            query: str, The query to generate the tool code.
            file: str, The file path to save the tool code.

        Returns:
            bool: true if everything worked fine.
        """

        instructions = f"""
            Please generate a python function (in English) for the prompt given at the end.
            Keep the first argument as: `ctx: RunContext[str]`, set the parameters types and return type as well.
            Return only the generated code. Please add docstring to the function 
            The ctx has no logging function, use logfire.log('info', '<log message here>') for logging anything.
            Please enclose the code in triple quotes like this: ```python <code> ```

            Example:

            ```python
            import <required-imports>

            def <tool-name>(ctx: RunContext[str], <arguments-list>) -> <return-type>:
                <code>
            ```

            User Prompt:
            `{query}`
        """

        if os.getenv("DEBUG", "False").lower() == "true":
            print(instructions)

        status = False
        messages = []

        while status != True:
            response = await self.assistant.run(instructions, message_history=messages)

            status, result, function_name = self._extract_function(response)

            if status == True:
                if os.getenv("DEBUG", "False").lower() == "true":
                    print("Registering tool")
                generated_function = result
                self._register_tool(Tool(generated_function))
                return True, function_name
            else:
                if os.getenv("DEBUG", "False").lower() == "true":
                    print("Error in tool: " + result)
                    print("Generating tool code again")
                messages = response._all_messages
                test_result = result
                instructions = f"The code generated has an error. Please generate the code again.\nError Trace: \n{test_result}"

        return False, None

    async def _divide_in_tasks(self, query: str) -> str:
        """
        This function divides the query into tasks based on the prompt.

        Args:
            query: str, The query to divide into tasks.

        Returns:
            List[str]: List of tasks.
        """

        response = await self.assistant.run(f"""
                                        Can you create tasks (high granularity 2 to 3 task prompts) from the user prompt `{query}` that should be in order. 
                                        Give numbers to each task and keep them in correct order. Keep it in one line. 
                                        Do not call any tool / function please.
                                        Keep the task short, simple and in English. Do not describe in detail. 
                                     """)

        tasks = response._all_messages[-1].parts[0].content

        return tasks

    def _extract_function(self, response):

        try:
            code = response._all_messages[-1].parts[0].content.replace(
                "```python\n", "").replace("\n```", "")

            if os.getenv("DEBUG", "False").lower() == "true":
                print(code)

            tree = ast.parse(code)
            function_def = next((node for node in ast.walk(
                tree) if isinstance(node, ast.FunctionDef)), None)

            function_name = function_def.name

            exec_globals = {"RunContext": RunContext}
            exec(code, exec_globals)

            generated_function = exec_globals.get(function_name)

            return True, generated_function, function_name
        except Exception as e:
            return False, traceback.format_exc(), None


model = OllamaModel(os.getenv("LLM_MODEL"))

agent = Developer(
    model,
    name="developer",
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
        print("Developer: " + result._all_messages[-1].parts[0].content)
        messages = result._all_messages

asyncio.run(main())
