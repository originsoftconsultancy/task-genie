import json
from tools.lead_search import fetch_leads, insert_leads
from tools.email_client import send_email
from tools.data_storage import insert_data

# Example usage
if __name__ == "__main__":

    with open("assets/workflows/simple_message_broadcast_001.json", "r") as workflow_file:
        workflow = json.load(workflow_file)

    executor = WorkflowExecutor(workflow)
    executor.execute()
