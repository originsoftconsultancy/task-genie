import requests
import jsonschema
from jsonschema import validate
from validation.workflow_validator import WorkflowValidator


class WorkflowExecutor:
    def __init__(self, workflow: dict):
        """
        Initializes the WorkflowExecutor with a workflow and schema.
        """
        self.workflow = workflow
        self.validator = WorkflowValidator()

    def execute(self):
        """
        Executes the workflow steps in order after validation.
        """
        self.validate_workflow()
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
        prompt = step["parameters"].get("prompt")
        inputs = {key: self.context.get(
            key) for key in step["parameters"].get("input_keys", [])}
        print(
            f"Generating LLM response for prompt: '{prompt}' with inputs: {inputs}")
        # Placeholder for actual LLM call
        llm_response = "LLM response"  # Replace with actual LLM response
        for key in step["parameters"].get("output_keys", []):
            self.context[key] = llm_response

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
