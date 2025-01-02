import uuid
import sendgrid
from sendgrid.helpers.mail import Mail, To
from sendgrid import SendGridAPIClient
from pydantic_ai.models.ollama import OllamaModel
from typing import Optional, Union, List
import openai
from pydantic import BaseModel, Field, ValidationError
from pydantic_ai import Agent, RunContext
from playwright.sync_api import sync_playwright
import ast
import os
import asyncio
from pydantic_ai import Tool
from pydantic_ai.models import ModelResponse
import logfire
from dotenv import load_dotenv
from pydantic.dataclasses import dataclass
import subprocess
import sys
import traceback

load_dotenv()
logfire.configure()


class SWArchitect(Agent):

    def __init__(self, model, name, system_prompt, deps_type, result_type, tools):

        self.params = None

        self.assistant = Agent(
            OllamaModel(os.getenv("LLM_MODEL")),
            name="assistant",
            deps_type=str,
            result_type=str,
            system_prompt="",
            tools=[]
        )

        self.developer = Agent(
            OllamaModel(os.getenv("DEVELOPER_LLM_MODEL")),
            name="developer",
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

        tasks, params = await self._divide_in_tasks_and_params(query)

        self.params = params

        while not done:
            try:
                response = await super().run(tasks, message_history=message_history)
                return response
            except Exception as e:
                if os.getenv("DEBUG", "False").lower() == "true":
                    detailed_trace = traceback.format_exc()
                    print("Error in running the agent: " + str(e))
                    print("Detailed Trace: " + detailed_trace)
                    print("Trying again")
                await asyncio.sleep(3)
                tasks = f"Getting the following error: {detailed_trace}. Please try to fix the problem and try again."
                continue

    async def generate_custom_tools(self, ctx: RunContext[str], query: str) -> str:
        """
        This function generates a tool code for the given user prompt given in `query`.

        Args:
            query: str, The query is the original prompt from the user

        Returns:
            str: Message showing if tool is generated or not.
        """

        tools_query = f"""
            Give me one prompt that you will send to LLM to generate a tool (python code) for you if the user prompt is the following.
            Try to keep the tool prompt for a single tool that performs all required operations.
            Do not give example of the code, just the prompt.

            For example if the user prompt is

            ```
            Can you tell me what is 2+2*2?
            ```

            the response should be

            ```
            Please generate a tool to calculate the result of the following mathematical expression: 2+2*2. The tool should return the result of the expression.
            ```

            User Prompt:
            ```
            {query}
            ```
        """

        response = await self.assistant.run(tools_query)
        content = response._all_messages[-1].parts[0].content

        prompt = content

        status, function_name = await self.register_tool(prompt)

        return f"The tool `{function_name}` is generated and registered successfully. You can call this tool successfully only once with parameters from: `{self.params}`"

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

        function_name = "tool_" + str(uuid.uuid4()).replace("-", "_")

        instructions = f"""
            Please generate a single python executable function (with parameters and return type) that fulfills the user prompt given at the end. 
            All the required imports should be included within the function. But before each import, please install the library using the `subprocess.check_call([sys.executable, "-m", "pip", "install", "<package_name>"])` command.
            There is no need of any logging or code comments, but general detailed docstring. Add a function call with all the required parameters (from the user prompt) at the end. Please enclose the code in triple quotes like this: ```python <code> ```
            Note: There must be exact one function in the code and the commented call to the function should be at the end of the code. Use the function name as `{function_name}`. You can extract function call parameters below as well.

            Example:

            ```python
            def {function_name}(<arguments-list>) -> <return-type>:
                import subprocess
                import sys
                subprocess.check_call([sys.executable, "-m", "pip", "install", "<package_name 1>"])
                subprocess.check_call([sys.executable, "-m", "pip", "install", "<package_name 2>"])
                import <package_name 1>
                import <package_name 2>

                <function code>
            
            # Function Call: {function_name}(<arguments extracted from user prompt>)
            ```

            User Prompt:
            `{query}`

            Parameters:
            `{self.params}`
        """

        if os.getenv("DEBUG", "False").lower() == "true":
            print(instructions)

        status = False
        messages = []

        while status != True:
            response = await self.developer.run(instructions, message_history=messages)

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

    async def _divide_in_tasks_and_params(self, query: str) -> str:
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

        response = await self.assistant.run(f"""
                                        Please extract user provided data parameters from the user prompt `{query}` that are required to fulfill the tasks:
                                        `{tasks}`
                                        The parameters should be in the form of json. Keep text in English.
                                            """)
        params = response._all_messages[-1].parts[0].content.replace(
            "```json\n", "").replace("\n```", "")

        return tasks, params

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

agent = SWArchitect(
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
        print("Developer: " + result._all_messages[-1].parts[0].content)
        messages = result._all_messages

asyncio.run(main())
