import json
from engine.workflow_executor import WorkflowExecutor
from tools.lead_search import fetch_leads, insert_leads
from tools.email_client import send_email
from tools.data_storage import insert_data

# Example usage
if __name__ == "__main__":

    # User-provided inputs
    user_inputs = {
        "prompt": "I want to send a message to doctors about our services for HIPAA compliance dashboards that can help them focus more on their medical services instead of compliance requirements. Our website landing page is https://abc-compliance.com."
    }

    with open("assets/workflows/simple_message_broadcast_001.json", "r") as workflow_file:
        workflow = json.load(workflow_file)

    executor = WorkflowExecutor(workflow, initial_context=user_inputs)
    executor.execute()
