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


load_dotenv()
logfire.configure()


class SolutionArchitect(Agent):

    def __init__(self, model, name, system_prompt, deps_type, result_type, tools):

        self.params = None

        self.assistant = Agent(
            OllamaModel(os.getenv("REASONING_MODEL")),
            name="assistant",
            deps_type=str,
            result_type=str,
            system_prompt="",
            tools=[]
        )

        self.developer = Agent(
            OllamaModel(os.getenv("REASONING_MODEL")),
            name="developer",
            deps_type=str,
            result_type=str,
            system_prompt="""
            You are a genius developer. Your job is to write executable code for the given prompt. 
            You should give your best effort to write the code that solves the problem or question given in the prompt. 
            You can use any library or code snippet to solve the problem. 
            Your code should not contain dummy values for any thing including arguments, return types and any local variable.
            """,
            tools=[]
        )

        system_prompt = f"""
        You are a genius solution architect agent. Your job is to solve the query given by the user completely and exactly. 
        You are given some building block tools to solve the query. You can use these tools to solve the query.
        `generate_custom_tools`: This tool generates a tool code for the given prompt.
        """ + "\n" + system_prompt

        tools = tools + [Tool(self.generate_custom_tools)]

        super().__init__(model=model, name=name, system_prompt=system_prompt,
                         deps_type=deps_type, result_type=result_type, tools=tools)

    async def run(self, query, message_history=[]):

        tasks = await self._divide_in_tasks_and_params(query)

        return await super().run(tasks, message_history=message_history, model_settings={"temperature": 0.0})

    async def generate_custom_tools(self, ctx: RunContext[str], query: str) -> str:
        """
        This function generates a tool code for the given prompt given in `query`.

        Args:
            query: str, The query is the original prompt

        Returns:
            str: Message showing if tool is generated or not.
        """

        function_name = "tool_" + str(uuid.uuid4()).replace("-", "_")

        instructions = f"""
            Please generate a single python executable function (with no parameters but only return type) that fulfills the prompt (given at the end). It should return as the outcome of last task done in the tool. 
            Please install the library using the `subprocess.check_call([sys.executable, "-m", "pip", "install", "<package_name>"])` command. After that all the required imports should be included within the function. Do not import libraries outside the new function.
            There is no need of any logging or code comments, but general detailed docstring. Please enclose the code in triple quotes like this: ```python <code> ```
            Note: 
            Do not add any other text or comments or any characters like ' in any text within the output as the code will be executed. 
            Use the function name as `{function_name}`. You can extract function call parameters below as well.
            Do not create any asynchronous functions or use any asynchronous code in the tool code.

            Example:

            ```python
            def {function_name}(<arguments-list>) -> <return-type>:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "<package_name 1>"])
                subprocess.check_call([sys.executable, "-m", "pip", "install", "<package_name 2>"])
                import <package_name 1>
                import <package_name 2>

                <function code>
            ```

            User Prompt:
            `{query}`
        """

        if os.getenv("DEBUG", "False").lower() == "true":
            print(instructions)

        status = False
        messages = []

        while status != True:
            response = await self.developer.run(instructions, message_history=messages)

            status, tool, function_name = self._extract_function(response)

            if status == True:

                if os.getenv("DEBUG", "False").lower() == "true":
                    print(
                        f"Tool generated successfully, trying to execute the tool code: {tool}")

                try:
                    response = str(tool())

                    if os.getenv("DEBUG", "False").lower() == "true":
                        print(
                            "Tool executed successfully with response: " + response)

                    return response
                except Exception as e:
                    detailed_trace = traceback.format_exc()
                    status = False
                    if os.getenv("DEBUG", "False").lower() == "true":
                        print("Error executing the tool code!")
                        print("Error Trace: " + detailed_trace)

                    instructions = f"The code generated has problem running. Please fix the code and try again. The code will be executed so only generate the code. \nError Trace: \n{detailed_trace}\nOriginal prompt: {instructions}"

            else:
                if os.getenv("DEBUG", "False").lower() == "true":
                    print("Error in tool: " + tool)
                    print("Generating tool code again")
                messages = response._all_messages
                test_result = tool
                instructions = f"The code generated has an error. Please generate the code again.\nError Trace: \n{test_result}"

        return None

    async def _divide_in_tasks_and_params(self, query: str) -> str:
        """
        This function divides the query into tasks based on the prompt.

        Args:
            query: str, The query to divide into tasks.

        Returns:
            List[str]: List of tasks.
        """

        response = await self.assistant.run(f"""
                                        Can you create tasks (as few as possible, high granularity task prompts) from the user prompt `{query}` that should be in order. 
                                        Give numbers to each task and keep them in correct order. Keep it in one line. 
                                        Each task will be dependent on the previous task and will work on its output. 
                                        Do not call any tool / function please.
                                        Keep the task short, simple and in English. Do not describe in detail. 
                                        """)

        tasks = response._all_messages[-1].parts[0].content

        format = "{'tasks': [{'task': '<description>', 'params': [{'key': 'value', 'key': 'value'}]}, ... ,{'task': '<description>', 'params': [{'key': 'value', 'key': 'value'}]}]}"

        response = await self.assistant.run(f"""
                                        Please extract user provided data parameters from the user prompt `{query}` that are required to fulfill the tasks:
                                        `{tasks}`
                                        The tasks and their related parameters should be in the English language and in form of json as follows: 
                                        `{format}`
                                            """)
        tasks = response._all_messages[-1].parts[0].content.replace(
            "```json\n", "").replace("\n```", "")

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

            exec_globals = globals().copy()
            exec(code, exec_globals)

            generated_function = exec_globals.get(function_name)

            return True, generated_function, function_name
        except Exception as e:
            return False, traceback.format_exc(), None


model = OllamaModel(os.getenv("LLM_MODEL"))

agent = SolutionArchitect(
    model,
    name="architect",
    deps_type=str,
    result_type=str,
    system_prompt="",
    tools=[]
)

"""
async def main():

    prompt = ""
    messages = []
    while prompt != "exit":
        prompt = input("User: ")
        result = await agent.run(prompt, message_history=messages)
        print("Developer: " + result._all_messages[-1].parts[0].content)
        messages = result._all_messages
"""


async def main():

    developer = Agent(
        OllamaModel(os.getenv("REASONING_MODEL")),
        name="developer",
        deps_type=str,
        result_type=str,
        system_prompt="""
            You are a genius developer. Your job is to write executable python code for the given prompt. 
            Remember to only return the executable code as your provided code will be directly executed.
            """,
        tools=[]
    )

    prompt = "Keep looking at the domain dataicraft.com through ping messages. If it goes out of reach, send email to me at mudassarm30@gmail.com."
    result = await developer.run(prompt, message_history=[])
    print("Developer: " + result._all_messages[-1].parts[0].content)


if __name__ == "__main__":
    asyncio.run(main())
