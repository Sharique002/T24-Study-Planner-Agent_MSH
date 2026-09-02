# T24 — Study Planner Agent

## 1. Project goal
This project implements the official  T24 topic, **Study Planner Agent**. The agent helps a student plan study blocks around real deadlines. It is built as a real agent with an LLM-driven plan-act loop, two callable tools, and session memory. The agent can add tasks, build a priority-first schedule, and use information from earlier turns when deciding what the student should study first.

## 2. Tools and memory
The two official tools are `add_task(name, due)` and `build_schedule()`. `add_task` validates and stores each task in session memory. `build_schedule` reads the remembered tasks, calculates days remaining, assigns urgency, sorts deadlines, and returns the recommended next task. Session memory also stores recent conversation turns, so a later request such as “what should I work on first?” can use deadlines from earlier turns rather than starting from zero.

## 3. Honest development failure and handling
During development, an invalid date such as `2026-02-30` caused Python date parsing to fail. Instead of allowing that exception to crash the agent, the tool now validates the date and returns a clear error path to the agent. The project includes a test for this failure. This makes the tool boundary predictable and keeps invalid user input from corrupting memory.

## Run
1. Install Python 3.10+.
2. Run `pip install -r requirements.txt`.
3. Copy `.env.example` to `.env`.
4. Add your GitHub Models token to `GITHUB_TOKEN`.
5. Run `python main.py`.
6. For the assessed demonstration, open `T24_Agent_Demo.ipynb` and **Run All**.

## Assessment mapping
- **Implementation (10):** `agent.py` contains the plan-act loop; `tools.py` contains the two working tools; `memory.py` provides session memory.
- **Presentation (10):** `T24_Agent_Demo.ipynb` demonstrates 3 goals and prints the tool-call/tool-result trace.
- **Viva (10):** the code is intentionally small enough to explain: model decides -> tool executes -> result returns -> model decides again; memory is written and read across turns.

## Important
Do not commit `.env` or a real API token. `.env.example` is safe to submit.
