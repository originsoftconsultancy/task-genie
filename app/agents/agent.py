from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
import inspect
import ast
import os
import asyncio
from pydantic_ai import Tool
from app.agents.tools import TOOLS
import logfire

logfire.configure()


class Genie(Agent):

    def __init__(self, model, name, system_prompt, deps_type, result_type, tools):

        tools = [self.generate_tool]
        super().__init__(model=model, name=name, system_prompt=system_prompt,
                         deps_type=deps_type, result_type=result_type, tools=tools)

    async def run(self, query):
        return await super().run(query)

    def generate_tool(self, ctx: RunContext[str], function_arguments: str, function_code: str, function_docstring: str) -> str:
        """
        This tool dynamically generates code for a tool for the provided `function_arguments`, `function_code` and `function_docstring`.
        Sometimes you may want to generate a tool dynamically based on the user's input. This tool does exactly that.
        Every argument is a string, and the return value should be a string as well.
        Please add "ctx: RunContext[str]" as the first argument in the `function_arguments` to access the context in which the tool operates.
        Example: `function_arguments` = "def add_tool(ctx: RunContext[str], a: int, b: int") -> int", `function_code` = "return a + b", `function_docstring` = "This tool adds two numbers a and b. Args: a: int, b: int. Returns: int".

        Args:
            ctx: RunContext[str], The context in which the tool operates.
            function_arguments: str, The signature of the tool.
            function_code: str, The code of the tool.
            function_docstring: str, The detailed docstring of the tool that describes the tool, arguments and return type.

        Returns:
            str: The generated tool code.
        """

        generated_code = f"""
{function_arguments}:
    \"\"\"
        {function_docstring}
    \"\"\"
    {function_code}"""

        tree = ast.parse(generated_code)
        function_def = next((node for node in ast.walk(
            tree) if isinstance(node, ast.FunctionDef)), None)

        function_name = function_def.name

        exec_globals = {"RunContext": RunContext}
        exec(generated_code, exec_globals)

        generated_function = exec_globals.get(function_name)

        self._register_tool(Tool(generated_function))

        return f"Tool '{function_name}' successfully generated and registered."


model = os.getenv("LLM_MODEL")

agent = Genie(
    model,
    name="genie",
    deps_type=str,
    result_type=str,
    system_prompt="",
    tools=[]
)


async def main():
    query = "Can you generate tool that adds two numbers a and b?"
    result = await agent.run(query)
    print(result._all_messages[-1].content)

    query = "Can you add two numbers 3 and 5?"
    result = await agent.run(query)
    print(result._all_messages[-1].content)

asyncio.run(main())
