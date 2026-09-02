
import json
import os
from typing import Any, Dict, List

from dotenv import load_dotenv
from openai import OpenAI

from memory import AgentMemory
from tools import StudyPlannerTools

load_dotenv()


SYSTEM_PROMPT = """You are a Study Planner Agent for a student.

You are an AGENT, not a simple chatbot. You must act on study-planning goals by
using tools and by deciding what to do next from tool results.

Official tools:
1. add_task(name, due) - stores a study task in session memory.
2. build_schedule() - reads all remembered tasks and builds a priority-first schedule.

Rules:
- If the user gives a task and due date, call add_task.
- If the user gives multiple tasks, call add_task for each task.
- After adding tasks, if the user's goal is to plan, prioritize, schedule, or decide
  what to study first, call build_schedule.
- If the user asks what is urgent, what to study first, or asks about deadlines,
  call build_schedule even if the tasks were added in an earlier turn.
- Use the returned tool data to make the decision. Do not invent deadlines.
- Remember earlier turns. If the user says "the task I added earlier", use memory
  and/or build_schedule to recover it.
- If a tool returns an error, explain it and ask for corrected input.
- Never claim a tool was called when it was not.
- Keep the final answer concise but state the action/decision you made.
"""


class StudyPlannerAgent:
    def __init__(self, model: str | None = None):
        token = os.getenv("GITHUB_TOKEN") or os.getenv("OPENAI_API_KEY")
        if not token:
            raise RuntimeError(
                "API token missing. Put GITHUB_TOKEN (recommended) or OPENAI_API_KEY in .env."
            )

        endpoint = os.getenv(
            "GITHUB_MODELS_ENDPOINT",
            "https://models.github.ai/inference",
        )
        self.model = model or os.getenv("MODEL", "openai/gpt-4.1-mini")
        self.client = OpenAI(base_url=endpoint, api_key=token)
        self.memory = AgentMemory()
        self.tools = StudyPlannerTools(self.memory)
        self.trace: List[Dict[str, Any]] = []

    def _tool_schemas(self):
        return [
            {
                "type": "function",
                "function": {
                    "name": "add_task",
                    "description": "Add a study task and its deadline to session memory.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "due": {
                                "type": "string",
                                "description": "Due date in YYYY-MM-DD format",
                            },
                        },
                        "required": ["name", "due"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "build_schedule",
                    "description": "Build a priority-first schedule from all remembered tasks.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": [],
                    },
                },
            },
        ]

    def _call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        if name == "add_task":
            return self.tools.add_task(**arguments)
        if name == "build_schedule":
            return self.tools.build_schedule()
        return {"status": "error", "message": f"Unknown tool: {name}"}

    def run(self, user_goal: str) -> str:
        self.trace = []
        self.memory.add_message("user", user_goal)

        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        messages.extend(self.memory.recent_messages())

        # PLAN-ACT LOOP:
        # 1) Ask the model what action/tool is needed.
        # 2) Execute the selected tool.
        # 3) Feed the result back to the model.
        # 4) Let the model decide the next step.
        for step in range(1, 7):
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=self._tool_schemas(),
                tool_choice="auto",
                temperature=0.2,
            )

            msg = response.choices[0].message
            assistant_message: Dict[str, Any] = {
                "role": "assistant",
                "content": msg.content or "",
            }

            if msg.tool_calls:
                assistant_message["tool_calls"] = []
                for call in msg.tool_calls:
                    assistant_message["tool_calls"].append(
                        {
                            "id": call.id,
                            "type": "function",
                            "function": {
                                "name": call.function.name,
                                "arguments": call.function.arguments,
                            },
                        }
                    )

            messages.append(assistant_message)

            if not msg.tool_calls:
                answer = msg.content or "I completed the request."
                self.memory.add_message("assistant", answer)
                self.trace.append(
                    {"step": step, "type": "final", "message": answer}
                )
                return answer

            for call in msg.tool_calls:
                name = call.function.name
                try:
                    args = json.loads(call.function.arguments or "{}")
                except json.JSONDecodeError:
                    args = {}
                    result = {
                        "status": "error",
                        "message": "The model produced invalid tool arguments.",
                    }
                else:
                    self.trace.append(
                        {
                            "step": step,
                            "type": "tool_call",
                            "tool": name,
                            "arguments": args,
                        }
                    )
                    try:
                        result = self._call_tool(name, args)
                    except Exception as exc:
                        result = {"status": "error", "message": str(exc)}

                self.trace.append(
                    {
                        "step": step,
                        "type": "tool_result",
                        "tool": name,
                        "result": result,
                    }
                )

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": call.id,
                        "content": json.dumps(result),
                    }
                )

        answer = "I could not complete the task within the six-step limit."
        self.memory.add_message("assistant", answer)
        self.trace.append({"step": 6, "type": "final", "message": answer})
        return answer
