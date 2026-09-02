# T24 Study Planner Agent — Project Documentation

## 1. Problem statement
Students often have several assignments and exams with different deadlines. A useful assistant should not merely generate study advice: it should remember tasks, inspect deadline data, and decide what action is most appropriate.

This project implements the official CSE476 T24 Study Planner Agent. The agent stores study tasks, calculates urgency, builds a schedule, and recommends what to work on first.

## 2. Architecture

```text
User Goal
   |
   v
LLM Agent (agent.py)
   |
   | decides next action
   v
+--------------------------+
| Plan -> Act -> Observe   |
+--------------------------+
   |                 |
   | tool call       | tool result
   v                 |
+--------------------------+
| Tool Layer (tools.py)   |
| 1. add_task             |
| 2. build_schedule       |
+--------------------------+
   |
   v
Session Memory (memory.py)
   |
   +--> tasks
   +--> conversation history
   |
   +--> result returned to LLM
             |
             v
       next decision / final answer
```

## 3. Why this is an agent, not a chatbot
A chatbot can answer a prompt directly. This project demonstrates agency in three ways required by the brief:

1. **Tool use:** the model calls real Python functions rather than only producing text.
2. **Multi-step decision making:** after a tool result is returned, the model can decide whether another tool call is needed. For example, after adding several tasks, it can call `build_schedule` to make a decision.
3. **Memory:** tasks and conversation turns persist inside the `StudyPlannerAgent` object. A later user turn can ask what is urgent without re-entering the earlier deadlines.

## 4. Tool design

### Tool 1 — add_task(name, due)
Purpose: store a study task.

Input:
- `name`: task/assignment name
- `due`: `YYYY-MM-DD`

Behavior:
- validates the date
- rejects an empty name
- writes the task to memory
- returns a structured result

### Tool 2 — build_schedule()
Purpose: turn remembered deadlines into a priority decision.

Behavior:
- reads all tasks from memory
- calculates days remaining from today's date
- labels tasks OVERDUE / CRITICAL / HIGH / NORMAL
- sorts by urgency
- returns the recommended first task

The tool result is observable by the model, so the final recommendation is based on actual stored data.

## 5. Memory design
Memory is session-scoped. It contains:
- `tasks`: a dictionary keyed by normalized task name
- `conversation`: recent user/assistant messages

This is enough for the assignment requirement: memory must remember earlier turns in the same conversation and be used later.

## 6. Demonstration plan
The notebook demonstrates three goals:

**Goal 1 — Add first tasks**
- Add CSE476 Agentic AI project
- Add DBMS assignment
- Build a schedule
- Show tool calls and tool results

**Goal 2 — Add another deadline**
- Add AI viva
- Build a new schedule
- Show that the previous tasks remain in memory

**Goal 3 — Memory test**
- Ask: “Which task should I work on first?”
- Do not repeat the deadlines
- Agent calls `build_schedule`
- Agent chooses from remembered tasks

A fourth small cell demonstrates the invalid-date failure and shows the clear validation message.

## 7. Viva: questions you should be able to answer

**Q1. Where is the plan-act loop?**  
`agent.py`, inside `StudyPlannerAgent.run()`. The loop calls the model, executes requested tools, sends tool results back, and lets the model decide the next step.

**Q2. What makes it multi-step?**  
A single user goal can cause multiple tool actions. For example, multiple `add_task` calls can be followed by `build_schedule`. The second decision is made after observing tool results.

**Q3. What are your two tools?**  
`add_task(name, due)` and `build_schedule()`.

**Q4. Where is memory?**  
`memory.py`, inside `AgentMemory`. The agent stores tasks and recent conversation turns.

**Q5. How is memory used later?**  
The same `StudyPlannerAgent` instance is reused across notebook goals. A later urgency question can call `build_schedule()`, which reads tasks stored during previous turns.

**Q6. Why do you need tools if the LLM can calculate?**  
Tools make the action and state explicit. The deadline data is stored and calculated by deterministic Python code, while the LLM decides when the tools are needed and how to communicate the result.

**Q7. What happens with an invalid date?**  
`_parse_due()` catches the date error and raises a clear `ValueError`. The agent records the tool failure in its trace instead of silently accepting bad data.

**Q8. What would you improve next?**  
Add persistent storage, calendar integration, study-duration estimation, conflict-aware time blocks, and a web UI. Those are extensions; the submitted core intentionally follows the official two-tool T24 scope.

## 8. Academic honesty note
The project is designed to be understandable during viva. The student should run the notebook, inspect the trace, and be able to explain every file and decision path before submission.
