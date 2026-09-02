
from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class AgentMemory:
    """Session memory: tasks plus recent conversation turns."""

    tasks: Dict[str, Dict[str, str]] = field(default_factory=dict)
    conversation: List[Dict[str, str]] = field(default_factory=list)

    def remember_task(self, name: str, due: str) -> None:
        self.tasks[name.strip().lower()] = {
            "name": name.strip(),
            "due": due,
        }

    def get_tasks(self) -> List[Dict[str, str]]:
        return list(self.tasks.values())

    def add_message(self, role: str, content: str) -> None:
        self.conversation.append({"role": role, "content": content})

    def recent_messages(self, limit: int = 10) -> List[Dict[str, str]]:
        return self.conversation[-limit:]

    def snapshot(self) -> Dict[str, Any]:
        return {
            "tasks": self.get_tasks(),
            "conversation_turns": len(self.conversation),
        }
