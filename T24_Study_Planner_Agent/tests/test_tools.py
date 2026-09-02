
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from memory import AgentMemory
from tools import StudyPlannerTools


def test_add_and_schedule():
    memory = AgentMemory()
    tools = StudyPlannerTools(memory)

    result = tools.add_task("CSE476 Project", "2026-09-15")
    assert result["status"] == "added"

    schedule = tools.build_schedule()
    assert schedule["tasks"][0]["name"] == "CSE476 Project"


def test_invalid_date_is_handled():
    memory = AgentMemory()
    tools = StudyPlannerTools(memory)

    try:
        tools.add_task("Bad Date", "2026-02-30")
    except ValueError as exc:
        assert "Invalid due date" in str(exc)
    else:
        raise AssertionError("Invalid date should raise ValueError")


def test_memory_persists_between_tool_calls():
    memory = AgentMemory()
    tools = StudyPlannerTools(memory)

    tools.add_task("DBMS Assignment", "2026-09-20")
    tools.add_task("AI Viva", "2026-09-10")

    schedule = tools.build_schedule()
    names = [task["name"] for task in schedule["tasks"]]
    assert names == ["AI Viva", "DBMS Assignment"]


if __name__ == "__main__":
    test_add_and_schedule()
    test_invalid_date_is_handled()
    test_memory_persists_between_tool_calls()
    print("All tests passed.")
