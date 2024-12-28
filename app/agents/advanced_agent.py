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

load_dotenv()
logfire.configure()


class Genie(Agent):

    def __init__(self, model, name, system_prompt, deps_type, result_type, tools):

        super().__init__(model=model, name=name, system_prompt=system_prompt,
                         deps_type=deps_type, result_type=result_type, tools=tools)

    async def run(self, query):
        await self.generate_custom_tools(query)
        response = await super().run(query)
        return response

    async def generate_custom_tools(self, query: str) -> bool:
        """
        This function generates a tool code.

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

        response = await super().run(tools_query)
        content = response._all_messages[-1].content.replace(
            "```python\n", "").replace("\n```", "")

        prompt_list = content.split("\n")

        for prompt in prompt_list:
            await self.register_tool(prompt + " (do not add any logging or print statements).")

        return True

    import os

    async def register_tool(self, query: str, file: str = None) -> bool:
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
            Return only the generated code. Please add docstrings to the function 
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

        print(instructions)

        response = await super().run(instructions)

        code = response._all_messages[-1].content.replace(
            "```python\n", "").replace("\n```", "")

        print(code)

        tree = ast.parse(code)
        function_def = next((node for node in ast.walk(
            tree) if isinstance(node, ast.FunctionDef)), None)

        function_name = function_def.name

        exec_globals = {"RunContext": RunContext}
        exec(code, exec_globals)

        generated_function = exec_globals.get(function_name)

        self._register_tool(Tool(generated_function))

        return True


model = OllamaModel("qwen2.5")

agent = Genie(
    model,
    name="genie",
    deps_type=str,
    result_type=str,
    system_prompt="",
    tools=[]
)


def send_email(sender: str, recipient: str, subject: str, body: str) -> bool:
    """
    Sends an email using the SendGrid API.

    Parameters:
    ctx (RunContext[str]): The runtime context.
    sender (str): The email address of the sender.
    recipient (str): The email address of the recipient.
    subject (str): The subject line of the email.
    body (str): The body content of the email.

    Returns:
    bool: True if the email was sent successfully, False otherwise.
    """
    try:
        api_key = os.getenv("SENDGRID_API_KEY")
        if not api_key:
            raise Exception("SendGrid API key is missing.")

        message = Mail(
            from_email=sender,
            to_emails=recipient,
            subject=subject,
            plain_text_content=body)

        sendgrid_client = SendGridAPIClient(api_key)
        response = sendgrid_client.send(message)

        print(response.status_code)
        print(response.body)
        return True
    except Exception as e:
        return False


async def main():

    send_email("hey@mobilegaragefleets.com",
               'mudassarm30@gmail.com', "Test email", "Hello world")
    # result = await agent.run("""
    #                            Please send me `Hello World` by an email using SendGrid API.
    #                            Use the following SendGrid API key and email details:
    #                            SendGrid API key: os.getenv("SENDGRID_API_KEY")
    #                            from_email: 'hey@mobilegaragefleets.com'
    #                            to_emails: 'hassan.zafar1994@gmail.com,mudassarm30@gmail.com'
    #
    #                            """)
    # print(result._all_messages[-1].content)


asyncio.run(main())
