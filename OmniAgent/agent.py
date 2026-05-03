import requests
import json
import time
from collections import defaultdict
import logging


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# @dataclass
# class AgentConfig:
#     code_exec_docker_enabled: bool = True
#     code_exec_docker_name: str = "omni-agent-exe"
#     code_exec_docker_image: str = "joaquino/omni-agent-exe:latest"
#     code_exec_docker_ports: dict[str,int] = field(default_factory=lambda: {"22/tcp": 50022})
#     code_exec_docker_volumes: dict[str, dict[str, str]] = field(default_factory=lambda: {files.get_abs_path("work_dir"): {"bind": "/root", "mode": "rw"}})
#     code_exec_ssh_enabled: bool = True
#     code_exec_ssh_addr: str = "localhost"
#     code_exec_ssh_port: int = 50022
#     code_exec_ssh_user: str = "root"
#     code_exec_ssh_pass: str = "toor"
#     additional: Dict[str, Any] = field(default_factory=dict)

class Agent:
    def __init__(self, role, model, url="http://localhost:11434/api/chat", context=None):
        self.model = model
        self.url = url
        self.context = context
        self.role = role


    def save_prompt(self, messages, file_path='llama3_prompts.json'):
        """
        Save the prompt to a JSON file for debugging purposes.
        """
        try:
            with open(file_path, 'r+') as f:
                try:
                    prompts = json.load(f)
                except json.JSONDecodeError:
                    prompts = []

                prompts.append({
                    'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
                    'messages': messages
                })

                f.seek(0)
                json.dump(prompts, f, indent=2)
                f.truncate()
        except FileNotFoundError:
            with open(file_path, 'w') as f:
                json.dump([{
                    'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
                    'messages': messages
                }], f, indent=2)

    def llama3(self, messages):
        """
        Send the messages to Llama3 and return the response.
        """
        data = {
            "model": "llama3",
            "messages": messages,
            "stream": False
        }

        headers = {
            'Content-Type': 'application/json'
        }

        # Save the prompt before sending it to Llama3
        self.save_prompt(messages)

        response = requests.post(self.llama3_url, headers=headers, json=data)
        response_json = response.json()
        return response_json.get('message', {}).get('content', '')

    def get_response(self, message):
        response = self.llama3([{
            "role": "user",
            "content": message
        }])
    
        return response