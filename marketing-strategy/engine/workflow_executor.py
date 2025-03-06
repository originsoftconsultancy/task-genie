import json
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

    def execute(self):
        """
        Executes the workflow steps in order after validation.
        """
        self.validate_workflow()
        print("Executing workflow...")

        for step in self.workflow.get("steps", []):
            print(f"Executing step: {step.get('step')}")
            # Placeholder for step execution logic

        print("Workflow execution completed.")


# Example usage
if __name__ == "__main__":

    with open("assets/workflows/simple_message_broadcast_001.json", "r") as workflow_file:
        workflow = json.load(workflow_file)

    executor = WorkflowExecutor(workflow)
    executor.execute()
