
from datetime import date, datetime
from typing import Any, Dict


def _parse_due(due: str) -> date:
    """Validate the official YYYY-MM-DD due-date format."""
    try:
        return datetime.strptime(due, "%Y-%m-%d").date()
    except ValueError as exc:
        raise ValueError(
            f"Invalid due date '{due}'. Use YYYY-MM-DD, for example 2026-09-15."
        ) from exc


class StudyPlannerTools:
    """The two official T24 tools."""

    def __init__(self, memory):
        self.memory = memory

    def add_task(self, name: str, due: str) -> Dict[str, Any]:
        due_date = _parse_due(due)
        clean_name = name.strip()
        if not clean_name:
            raise ValueError("Task name cannot be empty.")

        self.memory.remember_task(clean_name, due_date.isoformat())
        return {
            "status": "added",
            "task": clean_name,
            "due": due_date.isoformat(),
        }

    def build_schedule(self) -> Dict[str, Any]:
        """Build a priority-first study schedule from remembered deadlines."""
        today = date.today()
        tasks = []

        for item in self.memory.get_tasks():
            due_date = _parse_due(item["due"])
            days_left = (due_date - today).days

            if days_left < 0:
                priority = "OVERDUE"
            elif days_left <= 2:
                priority = "CRITICAL"
            elif days_left <= 7:
                priority = "HIGH"
            else:
                priority = "NORMAL"

            tasks.append(
                {
                    "name": item["name"],
                    "due": item["due"],
                    "days_left": days_left,
                    "priority": priority,
                }
            )

        # Earliest deadline first; overdue tasks naturally appear first.
        tasks.sort(key=lambda x: (x["days_left"], x["name"].lower()))

        return {
            "status": "schedule_built",
            "today": today.isoformat(),
            "tasks": tasks,
            "recommendation": tasks[0]["name"] if tasks else None,
        }
