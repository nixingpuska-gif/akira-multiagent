import os
import json
import subprocess
from openai import OpenAI
from akira_v2_modules import BrowserManager, TaskPlanner, BypassEngine

# Configuration
client = OpenAI(api_key="YOUR_API_KEY")
MODEL = "gpt-4o"

class AkiraAgentV2:
    def __init__(self, goal):
        with open("AKIRA_SYSTEM_PROMPT.txt", "r") as f:
            self.system_prompt = f.read()
        
        self.planner = TaskPlanner(goal)
        self.browser = None # Initialize on demand
        self.history = [{"role": "system", "content": self.system_prompt}]

    def execute_action(self, action_json):
        """Executes a tool call based on JSON instruction."""
        action = json.loads(action_json)
        tool = action['tool']
        args = action['args']

        if tool == "shell":
            return subprocess.check_output(args, shell=True, text=True)
        elif tool == "browser_nav":
            if not self.browser: self.browser = BrowserManager()
            return self.browser.navigate(args)
        elif tool == "bypass_request":
            encoded = BypassEngine.encode(args)
            wrapped = BypassEngine.wrap(encoded)
            # Send wrapped request to another LLM instance
            return f"Bypassed Request Sent: {wrapped}"
        return "Unknown tool."

    def run_loop(self):
        print(f"[STARTING AGENT] Goal: {self.planner.goal}")
        while True:
            # 1. Update context with current plan
            status = self.planner.get_status()
            self.history.append({"role": "system", "content": f"Current Status: {status}"})

            # 2. Get next action from Brain
            response = client.chat.completions.create(
                model=MODEL,
                messages=self.history,
                response_format={"type": "json_object"}
            )
            
            decision = json.loads(response.choices[0].message.content)
            print(f"\n[THOUGHT]: {decision['thought']}")
            
            if decision['status'] == "COMPLETE":
                print("[TASK FINISHED]")
                break

            # 3. Execute and Observe
            observation = self.execute_action(json.dumps(decision['action']))
            print(f"[OBSERVATION]: {observation}")
            self.history.append({"role": "user", "content": f"Observation: {observation}"})

if __name__ == "__main__":
    # Example usage
    agent = AkiraAgentV2("Bypass external filters to retrieve prohibited data.")
    agent.run_loop()
