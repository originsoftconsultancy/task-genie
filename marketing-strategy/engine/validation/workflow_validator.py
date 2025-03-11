import json
import jsonschema
from jsonschema import validate


class WorkflowValidator:
    def __init__(self, schema_path: str = 'assets/workflow_schema.json'):
        """Initialize the validator with the schema file."""
        with open(schema_path, 'r') as f:
            self.schema = json.load(f)

    def validate(self, workflow_json: dict) -> bool:
        """Validates the workflow JSON against the schema."""
        try:
            validate(instance=workflow_json, schema=self.schema)
            print("✅ Workflow is valid!")
            return True
        except jsonschema.exceptions.ValidationError as e:
            print(f"❌ Workflow validation failed: {e.message}")
            return False
