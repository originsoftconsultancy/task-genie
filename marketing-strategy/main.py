import json
from engine.workflow_executor import WorkflowExecutor
from flask import Flask, request, Response
from flask_cors import CORS
from tools.lead_search import fetch_leads, insert_leads
from tools.email_client import send_email
from tools.data_storage import insert_data
import time

app = Flask(__name__)
CORS(app)


@app.route('/process_prompt', methods=['POST'])
def process_prompt():
    user_inputs = request.json
    if 'prompt' not in user_inputs:
        return Response("No prompt provided", status=400)

    def generate_test():

        with open("assets/workflows/simple_message_broadcast_001.json", "r") as workflow_file:
            workflow = json.load(workflow_file)

        executor = WorkflowExecutor(workflow, initial_context=user_inputs)
        for item in executor.execute():
            if isinstance(item, bytes):
                yield item
            elif isinstance(item, str):
                # Convert string to JSON message format and encode as bytes
                message = {"message": {"content": item}}
                yield (json.dumps(message) + '\n').encode('utf-8')
            else:
                # For any other type, convert to string representation
                message = {"message": {"content": str(item)}}
                yield (json.dumps(message) + '\n').encode('utf-8')

    return Response(generate_test(), content_type='application/x-ndjson')


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
