
import sys

sys.stdout.reconfigure(encoding="utf-8")

from agent import StudyPlannerAgent


def print_trace(agent: StudyPlannerAgent):
    print("\n--- MULTI-STEP TRACE ---")
    for item in agent.trace:
        print(item)


if __name__ == "__main__":
    agent = StudyPlannerAgent()

    print("T24 Study Planner Agent")
    print("Type 'exit' to stop.\n")

    while True:
        goal = input("You: ").strip()
        if goal.lower() == "exit":
            break

        try:
            answer = agent.run(goal)
            print(f"Agent: {answer}")
            print_trace(agent)
        except Exception as exc:
            print(f"Error: {exc}")
