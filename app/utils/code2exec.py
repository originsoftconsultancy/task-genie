import re
import os
import subprocess
import shutil
import uuid
import sys


class CodeExecutor:
    def __init__(self):
        self.code = ""
        self.requirements = ""
        self.env_vars = ""
        self.execution_id = ""

    def execute(self, llm_response):

        self.code, self.requirements, self.env_vars = self._extract_function_and_requirements(
            llm_response)

        print(f"Code: {self.code}")
        print(f"Requirements: {self.requirements}")
        print(f"Environment variables: {self.env_vars}")
        return self._execute_user_code(
            self.code, self.requirements, self.env_vars)

    def _execute_user_code(self, user_code, requirements, env_vars, venv_path=".venv_exec"):

        result = None

        try:
            # Step 1: Ensure the virtual environment exists
            if not os.path.exists(venv_path):
                print("Creating virtual environment...")
                subprocess.check_call(
                    [sys.executable, "-m", "venv", venv_path])

            # Step 2: Create a temporary directory for user code execution
            self.execution_id = uuid.uuid4().hex
            exec_folder = f"user_code_exec_{self.execution_id}"
            os.makedirs(exec_folder, exist_ok=True)
            # print(f"Created temporary execution folder: {exec_folder}")

            # Step 3: Write the user code to a Python script in the execution folder
            script_path = os.path.join(exec_folder, "user_script.py")
            with open(script_path, "w") as script_file:
                script_file.write(user_code)
            # print(f"User code written to: {script_path}")

            # Step 4: Activate the virtual environment and install user requirements
            pip_path = os.path.join(venv_path, "bin", "pip") if os.name != "nt" else os.path.join(
                venv_path, "Scripts", "pip")
            # print("Installing dependencies...")
            for lib in requirements:
                try:
                    subprocess.check_call([pip_path, "install", lib])
                except:
                    pass
            # print("Dependencies installed successfully")

            # Step 5: Set environment variables
            for env_var in env_vars:
                try:
                    key, value = env_var.split("=")
                    os.environ[key] = value
                except:
                    pass
            # print("Environment variables set")

            # Step 6: Run the user script in the virtual environment
            python_path = os.path.join(venv_path, "bin", "python") if os.name != "nt" else os.path.join(
                venv_path, "Scripts", "python")
            # print(f"Executing user script: {script_path}")
            result = subprocess.run(
                [python_path, script_path], capture_output=True, text=True)

        except subprocess.CalledProcessError as e:
            print(f"An error occurred: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")
        finally:
            # Clean up the execution folder
            if os.path.exists(exec_folder):
                shutil.rmtree(exec_folder)
                print(f"Cleaned up temporary execution folder: {exec_folder}")

            # Check if the script ran successfully
            if result.returncode == 0:
                return result.stdout
            else:
                return f"""
                Script execution failed
                Error Output:
                {result.stderr}
                """

    def _extract_function_and_requirements(self, text):

        # Regex patterns for Python code and requirements
        code_pattern = r"```python(.*?)```"
        requirements_pattern = r"```requirements(.*?)```"
        env_vars_pattern = r"```env_vars(.*?)```"

        # Extract the first occurrence of each
        code = re.search(code_pattern, text, re.DOTALL)
        requirements = re.search(requirements_pattern, text, re.DOTALL)
        env_vars = re.search(env_vars_pattern, text, re.DOTALL)

        # Get the matched strings or set as empty if not found
        code = code.group(1).strip() if code else ""
        requirements = requirements.group(1).strip() if requirements else ""
        env_vars = env_vars.group(1).strip() if env_vars else ""

        # Split requirements and environment variables into lists

        try:
            requirements = requirements.split("\n") if requirements else []
        except:
            requirements = []

        try:
            env_vars = dict([line.split("=")
                             for line in env_vars.split("\n") if line])
        except:
            env_vars = []

        return code, requirements, env_vars
