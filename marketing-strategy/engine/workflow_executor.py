import json
import re
import os
import jsonschema
from pydantic import BaseModel
import requests
import logfire
import asyncio
from dotenv import load_dotenv
from engine.validation.workflow_validator import WorkflowValidator
from pydantic_ai import Agent, capture_run_messages, RunContext
from pydantic_ai.models.openai import OpenAIModel

load_dotenv()

model = OpenAIModel(model_name=os.getenv("ALI_BABA_MODEL_NAME"),
                    base_url=os.getenv("ALI_BABA_BASE_URL"), api_key=os.getenv("ALI_BABA_API_KEY"))

logfire.configure(send_to_logfire='if-token-present')


agent = Agent(
    model=model,
    system_prompt="Extract the audience and campaign message from the given user prompt.",
    result_type=str,
    deps_type=None,
    retries=3
)


@agent.system_prompt
def dynamic_prompt(ctx: RunContext[str]) -> str:
    return ctx.deps


class WorkflowExecutor:
    def __init__(self, workflow: dict, initial_context: dict = None):
        """
        Initializes the WorkflowExecutor with a workflow, schema, and an optional initial context.
        """
        self.workflow = workflow
        self.validator = WorkflowValidator()

        # Initialize context with user-provided inputs
        self.context = initial_context or {}

    def execute(self):
        """
        Executes the workflow steps in order after validation.
        """

        self.validate_workflow()
        self.preprocess_workflow()

        print("Executing workflow...")

        for step in self.workflow.get("workflow", {}).get("steps", []):
            self.execute_step(step)

        print("Workflow execution completed.")

    def execute_step(self, step):
        """
        Executes a single step based on its type.
        """
        step_type = step.get("type")
        if step_type == "tool_call":
            self.execute_tool_call(step)
        elif step_type == "api_call":
            self.execute_api_call(step)
        elif step_type == "llm_call":
            self.execute_llm_call(step)
        elif step_type == "conditional":
            self.execute_conditional(step)
        elif step_type == "for_loop":
            self.execute_for_loop(step)
        elif step_type == "while_loop":
            self.execute_while_loop(step)
        elif "parallel" in step:
            self.execute_parallel(step["parallel"])
        else:
            print(f"Unknown step type: {step_type}")

    def execute_tool_call(self, step):
        """
        Executes a tool call step.
        """
        tool_name = step["parameters"].get("tool")
        inputs = {key: self.context.get(
            key) for key in step["parameters"].get("input_keys", [])}
        print(f"Calling tool '{tool_name}' with inputs: {inputs}")
        # Placeholder for actual tool call
        outputs = {}  # Replace with actual tool outputs
        for key, value in zip(step["parameters"].get("output_keys", []), outputs):
            self.context[key] = value

    def execute_api_call(self, step):
        """
        Executes an API call step.
        """
        api_endpoint = step["parameters"].get("api")
        method = step["parameters"].get("method", "GET").upper()
        payload = {key: self.context.get(
            key) for key in step["parameters"].get("input_keys", [])}
        print(
            f"Making {method} request to '{api_endpoint}' with payload: {payload}")
        response = None
        if method == "GET":
            response = requests.get(api_endpoint, params=payload)
        elif method == "POST":
            response = requests.post(api_endpoint, json=payload)
        elif method == "PUT":
            response = requests.put(api_endpoint, json=payload)
        elif method == "DELETE":
            response = requests.delete(api_endpoint, json=payload)
        else:
            print(f"Unsupported HTTP method: {method}")
            return
        if response and response.status_code == 200:
            data = response.json()
            for key in step["parameters"].get("output_keys", []):
                self.context[key] = data.get(key)
        else:
            print(f"API call failed with status code: {response.status_code}")

    def execute_llm_call(self, step):
        """
        Executes an LLM (Language Model) call step.
        """
        # Resolve the prompt from the context
        prompt = step["parameters"].get("prompt")
        system_prompt = step["parameters"].get("system_prompt")

        # Prepare inputs for the LLM call
        output_keys = step["parameters"].get(
            "output_keys", [])

        if (len(output_keys) > 0):
            system_prompt = f"""
                {system_prompt}
                Format the response strictly with the following structure:
                Use the following exact key names for the outputs:
                {output_keys}
                Do not return any other text.
            """

        print(
            f"Generating LLM response for prompt: '{prompt}' with system prompt: '{system_prompt}'")

        with capture_run_messages() as messages:
            try:
                llm_response = asyncio.run(
                    agent.run(prompt, deps=system_prompt))

                if (len(output_keys) > 0):
                    llm_response = json.loads(llm_response.data)

                    for key, value in llm_response.items():
                        self.context[key] = value

                else:
                    self.context["response"] = llm_response.data

            except Exception as e:
                print("Error:", e)
                print("Messages:", messages)

    def execute_conditional(self, step):
        """
        Executes a conditional step.
        """
        for condition in step.get("conditions", []):
            condition_expr = condition.get("condition")
            if self.evaluate_condition(condition_expr):
                print(
                    f"Condition '{condition_expr}' met. Executing next step.")
                self.execute_step(condition.get("next_step"))
                break
            else:
                print(f"Condition '{condition_expr}' not met.")

    def execute_for_loop(self, step):
        """
        Executes a for-loop step.
        """
        loop_var = step.get("loop_variable")
        iterable = self.context.get(step.get("iterable"), [])
        print(
            f"Executing for-loop over '{iterable}' with loop variable '{loop_var}'")
        for item in iterable:
            self.context[loop_var] = item
            self.execute_step(step.get("body"))

    def execute_while_loop(self, step):
        """
        Executes a while-loop step.
        """
        condition = step.get("condition")
        print(f"Executing while-loop with condition '{condition}'")
        while self.evaluate_condition(condition):
            self.execute_step(step.get("body"))

    def execute_parallel(self, steps):
        """
        Executes steps in parallel.
        """
        print(f"Executing {len(steps)} steps in parallel.")
        # Placeholder for parallel execution logic
        for step in steps:
            self.execute_step(step)

    def evaluate_condition(self, condition):
        """
        Evaluates a condition expression.
        """
        try:
            return eval(condition, {}, self.context)
        except Exception as e:
            print(f"Error evaluating condition '{condition}': {e}")
            return False

    def preprocess_workflow(self):
        """
        Replaces placeholders in the workflow with actual values from the initial context.
        Raises a KeyError if a placeholder is missing in the initial context.
        """
        def replace_placeholders(obj):
            if isinstance(obj, dict):
                return {k: replace_placeholders(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [replace_placeholders(i) for i in obj]
            elif isinstance(obj, str):
                # Find all placeholders in the format $initial_context.key
                matches = re.findall(
                    r'\$initial_context\.([a-zA-Z_][a-zA-Z0-9_]*)', obj)
                for match in matches:
                    if match in self.context:
                        # Replace the placeholder with the actual value from the context
                        obj = obj.replace(
                            f'$initial_context.{match}', str(self.context[match]))
                    else:
                        # Raise an error if the placeholder is missing in the initial context
                        raise KeyError(
                            f"Placeholder '{match}' is missing in the initial context.")
                return obj
            else:
                return obj

        self.workflow = replace_placeholders(self.workflow)

    def validate_workflow(self):
        """
        Validates the workflow against the provided schema.
        Raises a validation error if the workflow is invalid.
        """
        try:
            self.validator.validate(self.workflow)
            print("Workflow validation successful.")
        except jsonschema.exceptions.ValidationError as e:
            print(f"Workflow validation failed: {e.message}")
            raise
